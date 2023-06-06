import asyncio
import glob
import os
import select
import time
from concurrent.futures import (
    FIRST_COMPLETED,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    wait,
)
from random import randint
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

T = TypeVar("T")
U = TypeVar("U")


def log_and_continue(exception: Exception):
    print(repr(exception))


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class Pipe:
    functions: Dict[str, Callable] = {}

    def __init__(self, *items):
        if len(items) == 1 and is_iterable(items[0]):
            items = items[0]
        self.items = iter(items)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.items)

    def __getattr__(self, name):
        def method(*args, **kwargs):
            return self.functions[name](*args, **kwargs)(self.items)

        return method

    def __call__(self):
        # Exhaust iterator
        for _ in self:
            pass

    @classmethod
    def add(cls, fn: Callable, name: Optional[str] = None) -> Callable:
        def fn_curried(*args, **kwargs):
            def _fn(items: Optional[Iterable[T]] = None):
                return cls(fn(items, *args, **kwargs))

            return _fn

        name = fn.__name__[1:] if name is None else name
        cls.functions[name] = fn_curried
        return fn_curried


def _map(
    items: Iterable[T],
    fn: Callable[[T], U],
    num_workers: int = 0,
    buffer: Optional[int] = None,
    mode: str = "multithread",
    handler: Callable = log_and_continue,
) -> Iterator[U]:
    assert mode in ["multithread", "multiprocess"]

    if num_workers == 0:
        for item in items:
            try:
                yield fn(item)
            except Exception as e:
                handler(e)
        return

    executors = dict(multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor)

    with executors[mode](max_workers=num_workers) as executor:
        futures = set()
        buffer = buffer or num_workers
        for item in items:
            # Fill up workers
            futures.add(executor.submit(fn, item))
            # If all busy, wait one to finish, then yield done and override remaining
            if len(futures) == buffer:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    try:
                        yield future.result()
                    except Exception as e:
                        handler(e)
        # Yield remaining results
        for future in futures:
            try:
                yield future.result()
            except Exception as e:
                handler(e)


map = Pipe.add(_map)


def _filter(
    items: Iterable[T], fn: Callable[[T], bool], *args, **kwargs
) -> Iterator[T]:
    for item, keep in _map(items, lambda x: (x, fn(x)), *args, **kwargs):
        if keep:
            yield item


filter = Pipe.add(_filter)


def _side(
    items: Iterable[T],
    fn: Callable[[T], U],
    num_workers: int = 0,
    mode: str = "multithread",
    handler: Callable = log_and_continue,
) -> Iterator[T]:
    assert mode in ["multithread", "multiprocess"]

    if num_workers == 0:
        for item in items:
            try:
                fn(item)
            except Exception as e:
                handler(e)
            yield item
        return

    executors = dict(multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor)
    with executors[mode](max_workers=num_workers) as executor:
        for item in items:
            executor.submit(fn, item)
            yield item


side = Pipe.add(_side)


def _batch(items: Iterable[T], size: int) -> Iterator[List[T]]:
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


batch = Pipe.add(_batch)


def _unbatch(items: Iterable[Sequence[T]]) -> Iterator[T]:
    for b in items:
        for item in b:
            yield item


unbatch = Pipe.add(_unbatch)


def pick(items: List[T], random: bool = False) -> T:
    idx = randint(0, len(items) - 1) if random else 0
    return items.pop(idx)


def _shuffle(items: Iterator[T], size: int, start: Optional[int] = None) -> Iterator[T]:
    start = start or size
    buffer = []
    for item in items:
        buffer.append(item)
        if len(buffer) < size:
            try:
                buffer.append(next(items))
            except StopIteration:
                pass
        if len(buffer) >= start:
            yield pick(buffer, random=True)
    # Empty buffer at the end
    while len(buffer) > 0:
        yield pick(buffer)


shuffle = Pipe.add(_shuffle)


def _limit(items: Iterable[T], limit: int = 10**100) -> Iterator[T]:
    for count, item in enumerate(items):
        if count >= limit:
            return
        yield item


limit = Pipe.add(_limit)


def _log(items: Iterable[T], fn: Callable[[T], None] = print) -> Iterator[T]:
    return _side(items, fn)


log = Pipe.add(_log)


def _tqdm(items: Iterable[T], *args, **kwargs) -> Iterator[T]:
    try:
        from tqdm import tqdm as progressbar
    except ImportError:
        raise ImportError("tqdm is required to use tqdm")
    for item in progressbar(items, *args, **kwargs):
        yield item


tqdm = Pipe.add(_tqdm)


def _sleep(items: Iterable[T], seconds: float) -> Iterator[T]:
    return _side(items, lambda _: time.sleep(seconds))


sleep = Pipe.add(_sleep)


def watchdir(
    path: str, changes: Sequence[int] = [1]  # default to watchgod.Change.added == 1
) -> Iterator[str]:
    try:
        from watchgod import awatch
    except ImportError:
        raise ImportError("watchgod is required to use watch")
    loop = asyncio.get_event_loop()
    async_generator = awatch(path)
    while True:
        for change, filepath in loop.run_until_complete(async_generator.__anext__()):
            if change in changes:
                yield filepath


def _readf(_, filepath: str, watch: bool = False) -> Iterator[str]:
    files = glob.glob(filepath)
    for file in files:
        yield file
    if watch:
        yield from watchdir(os.path.dirname(filepath))


readf = Pipe.add(_readf)


class Readf(Pipe):
    def __init__(self, *args, **kwargs):
        super().__init__(readf(*args, **kwargs)())


def _readl(_, filepath: str, watch: bool = False) -> Iterator[str]:
    with open(filepath, "r") as file:
        while True:
            line = file.readline()
            if line:
                yield line.strip()
            elif watch:
                select.select([file], [], [])  # Wait until there is more data to read
            else:
                break


readl = Pipe.add(_readl)


class Readl(Pipe):
    def __init__(self, *args, **kwargs):
        super().__init__(readl(*args, **kwargs)())


def _writel(items: Iterable[str], filepath: str) -> Iterator[str]:
    with open(filepath, "w") as f:
        for item in items:
            f.write(item + "\n")
            yield item


writel = Pipe.add(_writel)


def _filter_cached(
    items: Iterable[T],
    filepath: str,
    key: Optional[Callable] = None,
) -> Iterator[T]:
    cache = set(readl(filepath)) if os.path.exists(filepath) else set()
    with open(filepath, "a") as file:
        for item in items:
            value = key(item) if key is not None else item
            if value not in cache:
                cache.add(value)
                file.write(value + "\n")
                yield item


filter_cached = Pipe.add(_filter_cached)


def _write_csv(
    items: Iterable[Union[Dict[str, Any], Sequence[Any]]], filepath: str
) -> Iterable[Union[Dict[str, Any], Sequence[Any]]]:
    import csv

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        for i, item in enumerate(items):
            if isinstance(item, dict):
                if i == 0:  # Write headers only for the first dictionary item
                    writer.writerow(item.keys())
                item = item.values()  # type: ignore
            writer.writerow(item)
            yield item


write_csv = Pipe.add(_write_csv)


def _read_csv(
    _, filepath: str, header: Union[bool, Sequence[str]] = False
) -> Iterable[Union[Dict[str, str], List[str]]]:
    import csv

    with open(filepath, "r") as f:
        if header:
            fieldnames = header if isinstance(header, Sequence) else None
            yield from csv.DictReader(f, fieldnames=fieldnames)
        else:
            yield from csv.reader(f)


read_csv = Pipe.add(_read_csv)


class ReadCSV(Pipe):
    def __init__(self, *args, **kwargs):
        super().__init__(read_csv(*args, **kwargs)())

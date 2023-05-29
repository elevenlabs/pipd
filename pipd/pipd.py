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
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Sequence, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def log_and_continue(exception: Exception):
    print(repr(exception))


class Pipe:
    functions: Dict[str, Callable] = {}

    def __init__(self, *items):
        if len(items) == 1 and isinstance(items[0], Iterable):
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
    def add_function(cls, name: str, function: Callable):
        cls.functions[name] = function


def as_pipe(fn: Callable, name: Optional[str] = None) -> Callable:
    def fn_curried(*args, **kwargs):
        def _fn(items: Optional[Iterable[T]] = None):
            return Pipe(fn(items, *args, **kwargs))

        return _fn

    Pipe.add_function(
        # If name is None we assume the function is named _name and remove the _
        name=fn.__name__[1:] if name is None else name,
        function=fn_curried,
    )
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


map = as_pipe(_map)


def _filter(
    items: Iterable[T], fn: Callable[[T], bool], *args, **kwargs
) -> Iterator[T]:
    for item, keep in _map(items, lambda x: (x, fn(x)), *args, **kwargs):
        if keep:
            yield item


filter = as_pipe(_filter)


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


side = as_pipe(_side)


def _batch(items: Iterable[T], size: int) -> Iterator[List[T]]:
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


batch = as_pipe(_batch)


def _unbatch(items: Iterable[Sequence[T]]) -> Iterator[T]:
    for b in items:
        for item in b:
            yield item


unbatch = as_pipe(_unbatch)


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


shuffle = as_pipe(_shuffle)


def _limit(items: Iterable[T], limit: int = 10**100) -> Iterator[T]:
    for count, item in enumerate(items):
        if count < limit:
            yield item


limit = as_pipe(_limit)


def _log(items: Iterable[T], fn: Callable[[T], None] = print) -> Iterator[T]:
    return _side(items, fn)


log = as_pipe(_log)


def _tqdm(items: Iterable[T], *args, **kwargs) -> Iterator[T]:
    try:
        from tqdm import tqdm as progressbar
    except ImportError:
        raise ImportError("tqdm is required to use tqdm")
    for item in progressbar(items, *args, **kwargs):
        yield item


tqdm = as_pipe(_tqdm)


def _sleep(items: Iterable[T], seconds: float) -> Iterator[T]:
    return _side(items, lambda _: time.sleep(seconds))


sleep = as_pipe(_sleep)


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


readf = as_pipe(_readf)


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


readl = as_pipe(_readl)


class Readl(Pipe):
    def __init__(self, *args, **kwargs):
        super().__init__(readl(*args, **kwargs)())


def _writel(items: Iterable[str], filepath: str) -> Iterator[str]:
    with open(filepath, "w") as f:
        for item in items:
            f.write(item + "\n")
            yield item


writel = as_pipe(_writel)


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


filter_cached = as_pipe(_filter_cached)

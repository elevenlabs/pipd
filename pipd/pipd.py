import asyncio
import glob
import os
import select
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from random import randint
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def log_and_continue(exception: Exception):
    print(repr(exception))


def with_handler(fn: Callable, handler: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            handler(e)

    return wrapper


def curry(fn: Callable) -> Callable:
    # fn(a0, a1, a2) => curry(fn)(a1, a2)(a0)
    def fn_curried(*args, **kwargs):
        def _fn(arg0):
            return fn(arg0, *args, **kwargs)

        return _fn

    return fn_curried


def _pipe(items: Iterable[T], *fns: Callable) -> Iterable[U]:
    for fn in fns:
        items = fn(items)
    return items  # type: ignore


pipe = curry(_pipe)


def _batch(items: Iterable[T], size: int) -> Iterator[List[T]]:
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


batch = curry(_batch)


def _unbatch(items: Iterable[Sequence[T]]) -> Iterator[T]:
    for b in items:
        for item in b:
            yield item


unbatch = curry(_unbatch)


def pick(items: List[T], random: bool = False) -> T:
    idx = randint(0, len(items) - 1) if random else 0
    return items.pop(idx)


def _buffer(
    items: Iterator[T], size: int, start: int = 0, shuffle: bool = False
) -> Iterator[T]:
    buffer = []
    for item in items:
        buffer.append(item)
        if len(buffer) < size:
            try:
                buffer.append(next(items))
            except StopIteration:
                pass
        if len(buffer) >= start:
            yield pick(buffer, random=shuffle)
    # Empty buffer at the end
    while len(buffer) > 0:
        yield pick(buffer)


buffer = curry(_buffer)


def _map(
    items: Iterable[T],
    fn: Callable[[T], U],
    mode: Optional[str] = None,
    num_workers: Optional[int] = None,
    batch_size: Optional[int] = None,
    handler: Callable = log_and_continue,
) -> Iterator[U]:
    assert mode in [None, "multithread", "multiprocess"]

    if mode is None:
        yield from (with_handler(fn, handler)(item) for item in items)
        return

    executors = dict(multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor)

    num_workers = num_workers or os.cpu_count()
    batch_size = batch_size or num_workers

    with executors[mode](max_workers=num_workers) as executor:
        for items_batch in batch(batch_size)(items):  # type: ignore
            fs = {executor.submit(fn, item) for item in items_batch}
            yield from (with_handler(f.result, handler)() for f in as_completed(fs))


def _filter(items: Iterable[T], fn: Callable[[T], bool]) -> Iterator[T]:
    for item in items:
        if fn(item):
            yield item


filter = curry(_filter)


def _limit(items: Iterable[T], limit: int = 10**100) -> Iterator[T]:
    for count, item in enumerate(items):
        if count < limit:
            yield item


limit = curry(_limit)


def _log(items: Iterable[T], limit: int = 10**100) -> Iterator[T]:
    for count, item in enumerate(items):
        if count < limit:
            print(item)
        yield item


log = curry(_log)


def _tqdm(items: Iterable[T], *args, **kwargs) -> Iterator[T]:
    try:
        from tqdm import tqdm as progressbar
    except ImportError:
        raise ImportError("tqdm is required to use tqdm")
    for item in progressbar(items, *args, **kwargs):
        yield item


tqdm = curry(_tqdm)


def _sleep(items: Iterable[T], seconds: float) -> Iterator[T]:
    for item in items:
        time.sleep(seconds)
        yield item


sleep = curry(_sleep)


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


def readf(filepath: str, watch: bool = False) -> Iterator[str]:
    files = glob.glob(filepath)
    for file in files:
        yield file
    if watch:
        yield from watchdir(os.path.dirname(filepath))


def readl(filename: str, watch: bool = False) -> Iterator[str]:
    with open(filename, "r") as file:
        while True:
            line = file.readline()
            if line:
                yield line.strip()
            elif watch:
                select.select([file], [], [])  # Wait until there is more data to read
            else:
                break


def _writel(items: Iterable[str], filename: str) -> None:
    with open(filename, "w") as f:
        for item in items:
            f.write(item + "\n")


writel = curry(_writel)


def run(items: Iterable[T]) -> None:
    for item in items:
        pass

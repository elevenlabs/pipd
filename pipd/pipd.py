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
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def log_and_continue(exception: Exception):
    print(repr(exception))


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


map = curry(_map)


def _filter(items: Iterable[T], fn: Callable[[T], bool]) -> Iterator[T]:
    for item in items:
        if fn(item):
            yield item


filter = curry(_filter)


def _unpipe(
    items: Iterable[T],
    fn: Callable[[T], U],
    num_workers: int = 1,
    mode: str = "multithread",
) -> Iterator[T]:
    assert mode in ["multithread", "multiprocess"]
    executors = dict(multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor)
    with executors[mode](max_workers=num_workers) as executor:
        for item in items:
            executor.submit(fn, item)
            yield item


unpipe = curry(_unpipe)


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


def readl(filepath: str, watch: bool = False) -> Iterator[str]:
    with open(filepath, "r") as file:
        while True:
            line = file.readline()
            if line:
                yield line.strip()
            elif watch:
                select.select([file], [], [])  # Wait until there is more data to read
            else:
                break


def _writel(items: Iterable[str], filepath: str) -> Iterator[str]:
    with open(filepath, "w") as f:
        for item in items:
            f.write(item + "\n")
            yield item


writel = curry(_writel)


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


filter_cached = curry(_filter_cached)


def run(items: Iterable[T]) -> None:
    for item in items:
        pass

import os
import glob
import asyncio
import time
import select
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from random import randint
from typing import Callable, Iterable, Iterator, List, Optional, Sequence, TypeVar


T = TypeVar("T")
U = TypeVar("U")


def curry(fn: Callable) -> Callable:
    # fn(a0, a1, a2) => curry(fn)(a1, a2)(a0)
    def fn_curried(*args, **kwargs):
        def _fn(arg0):
            return fn(arg0, *args, **kwargs)
        return _fn
    return fn_curried
        

def _pipe(items: Iterable[T], *fns: Callable) -> Iterator[U]:
    for fn in fns:
        items = fn(items)
    return items

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
    batch_size: Optional[int] = None,
    max_workers: Optional[int] = None,
) -> Iterator[U]:
    assert mode in [None, "multithread", "multiprocess"]

    if mode is None:
        yield from (fn(item) for item in items)
        return

    executors = dict(multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor)

    num_workers = max_workers or os.cpu_count()
    batch_size = batch_size or num_workers

    with executors[mode](max_workers=max_workers) as executor:
        for items_batch in batch(batch_size)(items):  # type: ignore
            futures = {executor.submit(fn, item) for item in items_batch}
            yield from (future.result() for future in as_completed(futures))

map = curry(_map)

def _sleep(items: Iterable[T], seconds: float) -> Iterator[T]:
    for item in items:
        time.sleep(seconds)
        yield item

sleep = curry(_sleep)


def watchdir(
    path: str, 
    changes: Sequence[int] = [1] # default to Change.added == 1 
) -> Iterator[str]:
    try: 
        from watchgod import awatch, Change 
    except ImportError:
        raise ImportError('watchgod is required to use watch')
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
    with open(filename, 'r') as file:
        while True:
            line = file.readline()
            if line:
                yield line.strip()
            elif watch:
                select.select([file], [], []) # Wait until there is more data to read
            else:
                break


def _writel(items: Iterable[str], filename: str) -> None: 
    with open(filename, 'w') as f:
        for item in items:
            f.write(item + '\n') 

writel = curry(_writel)
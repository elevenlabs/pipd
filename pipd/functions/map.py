from concurrent.futures import (
    FIRST_COMPLETED,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    wait,
)
from typing import Callable, Iterable, Iterator, Optional, TypeVar

from pipd import Function, Pipe, log_traceback_and_continue

T = TypeVar("T")
U = TypeVar("U")


class Map(Function):
    def __init__(
        self,
        fn: Callable[[T], U],
        num_workers: int = 0,
        buffer: Optional[int] = None,
        mode: str = "multithread",
        handler: Callable = log_traceback_and_continue,
    ) -> None:
        assert mode in ["multithread", "multiprocess"]
        self.fn = fn
        self.num_workers = num_workers
        self.buffer = buffer
        self.mode = mode
        self.handler = handler

    def __call__(self, items: Iterable[T]) -> Iterator[U]:
        if self.num_workers == 0:
            for item in items:
                try:
                    yield self.fn(item)
                except Exception as e:
                    self.handler(e)
            return

        executors = dict(
            multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor
        )

        with executors[self.mode](max_workers=self.num_workers) as executor:
            futures = set()
            self.buffer = self.buffer or self.num_workers
            for item in items:
                futures.add(executor.submit(self.fn, item))
                if len(futures) == self.buffer:
                    done, futures = wait(futures, return_when=FIRST_COMPLETED)
                    for future in done:
                        try:
                            yield future.result()
                        except Exception as e:
                            self.handler(e)
            for future in futures:
                try:
                    yield future.result()
                except Exception as e:
                    self.handler(e)


Pipe.add_fn(Map)

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Iterable, Iterator, TypeVar

from pipd import Function, Pipe, log_traceback_and_continue

T = TypeVar("T")
U = TypeVar("U")


class Side(Function):
    def __init__(
        self,
        fn: Callable[[T], U],
        num_workers: int = 0,
        mode: str = "multithread",
        handler: Callable = log_traceback_and_continue,
    ) -> None:
        assert mode in ["multithread", "multiprocess"]
        self.fn = fn
        self.num_workers = num_workers
        self.mode = mode
        self.handler = handler

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        if self.num_workers == 0:
            for item in items:
                try:
                    self.fn(item)
                except Exception as e:
                    self.handler(e)
                yield item
            return

        executors = dict(
            multithread=ThreadPoolExecutor, multiprocess=ProcessPoolExecutor
        )
        with executors[self.mode](max_workers=self.num_workers) as executor:
            for item in items:
                executor.submit(self.fn, item)
                yield item


Pipe.add_fn(Side)

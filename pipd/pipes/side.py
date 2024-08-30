from typing import Callable, Iterable, Iterator, TypeVar

from pipd import Pipe, log_traceback_and_continue

T = TypeVar("T")
U = TypeVar("U")


class Side(Pipe):
    def __init__(
        self,
        fn: Callable[[T], U],
        num_workers: int = 0,
        mode: str = "multithread",
        handler: Callable = log_traceback_and_continue,
    ) -> None:
        assert mode in ["multithread", "multiprocess"]
        def side_wrapper(item: T):
            fn(item)
            return item
        self.map = Pipe.__getattr__(self, 'map')(side_wrapper, num_workers, None, mode, handler).pipe1

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        return self.map(items)
from typing import Callable, Iterable, Iterator, TypeVar

from pipd import Function, Pipe

from .side import Side

T = TypeVar("T")


class Log(Function):
    def __init__(self, fn: Callable[[T], None] = print) -> None:
        self.fn = fn

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        return Side(self.fn)(items)


Pipe.add_fn(Log)

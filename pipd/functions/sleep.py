import time
from typing import Iterable, Iterator, TypeVar

from pipd import Function, Pipe

from .side import Side

T = TypeVar("T")


class Sleep(Function):
    def __init__(self, seconds: float) -> None:
        self.seconds = seconds

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        return Side(lambda _: time.sleep(self.seconds))(items)  # type: ignore


Pipe.add_fn(Sleep)

import time
from typing import Iterable, Iterator, TypeVar

from pipd import Pipe

from .side import Side

T = TypeVar("T")


class Sleep(Pipe):
    def __init__(self, seconds: float) -> None:
        self.seconds = seconds

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        return Side(lambda _: time.sleep(self.seconds))(items)  # type: ignore


Pipe.register(Sleep)

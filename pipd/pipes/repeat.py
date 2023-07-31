from typing import Iterable, Iterator, TypeVar

from pipd import Pipe

T = TypeVar("T")


class Repeat(Pipe):
    def __init__(self, num: int = 10**10) -> None:
        self.num = num

    def __call__(self, items: Iterable[T]) -> Iterator[T]:  # type: ignore
        for _ in range(self.num):
            for item in items:
                yield item

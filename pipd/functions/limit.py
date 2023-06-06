from typing import Iterable, Iterator, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


class Limit(Function):
    def __init__(self, limit: int = 10**100) -> None:
        self.limit = limit

    def __call__(self, items: Iterable[T]) -> Iterator[T]:
        for count, item in enumerate(items):
            if count >= self.limit:
                return
            yield item


Pipe.add_fn(Limit)

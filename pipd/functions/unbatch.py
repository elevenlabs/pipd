from typing import Iterable, Iterator, Sequence, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


class Unbatch(Function):
    def __call__(self, items: Iterable[Sequence[T]]) -> Iterator[T]:
        for b in items:
            for item in b:
                yield item


Pipe.add_fn(Unbatch)

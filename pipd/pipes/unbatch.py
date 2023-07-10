from typing import Iterable, Iterator, Sequence, TypeVar

from pipd import Pipe

T = TypeVar("T")


class Unbatch(Pipe):
    def __call__(self, items: Iterable[Sequence[T]]) -> Iterator[T]:
        for b in items:
            for item in b:
                yield item


Pipe.register(Unbatch)

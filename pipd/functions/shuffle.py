from random import randint
from typing import Iterator, List, Optional, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


def pick(items: List[T], random: bool = False) -> T:
    idx = randint(0, len(items) - 1) if random else 0
    return items.pop(idx)


class Shuffle(Function):
    def __init__(self, size: int, start: Optional[int] = None):
        self.size = size
        self.start = start or size

    def __call__(self, items: Iterator[T]) -> Iterator[T]:
        buffer = []
        for item in items:
            buffer.append(item)
            if len(buffer) < self.size:
                try:
                    buffer.append(next(items))
                except StopIteration:
                    pass
            if len(buffer) >= self.start:
                yield pick(buffer, random=True)
        # Empty buffer at the end
        while len(buffer) > 0:
            yield pick(buffer)


Pipe.add_fn(Shuffle)

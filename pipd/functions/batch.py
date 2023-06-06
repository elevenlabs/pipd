from typing import Iterable, Iterator, List, TypeVar

from pipd import Function, Pipe

T = TypeVar("T")


class Batch(Function):
    def __init__(self, size: int) -> None:
        self.size = size

    def __call__(self, items: Iterable[T]) -> Iterator[List[T]]:
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == self.size:
                yield batch
                batch = []
        if batch:
            yield batch


Pipe.add_fn(Batch)

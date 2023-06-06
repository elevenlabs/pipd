import select
from typing import Iterable, Iterator

from pipd import Function, Pipe


def read_lines(filepath: str, watch: bool = False) -> Iterator[str]:
    with open(filepath, "r") as file:
        if watch:
            while True:
                line = file.readline()
                if line:
                    yield line.strip()
                else:
                    select.select(
                        [file], [], []
                    )  # Wait until there is more data to read
        else:
            for line in file:
                yield line.strip()


class ReadLines(Function):
    def __init__(self, watch: bool = False) -> None:
        self.watch = watch

    def __call__(self, items: Iterable[str]) -> Iterator[str]:
        for filepath in items:
            yield from read_lines(filepath=filepath, watch=self.watch)


Pipe.add_fn(ReadLines)

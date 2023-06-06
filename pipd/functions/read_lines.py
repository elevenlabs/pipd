import select
from typing import Iterator

from pipd import Function, Pipe


def read_lines(filepath: str, watch: bool = False) -> Iterator[str]:
    with open(filepath, "r") as file:
        while True:
            line = file.readline()
            if line:
                yield line.strip()
            elif watch:
                select.select([file], [], [])  # Wait until there is more data to read
            else:
                break


class ReadLines(Function):
    def __init__(self, filepath: str, watch: bool = False) -> None:
        self.filepath = filepath
        self.watch = watch

    def __call__(self, *args) -> Iterator[str]:
        return read_lines(filepath=self.filepath, watch=self.watch)


Pipe.add_fn(ReadLines)

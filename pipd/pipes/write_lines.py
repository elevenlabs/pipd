from typing import Iterable, Iterator

from pipd import Pipe


def write_lines(items: Iterable[str], filepath: str) -> Iterator[str]:
    with open(filepath, "w") as f:
        for item in items:
            f.write(f"{item}\n")
            yield item


class WriteLines(Pipe):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def __call__(self, items: Iterable[str]) -> Iterator[str]:
        return write_lines(items, self.filepath)


Pipe.register(WriteLines)

from typing import Dict, Iterable, Iterator, List, Sequence, Union

from pipd import Function, Pipe


class ReadCSV(Function):
    def __init__(self, header: Union[bool, Sequence[str]] = False) -> None:
        self.header = header

    def __call__(self, items: Iterator[str]) -> Iterable[Union[Dict[str, str], List[str]]]:  # type: ignore # noqa
        import csv

        for filepath in items:
            with open(filepath, "r") as f:
                if self.header:
                    fieldnames = (
                        self.header if isinstance(self.header, Sequence) else None
                    )
                    yield from csv.DictReader(f, fieldnames=fieldnames)
                else:
                    yield from csv.reader(f)


Pipe.add_fn(ReadCSV)

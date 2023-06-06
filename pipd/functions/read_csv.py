from typing import Dict, Iterable, List, Sequence, Union

from pipd import Function, Pipe


class ReadCSV(Function):
    def __init__(
        self, filepath: str, header: Union[bool, Sequence[str]] = False
    ) -> None:
        self.filepath = filepath
        self.header = header

    def __call__(self, *args) -> Iterable[Union[Dict[str, str], List[str]]]:  # type: ignore # noqa
        import csv

        with open(self.filepath, "r") as f:
            if self.header:
                fieldnames = self.header if isinstance(self.header, Sequence) else None
                yield from csv.DictReader(f, fieldnames=fieldnames)
            else:
                yield from csv.reader(f)


Pipe.add_fn(ReadCSV)

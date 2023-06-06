from typing import Any, Dict, Iterable, Iterator, Sequence, Union

from pipd import Function, Pipe


class WriteCSV(Function):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def __call__(
        self, items: Iterable[Union[Dict[str, Any], Sequence[Any]]]
    ) -> Iterator[Union[Dict[str, Any], Sequence[Any]]]:
        import csv

        with open(self.filepath, "w", newline="") as f:
            writer = csv.writer(f)
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    if i == 0:  # Write headers only for the first dictionary item
                        writer.writerow(item.keys())
                    item = item.values()  # type: ignore
                writer.writerow(item)
                yield item


Pipe.add_fn(WriteCSV)

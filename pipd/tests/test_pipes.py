import pytest
from pipd import Pipe


def test_merged_pipe():
    from pipd import MergedPipe

    pipe = Pipe(0, 1, 2, 3)
    pipe1 = Pipe("a", "b", "c", "d", "e")
    merged = MergedPipe(pipe, pipe1)

    it = iter(merged)
    assert next(it) == 0
    assert next(it) == "a"
    assert next(it) == 1
    assert next(it) == "b"
    assert next(it) == 2
    assert next(it) == "c"
    assert next(it) == 3
    assert next(it) == "d"
    with pytest.raises(StopIteration):
        next(it)

    pipe = Pipe(0, 1, 2, 3)
    pipe1 = Pipe("a", "b", "c", "d", "e")
    merged = MergedPipe(pipe, pipe1, repeat=True)

    it = iter(merged)
    assert next(it) == 0
    assert next(it) == "a"
    assert next(it) == 1
    assert next(it) == "b"
    assert next(it) == 2
    assert next(it) == "c"
    assert next(it) == 3
    assert next(it) == "d"
    assert next(it) == 0
    assert next(it) == "e"
    assert next(it) == 1
    assert next(it) == "a"

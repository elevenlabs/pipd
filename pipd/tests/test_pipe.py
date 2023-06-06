from pipd import Pipe


def test_pipe():
    pipe = Pipe(0, 1, 2, 3)
    assert list(pipe) == [0, 1, 2, 3]

    pipe = Pipe([0, 1, 2, 3])
    assert list(pipe) == [0, 1, 2, 3]

    pipe = Pipe(range(4))
    assert list(pipe) == [0, 1, 2, 3]

    class ClassWithGetItem:
        def __getitem__(self, key):
            return key

    pipe = Pipe(ClassWithGetItem())
    assert next(pipe) == 0
    assert next(pipe) == 1
    assert next(pipe) == 2


def test_add():
    pipe0 = Pipe(0, 1, 2, 3)
    pipe1 = Pipe(4, 5, 6, 7)
    pipe = pipe0 + pipe1
    assert list(pipe) == [0, 1, 2, 3, 4, 5, 6, 7]

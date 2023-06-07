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
    it = iter(pipe)
    assert next(it) == 0
    assert next(it) == 1
    assert next(it) == 2

    pipe = Pipe(0, 1, 2, 3)

    def gen():
        yield from pipe

    assert list(gen()) == [0, 1, 2, 3]


def test_metaclass():
    pipe = Pipe
    assert list(pipe(0, 1, 2, 3)) == [0, 1, 2, 3]

    pipe = Pipe.map(lambda x: x + 1)
    assert list(pipe(0, 1, 2, 3)) == [1, 2, 3, 4]


# def test_merge():
#     pipe0 = Pipe(0, 0, 0, 0, 0, 0)
#     pipe1 = Pipe(1, 1, 1, 1, 1, 1)
#     pipe = Pipe.merge(pipe0, pipe1, weights=[3, 1])
#     print(list(pipe))

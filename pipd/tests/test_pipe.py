from pipd import Pipe


def test_pipe():
    pipe = Pipe([0, 1, 2, 3])
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


def test_dot_chaining():
    pipe = Pipe([0, 1, 2, 3]).map(lambda x: x + 1).map(lambda x: x * 2)
    assert list(pipe) == [2, 4, 6, 8]


def test_class_chaining():
    from pipd import Map

    pipe = Pipe([0, 1, 2, 3]) | Map(lambda x: x + 1) | Map(lambda x: x * 2)
    assert list(pipe) == [2, 4, 6, 8]

    pipe = Map(lambda x: x + 1) | Map(lambda x: x * 2)
    assert list(pipe([0, 1, 2, 3])) == [2, 4, 6, 8]


def test_metaclass():

    pipe = Pipe.map(lambda x: x + 1)
    assert list(pipe([0, 1, 2, 3])) == [1, 2, 3, 4]

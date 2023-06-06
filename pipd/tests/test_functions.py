from pipd import Pipe


def double(x):
    return x * 2


def test_map():
    pipe = Pipe(range(5)).map(lambda x: x * 2)
    assert list(pipe) == [0, 2, 4, 6, 8]

    pipe = Pipe(range(5)).map(lambda x: x * 2, num_workers=2)
    assert sorted(pipe) == [0, 2, 4, 6, 8]

    # Multiprocess doesn't support lambdas or closures
    pipe = Pipe(range(5)).map(double, num_workers=2, mode="multiprocess")
    assert sorted(pipe) == [0, 2, 4, 6, 8]


def test_filter():
    pipe = Pipe(range(5)).filter(lambda x: x % 2 == 0)
    assert list(pipe) == [0, 2, 4]

    pipe = Pipe(range(5)).filter(lambda x: x % 2 == 0, num_workers=2)
    assert sorted(pipe) == [0, 2, 4]


def test_side():
    pipe = Pipe(range(5)).side(lambda x: x * 2)
    assert list(pipe) == [0, 1, 2, 3, 4]

    pipe = Pipe(range(5)).side(lambda x: x * 2, num_workers=2)
    assert list(pipe) == [0, 1, 2, 3, 4]


def test_batch():
    pipe = Pipe(range(5)).batch(2)
    assert list(pipe) == [[0, 1], [2, 3], [4]]


def test_unbatch():
    pipe = Pipe([[0, 1], [2, 3], [4]]).unbatch()
    assert list(pipe) == [0, 1, 2, 3, 4]


def test_shuffle():
    pipe = Pipe(range(5)).shuffle(2)
    assert list(pipe) != [0, 1, 2, 3, 4]


def test_limit():
    pipe = Pipe(range(5)).limit(3)
    assert list(pipe) == [0, 1, 2]


def test_read_lines():
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("1\n2\n3\n4\n5")
        f.close()
        pipe = Pipe().read_lines(f.name)
        assert list(pipe) == ["1", "2", "3", "4", "5"]
        os.remove(f.name)


def test_write_lines():
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        pipe = Pipe(range(5)).write_lines(f.name)
        pipe()
        with open(f.name, "r") as f2:
            assert f2.read() == "0\n1\n2\n3\n4\n"
        os.remove(f.name)


def test_filter_cached():
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        pipe = Pipe(range(5)).filter_cached(f.name)
        assert list(pipe) == [0, 1, 2, 3, 4]
        pipe = Pipe(range(6)).filter_cached(f.name)
        assert list(pipe) == [5]
        os.remove(f.name)


def test_read_csv():
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("1,2,3,4,5\n6,7,8,9,10")
        f.close()
        pipe = Pipe().read_csv(f.name)
        assert list(pipe) == [["1", "2", "3", "4", "5"], ["6", "7", "8", "9", "10"]]
        os.remove(f.name)


def test_write_csv():
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        pipe = Pipe([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]).write_csv(f.name)
        pipe()
        with open(f.name, "r") as f2:
            assert f2.read() == "1,2,3,4,5\n6,7,8,9,10\n"
        os.remove(f.name)

    # Test with dict
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        pipe = Pipe(
            [
                {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                {"a": 6, "b": 7, "c": 8, "d": 9, "e": 10},
            ]
        ).write_csv(f.name)
        pipe()
        with open(f.name, "r") as f2:
            assert f2.read() == "a,b,c,d,e\n1,2,3,4,5\n6,7,8,9,10\n"
        os.remove(f.name)


def test_read_files():
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "f1.txt"), "w") as f1:
            f1.write("a")
        with open(os.path.join(d, "f2.txt"), "w") as f2:
            f2.write("b")
        pipe = Pipe().read_files(f"{d}/*.txt")
        assert list(pipe) == [f1.name, f2.name]
        os.remove(f1.name)
        os.remove(f2.name)

## ⚙️ Install

```bash
pip install pipd
```

## Basics

_Create a pipeline_
```py
from pipd import Pipe
pipe = Pipe(1, 2, 3, 4, 5)
# or
pipe = Pipe([1, 2, 3, 4, 5])
```

_Chaining (dot-based)_
```py
pipe = Pipe(1, 2, 3, 4, 5).map(lambda x: x + 1).map(lambda x: x * 2)
list(pipe) == [4, 6, 8, 10, 12]
```

_Chaining (pipe-based)_
```py
from pipd import Pipe, Map
pipe = Pipe(1, 2, 3, 4, 5) | Map(lambda x: x + 1) | Map(lambda x: x * 2)
list(pipe) == [4, 6, 8, 10, 12]
```

_Use a meta pipeline (i.e. functional only)_
```py
pipe = Pipe.map(lambda x: x + 1).map(lambda x: x * 2)
# or
pipe = Map(lambda x: x + 1) | Map(lambda x: x * 2)

list(pipe([1, 2, 3, 4, 5])) == [4, 6, 8, 10, 12]
```

_Iterate over the pipeline_
```py
for item in pipe:
    # do something with item
```

_Iterate over the pipeline one item at a time_
```py
it = iter(pipe)
next(it)
next(it)
```


## Functions
### `map`
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2)
list(pipe) == [2, 4, 6]
```

_Map items to parallel workers_
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2, num_workers=2) # parallel map (note: order is not guaranteed)
list(pipe) == [2, 4, 6]
```

### `filter`

```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).filter(lambda x: x != 1)
list(pipe) == [2, 3]
```

### `side`

Applies a function on each item in the pipeline without changing the item, useful for logging, saving state, etc.
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).side(lambda x: print('side', x))
it = iter(pipe)
print(next(it))
print(next(it))
```

<details> <summary> Show output </summary>

```py
side 1
1
side 2
2
```

</details>

### `batch`
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3, 4, 5).batch(2)
list(pipe) == [[1, 2], [3, 4], [5]]
```

### `unbatch`

```py
from pipd import Pipe

pipe = Pipe([1, 2], [3], [4, 5]).unbatch()
list(pipe) == [1, 2, 3, 4, 5]
```

### `log`

```py
from pipd import Pipe

pipe = Pipe(range(10)).log()
list(pipe) # runs the pipeline
```

<details> <summary> Show output </summary>

```py
0
1
2
3
4
5
6
7
8
9
```

</details>

### `limit`
```py
from pipd import Pipe

pipe = Pipe(range(10)).limit(5).log()
list(pipe) == [0, 1, 2, 3, 4]
```

### `repeat`
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).repeat(2)
list(pipe) == [1, 2, 3, 1, 2, 3]
```

### `sleep`
Useful for debugging a pipeline that runs too fast.
```py
from pipd import Pipe

pipe = Pipe(range(5)).sleep(0.1).log()
list(pipe) # runs the pipeline
```

<details> <summary> Show output </summary>

```py
0 # sleep for 0.1 seconds
1 # sleep for 0.1 seconds
2 # sleep for 0.1 seconds
3 # sleep for 0.1 seconds
4 # sleep for 0.1 seconds
```

</details>


### `tqdm`
Shows a progress bar for the pipeline, useful to check how many `s/it` a pipeline is running at. Requires `tqdm` to be installed.
```py
from pipd import Pipe

pipe = Pipe(range(5)).sleep(1).tqdm()
print(list(pipe))
```

<details> <summary> Show output </summary>

```bash
0it [00:00, ?it/s]
1it [00:01,  1.01s/it]
2it [00:02,  1.01s/it]
3it [00:03,  1.01s/it]
4it [00:04,  1.00s/it]
5it [00:05,  1.01s/it]

[0, 1, 2, 3, 4]
```

</details>


### `mix`

Mixes iterators or pipes together, either interleaved or random.

```py
from pipd import Pipe, Mix

pipe = Pipe.mix([1, 2, 3], ['a', 'b', 'c'])
# or
pipe = Mix([1, 2, 3], ['a', 'b', 'c'])
list(pipe) == [1, 'a', 2, 'b', 3, 'c']
```

```py
from pipd import Pipe

pipe = Pipe.mix(
    Pipe(1, 2, 3),
    Pipe('a', 'b', 'c'),
    random=True # randomize from which iterator/pipe to take the next item
)
list(pipe) == [1, 2, 'a', 'b', 3, 'c']
```

### `map_key`
```py
from pipd import Pipe

pipe = Pipe([{'a': 1, 'b': 2}, {'a': 2, 'b': 4}]).map_key('a', lambda x: x + 1)
list(pipe) == [{'a': 2, 'b': 2}, {'a': 3, 'b': 4}]
```


### `shuffle`
```py
from pipd import Pipe

pipe = Pipe(range(10)).shuffle(size=5) # Shuffle buffer has size 5
list(pipe) == [3, 5, 6, 0, 2, 4, 1, 7, 8, 9]
```

### `read_files`
```py
from pipd import Pipe

pipe = Pipe(['*.md']).read_files()
list(pipe) == ['README.md']
```

### `read_lines`
```py
from pipd import Pipe

pipe = Pipe(['.gitignore', 'setup.py']).read_lines()
list(pipe)
```

<details> <summary> Show output </summary>

```py
['__pycache__',
 '.mypy_cache',
 '.DS_Store',
 'TODO.md',
 '*.ipynb',
 'from setuptools import find_packages, setup',
 '',
 'setup(',
 'name="pipd",',
 'packages=find_packages(exclude=[]),',
 'version="0.2.1",',
 'description="Utility functions for python data pipelines.",',
 'long_description_content_type="text/markdown",',
 'author="ElevenLabs",',
 'url="https://github.com/elevenlabs/pipd",',
 'keywords=["data processing", "pipeline"],',
 'install_requires=[],',
 'classifiers=[],',
 ')']
```

</details>

### `write_lines`
```py
from pipd import Pipe

pipe = Pipe([0, 1, 2, 3]).write_lines('test.txt')
list(pipe) == [0, 1, 2, 3]
```

<details> <summary> test.txt </summary>

```py
0
1
2
3
```

</details>

### `filter_cached`

Saves items to cache `filepath` such that once the pipeline is run again, the items are filtered out.
The optional `key` function can be used to specify a custom key for the cache.

```py
from pipd import Pipe

pipe = Pipe(range(5)).filter_cached(filepath='./cache.txt', key=lambda x: x)

list(pipe) == [0, 1, 2, 3, 4]
list(pipe) == []
```

<details> <summary> cache.txt </summary>

```py
0
1
2
3
4
```

</details>

### `read_csv`
### `write_csv`

## Create custom `Pipe` object

```py
class PlusOne(Pipe):

    def __call__(self, items):
        for item in items:
            yield item + 1

# Usage

pipe = Pipe([0,1,2]).plus_one()
list(pipe) == [1,2,3]

# or

pipe = Pipe([0,1,2]) | PlusOne()
list(pipe) == [1,2,3]

# or

pipe = PlusOne()
list(pipe([0,1,2])) == [1,2,3]

# multi

pipe = Pipe([0,1,2]).plus_one().plus_one()
list(pipe) == [2,3,4]
```

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

_Use a meta pipeline (i.e. functional only)_
```py
pipe = Pipe.map(lambda x: x + 1)

pipe([1, 2, 3, 4, 5]).list() == [2, 3, 4, 5, 6]
```

## Functions
### `map`
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2)
print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[2, 4, 6]
```

</details>

_Map items to parallel workers_
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2, num_workers=2) # parallel map (note: order is not guaranteed)
print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[2, 4, 6]
```

</details>

### `filter`

```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).filter(lambda x: x != 1)
print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[2, 3]
```

</details>

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
it = iter(pipe)
print(next(it))
print(next(it))
print(next(it))
```

<details> <summary> Show output </summary>

```py
[1, 2]
[3, 4]
[5]
```

</details>

### `unbatch`

```py
from pipd import Pipe

pipe = Pipe([1, 2], [3], [4, 5]).unbatch()
print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[1, 2, 3, 4, 5]
```

</details>

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
list(pipe) # runs the pipeline
```

<details> <summary> Show output </summary>

```py
0
1
2
3
4
```

</details>

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

### `shuffle`
### `read_files`
### `read_lines`
### `write_lines`
### `filter_cached`


## Pipes

### `MergedPipe`
```py
from pipd import Pipe, MergedPipe

pipe = MergedPipe(
    Pipe(1, 2, 3),
    Pipe('a', 'b', 'c')
)

print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[1, 'a', 2, 'b', 3, 'c']
```

</details>

```py
from pipd import Pipe, MergedPipe

pipe = MergedPipe(
    Pipe(1, 2, 3),
    Pipe('a', 'b', 'c'),
    random=True # randomize from which pipe to take the next item
)

print(list(pipe))
```

<details> <summary> Show output </summary>

```py
[1, 2, 'a', 'b', 3, 'c']
```

</details>

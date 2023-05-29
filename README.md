## ⚙️ Install

```bash
pip install pipd
```

## Usage

### Basics

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
next(pipe)
```

_Consume/run entire pipeline_
```py
pipe()
```


### `map`
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2)

print(next(pipe))
print(next(pipe))
print(next(pipe))
```

<details> <summary> Show output </summary>

```py
2
4
6
```

</details>

_Map items to parallel workers_
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).map(lambda x: x * 2, num_workers=2) # parallel map (note: order is not guaranteed)

print(next(pipe))
print(next(pipe))
print(next(pipe))
```

<details> <summary> Show output </summary>

```py
4
2
6
```

</details>

### `filter`

```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).filter(lambda x: x != 1)

print(next(pipe))
print(next(pipe))
```

<details> <summary> Show output </summary>

```py
2
3
```

</details>

### `side`

Applies a function on each item in the pipeline without changing the item, useful for logging, saving state, etc.
```py
from pipd import Pipe

pipe = Pipe(1, 2, 3).side(lambda x: print('side', x))

print(next(pipe))
print(next(pipe))
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

print(next(pipe))
print(next(pipe))
print(next(pipe))
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

print(next(pipe))
print(next(pipe))
print(next(pipe))
print(next(pipe))
print(next(pipe))
```

<details> <summary> Show output </summary>

```py
1
2
3
4
5
```

</details>

### `log`

```py
from pipd import Pipe

pipe = Pipe(range(10)).log()
pipe() # run the pipeline
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
pipe() # run the pipeline
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

### `tqdm`

### `sleep`

### `shuffle`

### `Readf`, `readf`

### `Readl`, `readl`

### `writel`

### `filter_cached`

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

### `unpipe`

### `limit`

### `tqdm`

### `buffer`

### `sleep`

### `Readf`, `readf`

### `Readl`, `readl`

### `writel`

### `filter_cached`

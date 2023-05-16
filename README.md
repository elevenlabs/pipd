## ⚙️ Install

```bash
pip install git+ssh://git@github.com/elevenlabs/pipd.git
```

## Usage

### `map`
```py
from pipd import map

map(lambda x: x ** 2, mode='multithread', batch_size=4)([1, 2, 3, 4]) # [1, 4, 9, 16]
```

### Example 0
```py
from pipd import pipe, batch, sleep, map, buffer, unbatch

def my_fn(items):
    return [item ** 2 for item in items]

pipeline = pipe(
    batch(size=10),
    sleep(0.2),
    map(my_fn, mode='multithread', batch_size=4),
    buffer(size=8, start=8),
    unbatch(),
)(range(1000))

for y in pipeline:
    print(y)
```

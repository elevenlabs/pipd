## ⚙️ Install

```bash
pip install pipd
```

## 🗣️ Usage

### `map`
```py
from pipd import map

map(lambda x: x ** 2, mode='multithread', batch_size=4)([1, 2, 3, 4]) # [1, 4, 9, 16]
```

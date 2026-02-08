# Sprachspiel - Claude Instructions

## Coding Standards

This project requires **strict type annotations** for all Python code.

### Type Annotations Rules

1. **Annotate all function parameters and return types**
   ```python
   def process_data(items: list[str]) -> dict[str, Any]:
       ...
   ```

2. **Annotate class attributes and method parameters**
   ```python
   class MyClass:
       value: int

       def __init__(self, value: int) -> None:
           self.value = value
   ```

3. **Use generic type parameters (Python 3.10+)**
   ```python
   # Good - explicit types
   items: list[str] = []
   mapping: dict[str, Any] = {}

   # Bad - use bare types
   items = []
   mapping = {}
   ```

4. **Use `Optional[T]` for nullable types**
   ```python
   from typing import Optional

   def get_name(name: Optional[str]) -> str:
       return name or "Unknown"
   ```

5. **Import `Any` from typing for unknown/variant types**
   ```python
   from typing import Any

   def handle_response(data: dict[str, Any]) -> None:
       ...
   ```

6. **Use TYPE_CHECKING for forward references**
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from sprachspiel.core.card import CardData
   else:
       CardData = object  # type: ignore
   ```

7. **Use proper coroutine types for async functions**
   ```python
   from typing import Coroutine

   async def get_value() -> Coroutine[Any, Any, str]:
       ...
   ```

8. **Mark intentionally unused variables with underscore prefix**
   ```python
   def process(_unused: int, value: int) -> None:
       pass
   ```

9. **Use `# type: ignore[...]` for unavoidable violations**
   ```python
   # For FastAPI decorator false positives
   @app.get("/")  # type: ignore[misc]
   def endpoint() -> dict[str, Any]:
       ...

   # For external library issues
   import ebooklib  # type: ignore
   ```

### Common Patterns

#### Dictionary/Dict types
```python
from typing import Any

config: dict[str, Any] = {"key": "value"}
headers: dict[str, str] = {"Content-Type": "application/json"}
```

#### List types
```python
items: list[str] = ["item1", "item2"]
numbers: list[int] = [1, 2, 3]

# For heterogeneous lists
mixed: list[dict[str, Any]] = [{"name": "test"}]
```

#### Async/Await
```python
import asyncio

# In sync context, use asyncio.run()
result = asyncio.run(async_function())

# In async context, use await
result = await async_function()
```

#### External library workarounds
```python
# For libraries without proper type stubs
import ebooklib  # type: ignore

# Use type: ignore for specific lines if needed
with ebooklib.EpubFile(...) as epub:  # type: ignore
    ...
```

## Project Structure

- `sprachspiel/core/` - Core business logic (card, engine, queue, mapper)
- `sprachspiel/services/` - External services (AI, TTS, Dictionary)
- `sprachspiel/anki/` - Anki integration (connect, file_export, base)
- `sprachspiel/parsers/` - Subtitle parsers (SRT, VTT, ASS)
- `sprachspiel/sources/` - Data source handling (reader, player, file_import)
- `sprachspiel/server/` - FastAPI server (app, routes)
- `sprachspiel/cli.py` - Command-line interface
- `tests/` - Unit tests

## Key Dependencies

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Click** - CLI framework
- **AnkiConnect** - Anki integration
- **ebooklib** - EPUB file handling

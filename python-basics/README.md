# Python Patterns for Backend and AI Code

This is a guided series for Python developers who already know core syntax, collections, modules, and inheritance, but want a stronger mental model for modern backend and AI code.

## How To Use This Guide

Create a separate file for each exercise, for example `exercise_01.py`. Read the theory, run the tiny example, complete the task without copying a solution, and answer the reflection question in your own words.

The first exercises use only the standard library. Exercises 11-15 introduce Pydantic, FastAPI, and LangChain-style patterns. Install those dependencies only when you reach them:

```powershell
pip install pydantic fastapi langchain
```

## Your Starting Point

You already understand ordinary functions, collections, modules, and inheritance. The main new vocabulary is:

- A type annotation describes an expected shape; it is usually not runtime validation by itself.
- `Callable[[str], int]` means a callable accepting one `str` and returning an `int`.
- A dataclass is a class whose data-focused methods, such as `__init__`, can be generated for you.
- Composition means building an object from other objects instead of relying only on inheritance.
- A decorator receives a function and returns a replacement or enhanced function.
- `await` pauses the current coroutine until an awaitable progresses; other scheduled tasks can run during that pause.
- Middleware receives a request and a next `handler`, can inspect or change the request, and then decides whether and how to call the handler.

---

## Exercise 1: Functions As Values

### Theory

In Python, functions are objects. You can store them in variables, put them in lists, pass them to other functions, and return them from functions. This is the foundation of callbacks and middleware.

### Example

```python
def double(value: int) -> int:
    return value * 2

operation = double
print(operation(4))  # 8
```

### Task

Write `apply_operation(value, operation)` that accepts a number and a function, then returns the function result. Try it with `double`, a function that squares, and a lambda that adds ten.

### Hints

- The parameter `operation` is called like `operation(value)`.
- A function name without parentheses is a function value.

### Expected Outcome

You can pass different behavior into one reusable function without changing `apply_operation`.

### Reflection

Why is `operation` written without parentheses when it is passed to `apply_operation`?

---

## Exercise 2: Callbacks And Closures

### Theory

A callback is a function passed to another function to be called later. A closure is an inner function that remembers values from the outer function even after the outer function returns.

### Example

```python
def make_multiplier(factor: int):
    def multiply(value: int) -> int:
        return value * factor
    return multiply

triple = make_multiplier(3)
print(triple(5))  # 15
```

### Task

Create `run_pipeline(values, steps)`. It should apply each callback in `steps` to every value and return the transformed list. Build a pipeline that strips text, lowercases it, and adds an exclamation mark.

### Hints

- `steps` is a list of functions.
- Each step receives the result of the previous step.

### Expected Outcome

You can explain both callback and closure, and you can build behavior from small functions.

### Reflection

What value does the inner function remember from `make_multiplier`?

---

## Exercise 3: Reading Type Annotations

### Theory

Annotations communicate intent to humans and tools. They do not usually change how Python executes a function. Read them from the outside inward: `list[str]` is a list whose items are strings; `Callable[[str], int]` is a function signature.

### Example

```python
from collections.abc import Callable

Formatter = Callable[[str], str]

def format_names(names: list[str], formatter: Formatter) -> list[str]:
    return [formatter(name) for name in names]
```

### Task

Define aliases for a parser that accepts `str` and returns `int`, and a validator that accepts `int` and returns `bool`. Annotate a function that receives a list of strings and both callables.

### Hints

- Prefer `collections.abc.Callable` in modern Python.
- The inner list in `Callable[[str], int]` describes parameter types, not a list value.

### Expected Outcome

You can translate nested annotations into plain English before writing the implementation.

### Reflection

What does `Callable[[], str]` mean compared with `Callable[[str], str]`?

---

## Exercise 4: Generics, Unions, And Type Aliases

### Theory

Generic types describe reusable containers. A union describes alternatives. `str | None` means either a string or `None`; it does not mean the value is always a string.

### Example

```python
from typing import TypeAlias

UserId: TypeAlias = int
Result = dict[str, str | int]

def find_name(users: dict[UserId, str], user_id: UserId) -> str | None:
    return users.get(user_id)
```

### Task

Create a `JsonValue` alias for `str | int | float | bool | None`, then annotate a function that accepts a dictionary of JSON-like values and returns one value by key. Handle a missing key safely.

### Hints

- A union describes what may be returned.
- Use `.get()` or check membership before indexing.

### Expected Outcome

Your code clearly communicates optional values and structured dictionaries.

### Reflection

What must a caller do before using the result of a function returning `str | None` as a string?

---

## Exercise 5: Dataclasses

### Theory

A dataclass is useful when a class primarily stores data. The decorator generates common methods such as `__init__` and `__repr__`. It is still a normal class and can have methods and validation logic.

### Example

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

user = User("Ada", 36)
print(user.name)
```

### Task

Create a `Message` dataclass with `role`, `content`, and an optional `metadata` dictionary. Add a method `is_from_user()`. Create user and assistant messages and print them.

### Hints

- Use `field(default_factory=dict)` for a fresh dictionary per instance.
- Do not use `{}` directly as a mutable default.

### Expected Outcome

You can identify when a dataclass is simpler than a manually written data class.

### Reflection

Why should each `Message` get its own metadata dictionary?

---

## Exercise 6: Composition Over Inheritance

### Theory

Composition means one object contains another object and delegates work to it. This keeps responsibilities separate and makes pieces replaceable. An agent can contain a model, tools, and a repository without inheriting from all of them.

### Example

```python
class Clock:
    def now(self) -> str:
        return "12:00"

class Greeting:
    def __init__(self, clock: Clock):
        self.clock = clock

    def text(self) -> str:
        return f"It is {self.clock.now()}"
```

### Task

Build a `ReportService` that receives a `Formatter` object in its constructor. The formatter should have a `format(title, rows)` method. Implement a plain-text formatter and a JSON formatter.

### Hints

- The service should not know the formatter's internal details.
- Instantiate `ReportService(TextFormatter())` and `ReportService(JsonFormatter())`.

### Expected Outcome

You can replace one collaborator without rewriting the service.

### Reflection

What would be harder if `ReportService` created its formatter internally?

---

## Exercise 7: Protocols And Duck Typing

### Theory

Python often cares about what an object can do rather than its exact class. A `Protocol` documents the required methods for static checkers while preserving duck typing at runtime.

### Example

```python
from typing import Protocol

class Sender(Protocol):
    def send(self, message: str) -> None: ...

def notify(sender: Sender, message: str) -> None:
    sender.send(message)
```

### Task

Define a `Repository` protocol with `save(key, value)` and `get(key)`. Implement an in-memory repository and use it with a function that does not know the concrete class.

### Hints

- The implementation does not need to inherit from `Repository`.
- Match method names and signatures.

### Expected Outcome

You understand how protocols create flexible boundaries between application code and adapters.

### Reflection

Why can an object satisfy a protocol without explicitly inheriting from it?

---

## Exercise 8: Exceptions And Result-Oriented Errors

### Theory

Exceptions are appropriate when an operation cannot continue normally. At an application boundary, catch expected exceptions and return a useful result or error message. Do not hide every exception with a bare `except`.

### Example

```python
def parse_port(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError("port is out of range")
    return port
```

### Task

Write `load_port(value)` that returns `tuple[int | None, str | None]`. On success return `(port, None)`; on invalid input return `(None, error_message)`. Test empty text, non-numeric text, zero, and a valid port.

### Hints

- Catch `ValueError` around the conversion and validation.
- Keep the original function strict; make the wrapper friendly.

### Expected Outcome

You can distinguish raising an error inside a domain function from handling it at a boundary.

### Reflection

When would returning an error object be clearer than raising an exception?

---

## Exercise 9: Decorators

### Theory

A decorator is a function that receives another function and returns a wrapped function. `functools.wraps` preserves the wrapped function's name and documentation. Decorators are commonly used for logging, timing, authorization, and framework registration.

### Example

```python
from functools import wraps
from collections.abc import Callable
from typing import Any

def log_call(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"calling {function.__name__}")
        return function(*args, **kwargs)
    return wrapper
```

### Task

Create a `require_role(role)` decorator factory. The decorated function must receive a keyword argument `current_role`; raise `PermissionError` if it does not match. Preserve the original function metadata.

### Hints

- The outer function receives the required role.
- The middle function receives the original function.
- The wrapper receives `*args` and `**kwargs`.

### Expected Outcome

You can explain the three layers of a decorator factory and why `wraps` matters.

### Reflection

What does `@require_role("admin")` become conceptually before Python calls the decorated function?

---

## Exercise 10: Callable Objects And Dependency Injection

### Theory

An object with `__call__` can be used like a function while holding configuration and state. Dependency injection means a function receives its collaborators instead of constructing them internally.

### Example

```python
class Prefixer:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, text: str) -> str:
        return f"{self.prefix}{text}"

add_log_prefix = Prefixer("LOG: ")
print(add_log_prefix("started"))
```

### Task

Create a `Retry` callable object that receives a function and a maximum attempt count. It should call the function until it succeeds or attempts are exhausted. Inject a fake unstable function for testing.

### Hints

- Store the function in `self.function`.
- A callable object can be passed anywhere a callback is expected.
- Re-raise the last exception after the final attempt.

### Expected Outcome

You can recognize a class instance used as a configured callback or dependency.

### Reflection

Why might a callable object be better than a closure when configuration becomes larger?

---

## Exercise 11: Pydantic Validation And Serialization

### Theory

Type hints describe intent, but Pydantic models validate and normalize data at runtime. This is why FastAPI commonly uses Pydantic models at request boundaries.

### Example

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=130)

user = UserInput.model_validate({"name": "Ada", "age": 36})
print(user.model_dump())
```

### Task

Create an `EmailRequest` model with validated recipient, non-empty subject, and body limited to 10,000 characters. Try valid data and invalid data, then print validation errors.

### Hints

- Use `EmailStr` only if the email extra is installed; otherwise begin with a non-empty string.
- `ValidationError` is the exception to catch for user input.

### Expected Outcome

You can explain the difference between a plain dictionary and a validated, serializable model.

### Reflection

Where should validation happen when data enters an application?

---

## Exercise 12: Async Coroutines And Tasks

### Theory

Calling an `async def` function creates a coroutine object; it does not execute the body immediately. `await` runs it from the current coroutine's perspective. `asyncio.create_task` schedules multiple operations so they can make progress concurrently during I/O waits.

### Example

```python
import asyncio

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return name

async def main() -> None:
    results = await asyncio.gather(fetch("a", 1), fetch("b", 1))
    print(results)

asyncio.run(main())
```

### Task

Write three async fake service calls with different delays. Compare sequential `await` calls with `asyncio.gather`. Print elapsed time for both approaches.

### Hints

- Use `time.perf_counter()`.
- The total time for concurrent calls is close to the longest delay, not the sum.
- Do not call `asyncio.run` from inside an already running event loop.

### Expected Outcome

You can explain coroutine creation, awaiting, scheduling, and I/O concurrency.

### Reflection

Why does `await` pause one coroutine without necessarily blocking every other scheduled coroutine?

---

## Exercise 13: Context Managers And Resource Lifecycle

### Theory

A context manager controls setup and cleanup around a `with` block. Files, database connections, locks, and client sessions use this pattern so cleanup happens even when an exception occurs.

### Example

```python
class ManagedResource:
    def __enter__(self):
        print("open")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("close")
        return False
```

### Task

Create a context manager for a temporary SQLite connection. Create a table, insert one row, query it, and guarantee the connection closes. Test the behavior when a query raises an exception.

### Hints

- `__exit__` returning `False` lets the original exception propagate.
- The standard library `sqlite3.Connection` can itself be used as a context manager, but implement a wrapper for learning.

### Expected Outcome

You can identify where resource ownership begins and ends.

### Reflection

Why is cleanup in `__exit__` safer than asking every caller to remember a close method?

---

## Exercise 14: Middleware With Request And Handler

### Theory

Middleware is a function around another function. The `request` is the current input object. The `handler` is the next step in the pipeline. A middleware may inspect the request, modify it, call the handler, and modify the response.

This explains a signature such as:

```python
from collections.abc import Callable

def middleware(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    return handler(request)
```

Read it as: “accept one `ModelRequest` and a function that turns a `ModelRequest` into a `ModelResponse`; return a `ModelResponse`.”

### Example

```python
from dataclasses import dataclass
from collections.abc import Callable

@dataclass
class Request:
    text: str

@dataclass
class Response:
    text: str

def uppercase_middleware(
    request: Request,
    handler: Callable[[Request], Response],
) -> Response:
    changed = Request(request.text.upper())
    return handler(changed)
```

### Task

Build a middleware pipeline with logging, authentication, and timing middleware. Each middleware receives `(request, handler)`. The final handler returns a response. Compose the pipeline so logging wraps authentication, which wraps timing, which wraps the final handler.

### Hints

- A middleware calls the next layer with `handler(request)`.
- Build a helper that folds a list of middleware functions around the final handler.
- Authentication may return an error response without calling the handler.

### Expected Outcome

You can trace control flow from the first middleware through the handler and back out.

### Reflection

What happens if middleware never calls `handler(request)`? When might that be intentional?

---

## Exercise 15: FastAPI And LangChain-Style Capstone

### Theory

FastAPI uses type annotations and Pydantic models to parse requests, validate data, and generate API documentation. LangChain-style middleware uses the same Python ideas: typed request objects, callable handlers, decorators for registration, and context/state objects for runtime information.

### Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    return {"reply": f"You said: {request.message}"}
```

A simplified AI middleware boundary looks like this:

```python
from collections.abc import Callable

class ModelRequest:
    def __init__(self, prompt: str):
        self.prompt = prompt

class ModelResponse:
    def __init__(self, text: str):
        self.text = text

def add_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    request.prompt = "Answer clearly. " + request.prompt
    return handler(request)
```

### Task

Build a small local assistant service with these parts:

1. A Pydantic `ChatRequest` containing `message`, `thread_id`, and optional `user_role`.
2. A dataclass `RuntimeContext` containing the user ID and role.
3. A SQLite repository that stores user messages and assistant replies.
4. A plain Python model adapter with `invoke(request) -> response`; it may echo text instead of calling an API.
5. Middleware that adds context, logs requests, and blocks an `external` role from a protected command.
6. A FastAPI `POST /chat` endpoint that validates the request, invokes the pipeline, and returns a Pydantic response model.
7. A test or script that sends valid input, invalid input, and a blocked protected request.

### Hints

- Keep the model adapter independent from FastAPI.
- Use composition: the pipeline receives a model adapter and repository.
- The handler passed to middleware is simply the next callable in the chain.
- Use SQLite parameters (`?`) rather than string interpolation in SQL.
- Begin with a fake model; replace it with LangChain only after the boundaries work.

### Expected Outcome

You can start from a line such as:

```python
def state_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
```

and design the surrounding objects, dependencies, and control flow instead of treating the signature as magic.

### Reflection

Which parts of your capstone are framework-independent, and which parts belong specifically to FastAPI or LangChain?

---

## Suggested Review Checklist

After each exercise, explain these items without looking them up:

- What are the input and output types?
- Is the value a class, an instance, or a function object?
- Who owns the dependency and who is allowed to replace it?
- Does the function call the next handler, return early, or raise an error?
- Is the operation synchronous or asynchronous?
- What validates the data at runtime?
- What cleanup or approval must happen before the operation completes?

from typing import Callable

def double(value: int) -> int:
    return value * 2

def apply_operation(value:int, operation: Callable[[int], int]):
    return operation(value)

operation = double
print(apply_operation(3, double))
print(apply_operation(3, lambda x: x **2))
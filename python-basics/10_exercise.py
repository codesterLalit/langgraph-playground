import random
from collections.abc import Callable

def fake_test() -> bool:
    return random.choice([True, False])

class MaxRetriesExceededError(Exception):
    pass

class Retry:
    def __init__(
        self,
        function: Callable[[], bool],
        max_attempts: int
    ) -> None:
        self.function = function
        self.max_attempts = max_attempts
    
    def __call__(self) -> bool:
        for attempt in range(1, self.max_attempts):
            success = self.function()
            
            if success:
                print(f"Sucess")
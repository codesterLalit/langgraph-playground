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
        for attempt in range(1, self.max_attempts + 1):
            success = self.function()
            
            if success:
                print(f"Sucess on attempt: {attempt}")
                return True
            print(f"Failed on attempt {attempt}")
        raise MaxRetriesExceededError(f"Function failed after {self.max_attempts} attempts")

retry = Retry(fake_test, max_attempts=3)

try:
    retry()
except MaxRetriesExceededError as error:
    print(error)
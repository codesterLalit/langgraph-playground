import random

def fake_test() -> bool:
    return random.choice([True, False])

class MaxRetriesExceededError(Exception):
    """Raised when maximum retry attempts are exhausted."""
    pass

class Retry:
    def __init__(self, func):
        self.func = func
        self.attempt = 0
        self.maximum_attempt = 2
        self.success = False
    
    def __call__(self):
        if self.success == True:
            print("Already succeed")
            return True

        is_success = self.func()
        
        if is_success == True:
            print("Success")
            self.success = True
        elif (is_success == False) and (self.attempt < self.maximum_attempt):
            self.attempt += 1
            print(f"Failed, attempt: {self.attempt}")
        elif self.attempt == self.maximum_attempt:
            raise MaxRetriesExceededError("Sorry! attempt exceeded")

retry = Retry(fake_test)
retry()
retry()
retry()
retry()
            
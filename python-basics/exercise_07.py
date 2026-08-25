from typing import Protocol

class Repository(Protocol):
    def save(self, key:str, value: str) -> None: ...
    def get(self, key:str) -> str: ...

def save_info(repository: Repository, key:str, value:str):
    repository.save(key, value)

def get_info(repository: Repository, key:str):
    return repository.get(key)


class InMemoryRepo:
    def __init__(self) -> None:
         self.store: dict[str, str] = {}
         
    def save(self, key, value):
        self.store[key] = value
    
    def get(self, key:str):
        return self.store.get(key)
    
repository = InMemoryRepo()
save_info(repository, "name", "Batman")
new_value = get_info(repository, "name")
print(f"value: {new_value}")
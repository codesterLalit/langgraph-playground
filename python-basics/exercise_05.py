from dataclasses import dataclass, field
from typing import Any

@dataclass
class Messsage:
    role:str
    content: str
    metadata: dict[str, any] = field(default_factory=dict)
    
    def is_from_user(self) -> bool:
        return self.role == "user"
    

user_message = Messsage("user", "Hello can you please write me a poem?", metadata={'userId': 32})
assistant_message = Messsage(role = "assistant", content="sure I can write")

print(f"is user message: {user_message.is_from_user()}")
print(f"is user message: {assistant_message.is_from_user()}")

print(user_message)
print(assistant_message)
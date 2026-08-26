from pydantic import BaseModel, Field

class UserInput(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=130)

user = UserInput.model_validate({"name": "Ada", "age": 36})
print(user.model_dump())
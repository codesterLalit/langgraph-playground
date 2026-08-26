from pydantic import BaseModel, Field, EmailStr, ValidationError

# class UserInput(BaseModel):
#     name: str = Field(min_length=1)
#     age: int = Field(ge=0, le=130)

# user = UserInput.model_validate({"name": "Ada", "age": 36})
# print(user.model_dump())

class EmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Subject cannot be empty")
    body: str = Field(..., max_length=10_000, description="Body must not exceed 10000 character.")
    recipient: EmailStr = Field(..., description="Must be valid email address." )

try:
    newEmail = EmailRequest.model_validate({"subject": "test", "body": "tesing", "recipient": "laalit@gmail.com"})
    print(newEmail.model_dump())
except ValidationError as error:
    print(error)
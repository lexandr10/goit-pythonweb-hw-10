from pydantic import BaseModel, EmailStr, ConfigDict, Field



class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="Username")
    email: EmailStr

class UserCreateSchema(UserSchema):
    password: str = Field(min_length=6, max_length=20, description="Password")

class UserResponseSchema(UserSchema):
    id: int
    avatar: str | None
    model_config = ConfigDict(from_attributes=True)
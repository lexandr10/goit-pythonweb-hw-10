from pydantic import BaseModel, EmailStr


class RequestEmailSchema(BaseModel):
    email: EmailStr

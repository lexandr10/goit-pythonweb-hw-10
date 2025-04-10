from datetime import date
from typing import Optional

from markdown_it.rules_inline.backticks import regex
from pydantic import BaseModel, EmailStr, ConfigDict, Field

from src.conf.constants import NAME_MAX_LENGTH, NAME_MIN_LENGTH, MAX_PHONE_LENGTH


class ContactSchema(BaseModel):
    first_name: str = Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        description="First name of the contact",
    )
    last_name: str = Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        description="Last name of the contact",
    )
    email: EmailStr = Field(
        description="Email of the contact", min_length=1, max_length=100
    )
    phone: str = Field(
        description="Phone number of the contact",
        min_length=1,
        max_length=MAX_PHONE_LENGTH,
        pattern=r"^\+?\d{7,15}$",
    )
    birthday: date = Field(description="Birthday of the contact")
    additional_data: Optional[str] = Field(
        default=None, description="Additional data of the contact"
    )


class ContactUpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    additional_data: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: Optional[str]

    model_config = ConfigDict(from_attributes=True)

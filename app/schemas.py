import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class GroupCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)


class GroupOut(BaseModel):
    id: int
    name: str
    contacts_count: int


class ContactCheck(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("phone", check_fields=False)
    @classmethod
    def check_phone(cls, value):
        if value is not None and not re.fullmatch(r"\+?[0-9 ()-]{5,20}", value):
            raise ValueError("только цифры, +, пробел, - и скобки")
        return value

    @field_validator("email", check_fields=False)
    @classmethod
    def check_email(cls, value):
        if value is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("неверный формат e-mail")
        return value

    @field_validator("birthday", check_fields=False)
    @classmethod
    def check_birthday(cls, value):
        if value is not None and value > date.today():
            raise ValueError("дата не может быть в будущем")
        return value


class ContactCreate(ContactCheck):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    birthday: date | None = None
    is_favorite: bool = False
    group_id: int | None = None


class ContactUpdate(ContactCheck):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    birthday: date | None = None
    is_favorite: bool | None = None
    group_id: int | None = None


class ContactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    email: str | None
    birthday: date | None
    is_favorite: bool
    group_id: int | None
    created_at: datetime

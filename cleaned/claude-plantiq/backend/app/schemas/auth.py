from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.common import clean_text_field, normalize_phone

USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,32}$")


def _username(v: object) -> str:
    name = str(v or "").strip().lower()
    if not USERNAME_RE.fullmatch(name):
        raise ValueError("Username must be 3–32 characters: letters, numbers, _ or .")
    return name


class RegisterIn(BaseModel):
    full_name: str
    username: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)
    preferred_language: Literal["en", "kn"] = "en"
    accept_terms: bool = False
    remember: bool = True
    device: str | None = Field(default=None, max_length=160)

    @field_validator("full_name", mode="before")
    @classmethod
    def _name(cls, v):
        return clean_text_field(v, min_len=2, max_len=120, label="Full name")

    @field_validator("username", mode="before")
    @classmethod
    def _user(cls, v):
        return _username(v)

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v):
        v = (v or "").strip().lower() if isinstance(v, str) or v is None else v
        return v or None

    @field_validator("phone", mode="before")
    @classmethod
    def _phone(cls, v):
        if v is None or str(v).strip() == "":
            return None
        return normalize_phone(v)

    @model_validator(mode="after")
    def _checks(self):
        if not self.email and not self.phone:
            raise ValueError("Enter a mobile number or an email address.")
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        if not self.accept_terms:
            raise ValueError("Please accept the terms to create an account.")
        return self


class LoginIn(BaseModel):
    identifier: str = Field(min_length=1, max_length=254, description="Username, email or 10-digit phone")
    password: str = Field(min_length=1, max_length=128)
    remember: bool = True
    device: str | None = Field(default=None, max_length=160)

    @model_validator(mode="before")
    @classmethod
    def _compat(cls, data):
        # The original app posted {"username": ..., "password": ...}
        if isinstance(data, dict) and "identifier" not in data and "username" in data:
            data = {**data, "identifier": data["username"]}
        return data


class RefreshIn(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=200)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    preferred_language: str = "en"
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    preferred_language: Literal["en", "kn"] | None = None

    @field_validator("full_name", mode="before")
    @classmethod
    def _name(cls, v):
        return None if v is None else clean_text_field(v, min_len=2, max_len=120, label="Full name")

    @field_validator("email", mode="before")
    @classmethod
    def _email(cls, v):
        if v is None:
            return None
        return str(v).strip().lower() or ""

    @field_validator("phone", mode="before")
    @classmethod
    def _phone(cls, v):
        if v is None:
            return None
        if str(v).strip() == "":
            return ""
        return normalize_phone(v)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)
    confirm_password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def _match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class DeleteAccountIn(BaseModel):
    password: str = Field(min_length=1, max_length=128)


class PasswordStrengthIn(BaseModel):
    password: str = Field(max_length=128)
    username: str | None = None


class PasswordStrengthOut(BaseModel):
    ok: bool
    score: int
    problems: list[str]


class SessionOut(BaseModel):
    id: int
    device: str
    ip: str | None
    created_at: datetime
    last_used_at: datetime
    current: bool


class AvailabilityOut(BaseModel):
    field: str
    available: bool
    reason: str | None = None

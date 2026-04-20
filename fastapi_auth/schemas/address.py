from pydantic import BaseModel
from datetime import date
from typing import Optional


class CreateAddress(BaseModel):
    first_name: str
    last_name: str
    city: str
    state: str
    pincode: int
    phone_number: int
    date_of_birth: Optional[date] = None
    title: str
    address: str
    country: str
    is_default: Optional[bool] = False


class AddressOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    city: str
    state: str
    pincode: int
    phone_number: int
    date_of_birth: Optional[date] = None
    title: str
    address: str
    country: str
    is_default: bool


class UpdateAddress(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: int | None = None
    phone_number: int | None = None
    date_of_birth: str | None = None
    title: str | None = None
    address: str | None = None
    country: str | None = None
    is_default: bool


class DeleteAddress(BaseModel):
    id: int

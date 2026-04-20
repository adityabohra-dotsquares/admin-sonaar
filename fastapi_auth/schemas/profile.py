from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phonenumber: Optional[int] = None
    date_of_birth: Optional[str] | None = None

class ProfileUpdateResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phonenumber: Optional[int] = None
    date_of_birth: Optional[date] | None = None


class DeleteAddress(BaseModel):
    id: int

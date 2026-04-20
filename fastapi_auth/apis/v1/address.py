from fastapi import Depends, APIRouter
from fastapi_auth.utils.token import get_current_user
from accounts.models import User, SavedAddress
from fastapi_auth.schemas.address import (
    CreateAddress,
    UpdateAddress,
    DeleteAddress,
    AddressOut,
)

from datetime import datetime
from fastapi import HTTPException

from typing import List

router = APIRouter()


@router.get("/address", response_model=List[AddressOut])
def GetAddresses(user=Depends(get_current_user)):
    address = SavedAddress.objects.filter(user=user.id)
    return list(address.values())


def update_profile(address: SavedAddress, data: dict):
    for field, value in data.items():
        if value is not None:  # only update non-null values
            setattr(address, field, value)
    address.save()
    return address


@router.put("/address", response_model=AddressOut)
def UpdateAddresses(data: UpdateAddress, user=Depends(get_current_user)):
    address_qs = SavedAddress.objects.filter(user=user, id=data.id)
    if not address_qs.exists():
        raise HTTPException(status_code=404, detail="Address not found")
    address = address_qs.get()
    if data.is_default:
        saved = SavedAddress.objects.filter(user=user, is_default=True).update(
            is_default=False
        )
    print(data)
    update_data = data.dict(exclude_unset=True)
    update_profile(address, update_data)
    return address


@router.post("/address", response_model=AddressOut)
def AddAddresses(data: CreateAddress, user=Depends(get_current_user)):

    if SavedAddress.objects.filter(user=user, title=data.title).exists():
        raise HTTPException(status_code=400, detail="Already Exist with Same Address Type")
    if data.is_default:
        saved = SavedAddress.objects.filter(user=user, is_default=True).update(
            is_default=False
        )
    address = SavedAddress(user=user)


    update_data = data.dict(exclude_unset=True)

    update_profile(address, update_data)
    return address


@router.delete("/address")
def DeleteAddresses(data: DeleteAddress, user=Depends(get_current_user)):
    address = SavedAddress.objects.filter(user=user.id, id=data.id)
    if not address.exists():
        return {"response": "Address Not Found"}
    address = address.get()
    address.delete()
    return {"response": "Deleted Successfully"}

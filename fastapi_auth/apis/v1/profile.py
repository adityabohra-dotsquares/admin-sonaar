from fastapi import Depends, APIRouter
from fastapi_auth.utils.token import get_current_user
from accounts.models import User, SavedAddress
from fastapi_auth.schemas.profile import ProfileUpdate, ProfileUpdateResponse

router = APIRouter()


@router.get("/profile")
def GetProfile(user=Depends(get_current_user)):
    print(User.objects.filter(id=user.id).values(), "USER DETAILS")
    user = User.objects.filter(id=user.id).only("email", "first_name", "last_name")
    if not user.exists():
        return {"response": "User not Found"}
    user = user.get()
    return {
        "response": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phonenumber": user.phonenumber,
            "email": user.email,
            "date_of_birth": user.date_of_birth,
        }
    }


from datetime import datetime


@router.put(
    "/profile",
)
def GetProfile(data: ProfileUpdate, user=Depends(get_current_user)):
    user = User.objects.filter(id=user.id)
    if not user.exists():
        return {"response": "User not Found"}
    user = user.first()
    user.first_name = data.first_name
    user.last_name = data.last_name
    # TODO Add Date of Birth
    print(data.date_of_birth, "************************")
    if data.date_of_birth:  
        user.date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d")
    user.phonenumber = data.phonenumber
    user.save()

    return {
        "response": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phonenumber": user.phonenumber,
            "email": user.email,
            "date_of_birth": datetime.strftime(user.date_of_birth, "%Y-%m-%d") if user.date_of_birth else None,
        }
    }

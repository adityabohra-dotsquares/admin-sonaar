from fastapi import Depends, APIRouter
from fastapi_auth.utils.token import get_current_user
from accounts.models import User, SavedAddress
from fastapi_auth.schemas.profile import ProfileUpdate, ProfileUpdateResponse

router = APIRouter()


# @router.get("/mailing_list")
# def GetProfile(user=Depends(get_current_user)):
#     print(User.objects.filter(id=user.id).values(), "USER DETAILS")
#     user = User.objects.filter(id=user.id).only("email", "first_name", "last_name")
#     if not user.exists():
#         return {"response": "User not Found"}
#     user = user.get()
#     return {
#         "response": {
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "phonenumber": user.phonenumber,
#             "email": user.email,
#             "date_of_birth": user.date_of_birth,
#         }
#     }


# from datetime import datetime

from marketing.models import MailingList
from services.sendgrid import send_email
from asgiref.sync import sync_to_async
import os

@router.post(
    "/mailing-list",
)
async def MailingListAdd(data: dict):
    print(data, "DATA")
    email = data.get('email')
    if not email:
        return {"error": "Email is required"}

    exists = await sync_to_async(MailingList.objects.filter(email=email).exists)()
    if exists:
        return {
            "response": {
                "response": "Already Subscribed",
            }
        }
    
    user = await sync_to_async(MailingList.objects.create)(email=email)
    
    # Send Welcome Email
    subject = "Welcome to Shopper Beats!"
    content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #dc3545; margin: 0;">Shopper Beats</h1>
            </div>
            <h2 style="color: #333;">Welcome to our community!</h2>
            <p style="color: #555; line-height: 1.6;">
                Hi there,
            </p>
            <p style="color: #555; line-height: 1.6;">
                Thank you for subscribing to our mailing list! We're thrilled to have you with us. 
                You'll now be the first to know about our latest products, exclusive deals, and exciting updates.
            </p>
            <p style="color: #555; line-height: 1.6;">
                Stay tuned for some amazing content coming your way soon!
            </p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #888; font-size: 12px;">
                <p>&copy; 2026 Shopper Beats. All rights reserved.</p>
                <p>If you'd like to unsubscribe, please click <a href="#" style="color: #dc3545;">here</a>.</p>
            </div>
        </div>
    """
    
    try:
        from_mail = "noreply@shopperbeats.com"
        print(from_mail, "FROM MAIL")
        await send_email(
            from_mail=from_mail,
            to_mail=email,
            subject=subject,
            content=content
        )
        print("Email Sent Successfully")
    except Exception as e:
        print(f"Error sending welcome email: {e}")
    print("Email Sent or not  Successfully")
    return {
        "response": {
            "email": user.email,
        }
    }

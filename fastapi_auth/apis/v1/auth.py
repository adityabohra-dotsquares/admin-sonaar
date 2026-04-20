from fastapi import APIRouter
from fastapi_auth.service.auth import CreateUser, AuthenticateUser, authenticate_google_user, get_client_ip
from fastapi_auth.schemas.auth import (
    UserSignup,
    UserLogin,
    RefreshToken,
    ForgotPasswordSchema,
    # ResetPasswordConfirmSchema,
    ResetPasswordSchema,
    ChangePassword,
    ResendVerificationSchema,
    GoogleLoginSchema,
)
from fastapi.requests import Request
from fastapi.responses import JSONResponse, Response
from fastapi_auth.utils.token import get_current_user, refresh_access_token
from fastapi import Depends, HTTPException
from fastapi_auth.utils.token import create_token_cookies, create_tokens

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from accounts.models import User, UserToken
from django.contrib.messages.storage.fallback import FallbackStorage
from django.conf import settings
from fastapi_auth.utils.db_utils import sync_db_to_async, db_auto_cleanup


from asgiref.sync import sync_to_async
from allauth.account.forms import ResetPasswordForm
from django.http import HttpRequest

router = APIRouter()



    

# TODO Check Token Validity
class DummyRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self.META = {}


from fastapi import Depends, HTTPException, status


@router.post("/login")
async def Login(request: Request, response: Response, data: UserLogin):
    if not settings.DEBUG:
        res = await verify_recaptcha(data.recaptcha_token)
        if not res:
            return {"response": "ReCaptcha Validation Failed"}
    service = await sync_db_to_async(AuthenticateUser)(request, data, remember_me=data.remember_me)
    from django.utils import timezone
    from datetime import timedelta
    print("----STARTING LOGIN----")

    if data.remember_me:
        access_token = create_token_cookies(
            response,
            service[settings.ACCESS_TOKEN_NAME],
            settings.ACCESS_TOKEN_NAME,
            time=timezone.now() + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
        )
    else:
        access_token = create_token_cookies(
            response, service[settings.ACCESS_TOKEN_NAME], settings.ACCESS_TOKEN_NAME
        )
    refresh_token = create_token_cookies(
        response,
        service[settings.REFRESH_TOKEN_NAME],
        settings.REFRESH_TOKEN_NAME,
        time=60 * 60 * 24 * 20,
    )

    if not service:
        return {"error": "User not exist"}

    return {"response": service}


@router.post("/google-login")
async def google_login(request: Request, response: Response, data: GoogleLoginSchema):
    print("----STARTING GOOGLE LOGIN----")
    service = await authenticate_google_user(request, data.access_token)
    
    from django.utils import timezone
    from datetime import timedelta

    # Default to remember_me=True for social login or just standard expiration
    access_token = create_token_cookies(
        response,
        service[settings.ACCESS_TOKEN_NAME],
        settings.ACCESS_TOKEN_NAME,
        time=timezone.now() + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
    )
    
    refresh_token = create_token_cookies(
        response,
        service[settings.REFRESH_TOKEN_NAME],
        settings.REFRESH_TOKEN_NAME,
        time=60 * 60 * 24 * 20,
    )

    return {"response": service}


import asyncio





@router.post("/signup")
async def signup(data: UserSignup):
    if data.mailing_list == True:
        print("Add Mailing List Functionality")
    print("starting signup")
    # res = await verify_recaptcha(data.recaptcha_token)
    # if not res:
    #     return {"response": "ReCaptcha Validation Failed"}
    service = await CreateUser(data=data)
    print("starting signup")
    if not service:
        return JSONResponse(status_code=503, content={"response": "Failed"})
    # con

    return {"response": "signup working", "data": data}


class DummyRequest(HttpRequest):
    def build_absolute_uri(self, location=None):
        base_url = "http://localhost:8000"  # Change to your real domain
        if location:
            return f"{base_url}{location}"
        return base_url


@router.post("/forgot-password")
@db_auto_cleanup
def forgot_password(data: ForgotPasswordSchema):
    # Create a dummy HttpRequest for Django
    # res = await verify_recaptcha(data.recaptcha_token)
    # if not res:
    #     return {"response": "ReCaptcha Validation Failed"}
    request = DummyRequest()
    # request.META["SERVER_NAME"] = "localhost"
    # request.META["SERVER_PORT"] = "8000"
    # request.META["wsgi.url_scheme"] = "http"
    form = ResetPasswordForm(data={"email": data.email_address})
    if form.is_valid():
        form.save(
            request=request,
            use_https=False,
            domain_override="192.168.9.36:3001",
            email_template_name="account/email/password_reset_key.html",
        )
        return {"message": "Password reset email sent"}
    else:
        raise HTTPException(status_code=400, detail=form.errors)



from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from asgiref.sync import sync_to_async


# class ForgotPasswordSchema(BaseModel):
#     email: str


# @router.post("/forgot-password")
# async def forgot_password(data: ForgotPasswordSchema):
#     factory = APIRequestFactory()
#     request = factory.post(
#         "/password/reset/",
#         {
#             "email": data.email,
#             "domain_override": "192.168.9.36:3001",
#         },
#     )

#     # Use sync_to_async to call DRF view
#     view = PasswordResetView.as_view()
#     response = await sync_to_async(view)(request)

#     if response.status_code != 200:
#         raise HTTPException(status_code=400, detail=response.data)

#     return {"message": "Password reset email sent"}


from django.contrib.auth.tokens import default_token_generator



# @router.post("/reset-password")
# def reset_password(data: ResetPasswordSchema):
#     request = HttpRequest()
#     request.META["SERVER_NAME"] = "localhost"
#     request.META["SERVER_PORT"] = "8000"
#     request.META["wsgi.url_scheme"] = "http"

#     # Step 1: Find the user from the key
#     from allauth.account.models import EmailConfirmationHMAC
#     from allauth.account.forms import ResetPasswordKeyForm

#     # This will raise 404 if invalid
#     try:
#         # confirmation = EmailConfirmationHMAC.from_key(data.key)
#         user = User.objects.get(id=data.key.split("-", 1)[0])
#         print(user,'check',data.key.split("-",1)[1])
#         # if not default_token_generator.check_token(user, data.key.split("-", 1)[1]):
#         #     raise HTTPException(
#         #         status_code=400, detail="Invalid or expired reset token"
#         #     )
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid reset key")


#     form = ResetPasswordKeyForm(
#         user=user,
#         data={
#             "key": data.key,
#             "password1": data.password1,
#             "password2": data.password2,
#         },
#     )
#     if form.is_valid():
#         form.save()
#         return {"message": "Password reset successfully"}
#     else:
#         raise HTTPException(status_code=400, detail=form.errors)
class ResetPasswordSchema(BaseModel):
    uid: str
    token: str
    password1: str
    password2: str


@router.post("/reset-password")
async def reset_password(data: ResetPasswordSchema):
    factory = APIRequestFactory()
    request = factory.post(
        "/password/reset/confirm/",
        {
            "uid": data.uid,
            "token": data.token,
            "new_password1": data.password1,
            "new_password2": data.password2,
        },
    )

    view = PasswordResetConfirmView.as_view()
    response = await sync_to_async(view)(request)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=response.data)
    else:
        return {"response": "Password Reset Success"}


@router.post("/resend-verification-code")
async def resend_verification_code(data: ResendVerificationSchema):
    from fastapi_auth.service.auth import trigger_email_verification
    # from accounts.models import User
    
    try:
        user = await sync_to_async(User.objects.get)(email=data.email)
    except User.DoesNotExist:
         raise HTTPException(status_code=404, detail="User not found")

    from allauth.account.models import EmailAddress
    try:
        email_address = await sync_to_async(EmailAddress.objects.get)(user=user, email=data.email)
        if email_address.verified:
             return {"message": "Email already verified"}
    except EmailAddress.DoesNotExist:
        pass 

    await trigger_email_verification(user)
    return {"message": "Verification email sent"}


@router.get("/verify-email/{key}")
@db_auto_cleanup
def verify_email(key: str, fast_api_request: Request, response: Response):
    # Try HMAC-based confirmation first
    confirmation = EmailConfirmationHMAC.from_key(key)
    print(confirmation, "confirmation")
    if not confirmation:
        # Fallback: DB stored confirmation
        try:
            confirmation = EmailConfirmation.objects.get(key=key.lower())
            print(confirmation, "confirmation")

            if confirmation.email_address.verified:
                return {"message": "Email already verified"}
        except EmailConfirmation.DoesNotExist:
            raise HTTPException(status_code=404, detail="Invalid or expired key")
    if confirmation.sent is None:
        from datetime import datetime
        from django.utils import timezone

        confirmation.sent = timezone.now()
        confirmation.save(update_fields=["sent"])

    get_adapter().add_message = lambda request, level, message, extra_tags="": None
    # Confirm email
    from django.test import RequestFactory

    # Create a RequestFactory request
    factory = RequestFactory()
    request = factory.get("/")
    request.user = confirmation.email_address.user

    # Add session (required for messages)
    from django.contrib.sessions.middleware import SessionMiddleware

    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()

    # Add messages storage
    request._messages = FallbackStorage(request)
    confirmation.confirm(request)

    # Auto Login Logic
    user = confirmation.email_address.user
    from django.utils import timezone
    from datetime import timedelta

    access_token, refresh_token = create_tokens(user, remember_me=True)
    
    token = UserToken.objects.create(
        user=user,
        ip_address=get_client_ip(fast_api_request),
        user_agent=fast_api_request.headers.get("user-agent", ""),
        access_expires_at=timezone.now() + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
        refresh_expires_at=timezone.now() + timedelta(days=7),
        access_token=access_token,
        refresh_token=refresh_token,
    )

    create_token_cookies(
        response,
        access_token,
        settings.ACCESS_TOKEN_NAME,
        time=timezone.now() + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
    )
    
    create_token_cookies(
        response,
        refresh_token,
        settings.REFRESH_TOKEN_NAME,
        time=60 * 60 * 24 * 20,
    )

    return {
        "message": "Email verified successfully!",
        "user": {
            "id": user.id,
            "email": user.email,
        },
        settings.ACCESS_TOKEN_NAME: access_token,
        settings.REFRESH_TOKEN_NAME: refresh_token,
    }


# AUTHENTICATED Views


@router.post("/logout")
@db_auto_cleanup
def logout(request: Request, response: Response, user=Depends(get_current_user)):
    print("Logout")
    token_str = request.access_token
    print(token_str, "Token String")
    token = UserToken.objects.filter(access_token=token_str, is_active=True).first()
    if token:
        token.is_active = False
        token.save()
    response.delete_cookie(settings.ACCESS_TOKEN_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_NAME)

    return {"detail": "Logged out"}


# //TODO cookies secure
@router.post("/refresh-token")
@db_auto_cleanup
def RefreshToken(response: Response, data: RefreshToken):
    # TODO Session Update for multi device update and activity update
    service = refresh_access_token(data.refresh_token)
    if not service:
        return {"error": "User not exist"}
    response.delete_cookie(settings.ACCESS_TOKEN_NAME)
    access_token = create_token_cookies(response, service, settings.ACCESS_TOKEN_NAME)

    return {"response": service}


@router.get("/details")
@db_auto_cleanup
def UserDetails(data: UserLogin, user=Depends(get_current_user)):
    return {"tesst": "passed"}
    # service = AuthenticateUser(data)
    # if not service:
    #     return {"error": "User not exist"}
    # return {"response": service}


@router.get("/sessions")
@db_auto_cleanup
def list_sessions(user=Depends(get_current_user)):
    tokens = user.tokens.filter(is_active=True)
    return [
        {
            "access_token": t.access_token,
            "refresh_token": t.refresh_token,
            "ip_address": t.ip_address,
            "user_agent": t.user_agent,
            "created_at": t.created_at,
            "last_activity": t.last_activity,
            "access_expires_at": t.access_expires_at,
            "refresh_expires_at": t.refresh_expires_at,
        }
        for t in tokens
    ]


@router.get("/secure_page")
@db_auto_cleanup
def secure_page(user=Depends(get_current_user)):
    return {"response": "You are authenticated"}


async def verify_recaptcha(token: str):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": settings.RECAPTCHA_SECRET, "response": token}
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
        result = response.json()
        print(result)
        # result['success'] is True if verified
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")
        return True


@router.get("/verify_recaptcha/{key}")
async def test_recaptcha(key: str):
    print("Captcha token------", key)

    respo = await verify_recaptcha(key)
    print("Captcha token------", key, respo)
    return {"response": key}


@router.post("/change-password")
@db_auto_cleanup
def change_password(
    response: Response,
    data: ChangePassword,
    user=Depends(get_current_user),
):
    print(user)
    if not user.check_password(data.current_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # Set new password
    user.set_password(data.new_password)
    user.save()
    # TODO INVALIDATE YOUR ALL SESSIONS HERE
    invalidate_all_sessions(user, response)
    return {"detail": "Password changed successfully"}


def invalidate_all_sessions(user, response):
    userToken = UserToken.objects.filter(user=user, is_active=True)
    if userToken.exists():
        userToken.delete()
    response.delete_cookie(settings.ACCESS_TOKEN_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_NAME)

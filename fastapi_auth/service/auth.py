from accounts.models import User, UserToken
from allauth.account.adapter import get_adapter
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from fastapi import HTTPException
from fastapi_auth.utils.token import create_tokens
from django.contrib.auth.hashers import check_password
from fastapi.requests import Request
from services.sendgrid import send_email
from allauth.account.models import EmailAddress, EmailConfirmation, EmailAddress
import os
from dotenv import load_dotenv
from fastapi_auth.utils.db_utils import db_auto_cleanup, sync_db_to_async

load_dotenv()


class DummyRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self.META = {}

    def build_absolute_uri(self, location=None):
        base_url = "http://localhost:8000"
        if location and "accounts/confirm-email" in location:
            key = location.rstrip("/").split("/")[-1]
            location = f"/verify-email/{key}"
        if not location:
            return base_url
        if location.startswith("http"):
            return location
        return f"{base_url.rstrip('/')}/{location.lstrip('/')}"

    def get_host(self):
        return "localhost:8000"


# def trigger_email_verification(user):
#     request = DummyRequest(user)
#     try:
#         email_address = EmailAddress.objects.get(user=user, primary=True)
#     except EmailAddress.DoesNotExist:
#         raise Exception("No primary email found for user")
#     confirmation = EmailConfirmation.create(email_address)
#     adapter = get_adapter(user)
#     adapter.send_confirmation_mail(request, confirmation, signup=True)
#     # email_address.send_confirmation(request)


def confirm_email(user, email):
    email_obj = EmailAddress.objects.get(user=user, email=email)
    email_obj.verified = True
    email_obj.save()


class DummySession(dict):
    def __getitem__(self, key):
        return super().get(key, None)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)


import asyncio

# def CreateUser(data):
#     if User.objects.filter(email=data.email).exists():
#         raise HTTPException(status_code=400, detail="Email already registered")
#     user = User.objects.create_user(
#         email=data.email,
#         password=data.password,
#     )
#     user_instance = User.objects.get(email=data.email)
#     EmailAddress.objects.create(
#         user=user_instance, email=user_instance.email, primary=True, verified=False
#     )

#     trigger_email_verification(user_instance)

#     # Complete signup (sets email verification, etc.)
#     # TODO do custom email verification system using All auth
#     return user


# async def trigger_email_verification(user):
#     from django.apps import apps

#     # Get EmailAddress object
#     EmailAddress = apps.get_model("account", "EmailAddress")
#     email_address = await asyncio.to_thread(
#         EmailAddress.objects.get, user=user, primary=True
#     )

#     # Generate confirmation token
#     EmailConfirmation = apps.get_model("account", "EmailConfirmation")
#     confirmation = await asyncio.to_thread(EmailConfirmation.create, email_address)

#     # Build verification URL
#     verify_url = f"https://shopper-beats-frontend-877627218975.australia-southeast2.run.app/verify-email?key={confirmation.key}"

#     subject = "Verify your email"
#     content = f"""
#         <p>Hello {user.email},</p>
#         <p>Thank you for signing up. Please verify your email by clicking the link below:</p>
#         <p><a href="{verify_url}" style="color: #4f46e5; font-weight: bold;">
#             Verify Email
#         </a></p>
#         <br/>
#         <p>If you did not create an account, you can ignore this email.</p>
#     """

#     # Send email using your SendGrid function

#     from_mail = os.getenv("DEFAULT_FROM_EMAIL", "noreply@shopperbeats.com")
#     print("this is mail", from_mail)
#     response = await send_email(
#         from_mail="noreply@shopperbeats.com",
#         to_mail=user.email,
#         subject=subject,
#         content=content,
#     )
#     print(response,"******************")

#     return response




# LASTONE
import asyncio
import os
from django.apps import apps
from allauth.account.adapter import get_adapter

async def trigger_email_verification(user):
    adapter = get_adapter()  # Your DatabaseEmailAdapter

    EmailAddress = apps.get_model("account", "EmailAddress")
    EmailConfirmation = apps.get_model("account", "EmailConfirmation")

    try:
        email_address = await asyncio.to_thread(
            EmailAddress.objects.select_related("user").get,
            user=user,
            primary=True,
        )
    except EmailAddress.DoesNotExist:
        email_address = await asyncio.to_thread(
            EmailAddress.objects.create,
            user=user,
            email=user.email,
            primary=True,
            verified=False,
        )

    # Create confirmation
    confirmation = await asyncio.to_thread(EmailConfirmation.create, email_address)
    await asyncio.to_thread(confirmation.save)

    frontend_url ="https://shopperbeats.com.au"
    verify_url = f"{frontend_url}/verify-email?key={confirmation.key}"

    # Optional: update the activate_url in context if needed (allauth uses this var in templates)
    # But we don't need to override context — allauth builds it internally using the confirmation.key

    # CORRECT CALL: positional args
    await asyncio.to_thread(
        adapter.send_confirmation_mail,
        None,              # request — can be None
        confirmation,      # email_confirmation — positional!
        signup=True        # keyword is fine
    )

    print(f"Verification email sent via allauth adapter to {user.email}")
    return {"success": True, "key": confirmation.key}








# import os
# from django.apps import apps
# from allauth.account.adapter import get_adapter
# from allauth.account import app_settings

# async def trigger_email_verification(user):
#     """
#     Sends email verification using allauth's system (goes through your DatabaseEmailAdapter)
#     Supports async context and uses DB templates.
#     """
#     # Get the adapter (which is your DatabaseEmailAdapter)
#     adapter = get_adapter()

#     # Get or create the primary EmailAddress
#     EmailAddress = apps.get_model("account", "EmailAddress")
#     try:
#         email_address = await asyncio.to_thread(
#             EmailAddress.objects.get, user=user, primary=True
#         )
#     except EmailAddress.DoesNotExist:
#         # Create it if missing (shouldn't happen, but safe)
#         email_address = await asyncio.to_thread(
#             EmailAddress.objects.create,
#             user=user,
#             email=user.email,
#             primary=True,
#             verified=False,
#         )

#     # Create confirmation object (generates key)
#     EmailConfirmation = apps.get_model("account", "EmailConfirmation")
#     confirmation = await asyncio.to_thread(EmailConfirmation.create, email_address)

#     # Save it to DB
#     await asyncio.to_thread(confirmation.save)

#     # Build context exactly like allauth does
#     # context = {
#     #     "user": user,
#     #     "activate_url": f"https://shopper-beats-frontend-877627218975.australia-southeast2.run.app/verify-email?key={confirmation.key}",
#     #     "current_site": app_settings.SITES_FALLBACK,  # or your custom site
#     #     "key": confirmation.key,
#     #     "email": user.email,
#     # }

#     # This will use your DatabaseEmailAdapter.send_mail() → pulls from DB template!
#     await asyncio.to_thread(
#         adapter.send_confirmation_mail,
#         request=None,  # request is optional for email sending
#         email_confirmation=confirmation,
#         signup=True,  # tells allauth it's a signup confirmation
#     )

#     # Optional: log or return success
#     print(f"Verification email triggered for {user.email} with key {confirmation.key}")
#     return {"success": True, "key": confirmation.key}







from asgiref.sync import sync_to_async

async def CreateUser(data):
    print("CREATING USER", data.email)

    if await sync_db_to_async(User.objects.filter(email=data.email).exists)():
        user = await sync_db_to_async(User.objects.get)(email=data.email)
        # Check if user has any verified email address
        is_verified = await sync_db_to_async(EmailAddress.objects.filter(user=user, verified=True).exists)()
        
        if not is_verified:
            raise HTTPException(status_code=400, detail="User Email Not Verified")
        raise HTTPException(status_code=400, detail="User is already registered")

    user = await sync_db_to_async(User.objects.create_user)(
        email=data.email,
        password=data.password,
    )
    print("CREATING USER", data.email)

    await sync_db_to_async(EmailAddress.objects.create)(
        user=user,
        email=user.email,
        primary=True,
        verified=False,
    )

    await trigger_email_verification(user)
    return user


from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from fastapi import status


def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host


@db_auto_cleanup
def AuthenticateUser(request, data, remember_me):
    if not User.objects.filter(email=data.email).exists():
        raise HTTPException(status_code=400, detail="No record found")
    # Check if blocked

    user = User.objects.get(email=data.email)
    email_verified = EmailAddress.objects.filter(user=user, verified=True)
    if not email_verified.exists():
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail="User Email Not Verified ",
        )

    if user.is_blocked and user.blocked_until and user.blocked_until > timezone.now():
        raise HTTPException(
            status_code=403,
            detail=f"Account blocked. Try again at {user.blocked_until}",
        )

    if not check_password(data.password, user.password):
        user.failed_login_attempts += 1
        user.last_failed_login = timezone.now()
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.is_blocked = True
            user.blocked_until = timezone.now() + settings.BLOCK_DURATION
            # Send email notification
            subject="Account Blocked"
            content=f"Your account has been blocked due to {settings.MAX_FAILED_LOGIN_ATTEMPTS} failed login attempts.You can try logging in again after {settings.BLOCK_DURATION}."
            try:
                response = send_email(
                    from_mail="noreply@shopperbeats.com",
                    to_mail=user.email,
                    subject=subject,
                    content=content,
                )
                print("SENT the EMAIL",response)
                # send_mail(

                #     from_email=settings.DEFAULT_FROM_EMAIL,
                #     recipient_list=[user.email],
                # )
            except:
                print("ERRROR Sending Mail")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error sending Mail")
        user.save()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # For User Login In Multiple Devices
    access_token, refresh_token = create_tokens(user, remember_me)
    token = UserToken.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
        access_expires_at=timezone.now()
        + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
        refresh_expires_at=timezone.now() + timedelta(days=7),
        access_token=access_token,
        refresh_token=refresh_token,
    )
    # Successful login
    user.failed_login_attempts = 0
    user.is_blocked = False
    user.blocked_until = None
    user.save()

    return {
        "user": {
            "id": user.id,
            "email": user.email,
        },
        settings.ACCESS_TOKEN_NAME: access_token,
        settings.REFRESH_TOKEN_NAME: refresh_token,
    }


async def authenticate_google_user(request, access_token):
    if not access_token or not access_token.strip():
        raise HTTPException(status_code=400, detail="Invalid Google Token: Token is empty")

    import httpx
    # 1. Verify the token with Google
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Google Token")
        
        user_info = response.json()
    
    email = user_info.get("email")
    google_id = user_info.get("sub")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    # 2. Check for SocialAccount
    from allauth.socialaccount.models import SocialAccount
    
    try:
        social_account = await sync_db_to_async(SocialAccount.objects.get)(
            provider="google", uid=google_id
        )
        user = await sync_db_to_async(lambda: social_account.user)()
    except SocialAccount.DoesNotExist:
        # 3. Check for existing User
        try:
            user = await sync_db_to_async(User.objects.get)(email=email)
        except User.DoesNotExist:
            # 4. Create new User
            user = await sync_db_to_async(User.objects.create_user)(
                email=email,
                password=None, # Unusable password
            )
            # Create EmailAddress as verified
            await sync_db_to_async(EmailAddress.objects.create)(
                user=user,
                email=email,
                primary=True,
                verified=True
            )
        
        # 5. Link SocialAccount
        await sync_db_to_async(SocialAccount.objects.create)(
            user=user,
            provider="google",
            uid=google_id,
            extra_data=user_info
        )

    # 6. Generate Tokens (Ensure user is active/not blocked)
    if user.is_blocked and user.blocked_until and user.blocked_until > timezone.now():
        raise HTTPException(
            status_code=403,
            detail=f"Account blocked. Try again at {user.blocked_until}",
        )

    # Logic from AuthenticateUser regarding tokens
    access_token_str, refresh_token_str = create_tokens(user, remember_me=True)
    
    await sync_to_async(UserToken.objects.create)(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
        access_expires_at=timezone.now()
        + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
        refresh_expires_at=timezone.now() + timedelta(days=7),
        access_token=access_token_str,
        refresh_token=refresh_token_str,
    )
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
        },
        settings.ACCESS_TOKEN_NAME: access_token_str,
        settings.REFRESH_TOKEN_NAME: refresh_token_str,
    }

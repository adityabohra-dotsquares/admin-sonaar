import jwt
import datetime
from fastapi import HTTPException
from fastapi.responses import Response
from fastapi.requests import Request
from django.contrib.auth.models import User
from django.conf import settings
from accounts.models import UserToken
from django.utils import timezone
from allauth.account.models import EmailConfirmation, EmailAddress

# Secret key from Django settings
JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"
from datetime import timedelta,datetime
import calendar

import json
import uuid

# class UUIDEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, uuid.UUID):
#             return str(obj)
#         return super().default(obj)

def convert_uuid_to_str(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_uuid_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_uuid_to_str(i) for i in obj]
    return obj
def access_token_helper(user, add_time=0):
    print(JWT_SECRET)
    from datetime import timedelta,datetime

    iat = timezone.now()
    print(iat,"IAT@@@@@@@@@@@@@@@@@@@@@@")
    exp = iat + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME)
    # Access token
    print(iat,exp)

    access_payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": int(iat.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access",
    }
    access_payload = convert_uuid_to_str(access_payload)
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return access_token


def refresh_token_helper(user, add_time=0):
    try:
        # Refresh token
        refresh_payload = {
            "user_id": user.id,
            "exp": datetime.utcnow()
            + timedelta(days=settings.REFRESH_TOKEN_LIFETIME + add_time),
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        refresh_payload = convert_uuid_to_str(refresh_payload)
        refresh_token = jwt.encode(
            refresh_payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )
        return refresh_token
    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token expired")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Invalid token: {e}")


def create_tokens(user, remember_me):
    if remember_me:
        return access_token_helper(user, add_time=100), refresh_token_helper(user)

    return access_token_helper(user), refresh_token_helper(user)


def refresh_access_token(refresh_token):
    """Verify refresh token and create a new access token."""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("Invalid token type")

        # Here you would normally fetch the user from DB using payload['user_id']
        user_id = payload["user_id"]
        email = payload.get("email", "")  # optional if stored in refresh token

        # Create a new access token
        now = datetime.datetime.utcnow()
        new_access_payload = {
            "user_id": user_id,
            "email": email,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
            "iat": now,
            "type": "access",
        }
        new_access_token = jwt.encode(
            new_access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM
        )
        user = User.objects.filter(id=user_id)
        if not user.exists():
            raise Exception("User Doesn't Exist")
        return new_access_token

    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token expired")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Invalid token: {e}")


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

# Use FastAPI's HTTPBearer scheme
auth_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    print(request.cookies, "current_user")
    token = None
    cookie_token = request.cookies.get(settings.ACCESS_TOKEN_NAME)
    print(cookie_token)
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            token = cookie_token[len("Bearer ") :]
        else:
            cookie_token = token
    else:
        token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(status_code=401, detail="Not Token to verify user")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = payload.get("user_id")
        user = None
        from django.db import close_old_connections
        from django.db.utils import OperationalError
        try:
            user = User.objects.get(id=user_id)
        except OperationalError:
            print("REPAIRING CLOSING OLD CONNECTIONS")
            close_old_connections()  # Closes stale connections
            user = User.objects.get(id=user_id)  # Retry


        token_str = token
        print("TOKEN ", token)

        try:
            token = UserToken.objects.get(access_token=token_str, is_active=True)
        except UserToken.DoesNotExist:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Check expiration
        print(token.access_expires_at, timezone.now(), "CHECKUP HERE")
        if token.access_expires_at < timezone.now():
            token.is_active = False
            token.save()
            raise HTTPException(status_code=401, detail="Access token expired")

        # Update last activity
        token.last_activity = timezone.now()
        token.save()
        print("TOKEN SAVED")
        request.access_token = token_str
        email_verified = EmailAddress.objects.filter(user=user, verified=True)
        if not email_verified.exists():
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail="User Email Not Verified ",
            )

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )


def create_token_cookies(response: Response, token, token_name, time=0):
    from datetime import timedelta

    response.set_cookie(
        key=token_name,
        value=f"Bearer {token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_LIFETIME * 60,
        expires=timezone.now() + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
        secure=False,
        samesite="lax",
    )

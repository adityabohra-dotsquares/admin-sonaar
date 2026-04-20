import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = "HS256"


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints
        if request.url.path in ["/login", "/signup", "/refresh", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

        token = auth_header.split(" ")[1]

        try:
            # Decode JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")

            # Attach user to request.state
            user = User.objects.get(id=payload["user_id"])
            request.state.user = user

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except User.DoesNotExist:
            raise HTTPException(status_code=401, detail="User not found")

        return await call_next(request)



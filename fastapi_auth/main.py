from fastapi import FastAPI
import os
import django
from fastapi.staticfiles import StaticFiles

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop.settings")
django.setup()
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()
# Always import after setup
from .apis.v1.auth import router as authRouter
from .apis.v1.address import router as AddressRouter
from .apis.v1.profile import router as ProfileRouter
from .apis.v1.marketing import router as MarketingRouter
from .apis.v1.menu import router as MenuRouter
from .apis.v1.social_media import router as SocialMediaRouter

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_auth.AuditMiddleware import AuditIOMiddleware


from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Scope, Receive, Send

ADMIN_DOMAIN = "admin-uat.shopperbeats.com.au"


class SilentRequestAbortedMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        try:
            await self.app(scope, receive, send)
        except RequestAborted:
            # Silently ignore client disconnect after response
            pass
        except Exception as e:
            # Re-raise other exceptions
            raise e


class AdminDomainMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            host = headers.get(b"host", b"").decode().split(":")[0]

            # If admin domain is hit
            if host == ADMIN_DOMAIN:
                await django_asgi_app(scope, receive, send)
                return
                path = scope.get("path", "")

                # # Redirect root `/` → `/admin`
                # if path == "/" or path == "":
                #     response = RedirectResponse(url="/admin", status_code=302)
                #     await response(scope, receive, send)
                #     return

                # # Let Django handle /admin/*
                # if path.startswith("/admin"):
                #     await django_asgi_app(scope, receive, send)
                #     return

        # Otherwise continue FastAPI
        await self.app(scope, receive, send)


fastapi_app = FastAPI(title="Customer AUTH API")

import os

SERVER_MODE = os.getenv("SERVER_MODE", "production")

if SERVER_MODE == "development":
    fastapi_app.mount("/_django", SilentRequestAbortedMiddleware(django_asgi_app))
    fastapi_app.mount("/static", StaticFiles(directory="staticfiles"), name="static")

app = AdminDomainMiddleware(fastapi_app)
fastapi_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


from django.db import close_old_connections


class DjangoDBMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            await self.app(scope, receive, send)
        finally:
            close_old_connections()


fastapi_app.add_middleware(DjangoDBMiddleware)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORSFASTAPI", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(AuditIOMiddleware)


@fastapi_app.get("/health-check")
def healthCheck():
    return {"response": "System Working Properly"}


from .apis.v1.faq import router as FAQRouter

fastapi_app.include_router(authRouter, prefix="/api/v1/users", tags=["auth"])
fastapi_app.include_router(AddressRouter, prefix="/api/v1/users", tags=["address"])
fastapi_app.include_router(ProfileRouter, prefix="/api/v1/users", tags=["address"])
fastapi_app.include_router(
    MarketingRouter, prefix="/api/v1/marketing", tags=["marketing"]
)
fastapi_app.include_router(MenuRouter, prefix="/api/v1/menu", tags=["menu"])
fastapi_app.include_router(
    SocialMediaRouter, prefix="/api/v1/social-media", tags=["social-media"]
)
fastapi_app.include_router(FAQRouter, prefix="/api/v1/faqs", tags=["faqs"])

from django.core.exceptions import RequestAborted
from starlette.types import ASGIApp, Receive, Scope, Send

# Apply it when mounting
# fastapi_app.mount("/admin", SilentRequestAbortedMiddleware(django_asgi_app))
# app.mount("/", django_asgi_app)

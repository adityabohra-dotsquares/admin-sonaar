# app/middleware/audit_io.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_auth.utils.logger import audit_log
import json


class AuditIOMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        # Read request body
        body_bytes = await request.body()
        try:
            body = await request.json()
        except Exception:
            body = body_bytes.decode("utf-8")

        # Call the endpoint
        response = await call_next(request)

        # Capture response body
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk

        # Reset response body for client using async generator
        async def resp_gen():
            yield resp_body

        response.body_iterator = resp_gen()

        # Parse response JSON safely
        try:
            resp_data = json.loads(resp_body)
        except Exception:
            resp_data = resp_body.decode("utf-8")

        # Log audit
        user_id = getattr(request.state, "user_id", None)
        audit_log(
            user_id=user_id,
            action=f"{request.method} {request.url.path}",
            object_type="APIRequest",
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            changes={"input": body, "output": resp_data},
            status="success" if response.status_code < 400 else "failed",
        )

        return response

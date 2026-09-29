from fastapi import Header, HTTPException
from app.config import settings


def get_current_tenant(
    authorization: str = Header(default=""),
    x_tenant_id: str = Header(default=""),
    x_user_email: str = Header(default="demo@example.com"),
) -> dict:
    """
    Local dev mode: accept `X-Tenant-Id` header directly.
    Phase 2: validate Cognito JWT and extract `custom:tenant_id` claim.
    """
    if settings.AUTH_MODE == "local":
        if not x_tenant_id:
            raise HTTPException(status_code=401, detail="X-Tenant-Id header required in local mode")
        return {"tenant_id": x_tenant_id, "email": x_user_email}

    # Phase 2: Cognito verification placeholder
    raise HTTPException(status_code=501, detail="Cognito auth not implemented in Phase 1")
from fastapi import Depends, HTTPException
from middlewares.jwt import verify_jwt


def require_roles(allowed_roles: list[str]):
    async def role_checker(payload: dict = Depends(verify_jwt)):
        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied: role not permitted")
    return role_checker
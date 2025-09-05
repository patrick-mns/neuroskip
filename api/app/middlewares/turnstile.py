from core.config import settings
import httpx
from fastapi import HTTPException, Request, Query

async def verify_turnstile(request: Request, id: str, session: str, type: str, turnstile_token: str = Query(None)):
    
    if settings.development: 
        return True

    turnstile_token = turnstile_token or request.headers.get("cf-turnstile-response")
    if not turnstile_token:
        raise HTTPException(status_code=400, detail="Turnstile token not provided")

    client_ip = request.client.host if request.client else None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": settings.turnstile_secret_key, "response": turnstile_token, "remoteip": client_ip},
        )
        result = response.json()

    if not result.get("success"):
        raise HTTPException(status_code=403, detail="Turnstile failed verification")
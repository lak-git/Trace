from fastapi import Header, HTTPException, status

from app.core.config import Settings, get_settings


async def verify_webhook_secret(
    x_agent_secret: str = Header(..., alias="X-Agent-Secret"),
) -> None:
    settings: Settings = get_settings()
    if x_agent_secret != settings.AGENT_N8N_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

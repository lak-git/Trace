from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from supabase import AsyncClient, create_async_client

from app.core.config import Settings


async def init_supabase(settings: Settings) -> AsyncClient:
    return await create_async_client(
        str(settings.SUPABASE_URL),
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def get_supabase(request: Request) -> AsyncClient:
    client = getattr(request.app.state, "supabase", None)
    if client is None:
        raise RuntimeError("Supabase client has not been initialised")
    return client


@asynccontextmanager
async def supabase_lifespan(app: FastAPI, settings: Settings) -> AsyncIterator[None]:
    app.state.supabase = await init_supabase(settings)
    yield

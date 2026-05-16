from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import blocker, context, health, memory, participant, plane
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.database import supabase_lifespan


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    async with supabase_lifespan(app, settings):
        yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Agentic Scrum Assistant API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api")
    app.include_router(participant.router, prefix="/api")
    app.include_router(context.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")
    app.include_router(plane.router, prefix="/api")
    app.include_router(blocker.router, prefix="/api")
    return app


app = create_app()

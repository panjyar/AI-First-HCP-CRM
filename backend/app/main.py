from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat_router, resources_router
from app.config import get_settings
from app.database.init_db import close_db, init_db
from app.tools import CRM_TOOLS


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix=settings.api_prefix)
app.include_router(resources_router, prefix=settings.api_prefix)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get(f"{settings.api_prefix}/tools", tags=["System"])
async def list_agent_tools() -> dict[str, list[dict[str, str]]]:
    return {
        "tools": [
            {
                "name": crm_tool.name,
                "description": crm_tool.description,
            }
            for crm_tool in CRM_TOOLS
        ]
    }

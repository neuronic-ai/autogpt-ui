from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> "FastAPI":
    from prisma import Prisma

    from app.api.v1 import api
    from app.core import settings

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        prisma = Prisma(auto_register=True)
        await prisma.connect()
        yield
        await prisma.disconnect()

    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.BASE_URL}/openapi.json",
        version=settings.VERSION,
        redoc_url=f"{settings.BASE_URL}/redoc",
        docs_url=f"{settings.BASE_URL}/docs",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api.router, prefix=settings.API_V1_STR)

    return app

from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database.db import session_manager
from src.routers import contacts_routes, user_routes, auth_routes

scheduler = AsyncIOScheduler()


async def cleanup_expired_tokens():
    async with session_manager() as session:
        time_now = datetime.now(timezone.utc)
        cutoff = time_now - timedelta(days=7)
        stmt = text(
            "DELETE FROM refresh_tokens WHERE expired_at < :time_now OR revoked_at IS NOT NULL AND revoked_at < :cutoff"
        )
        await session.execute(stmt, {"time_now": time_now, "cutoff": cutoff})
        await session.commit()
        print(f"Cleaned up expired tokens [{time_now.strftime('%Y-%m-%d %H:%M:%S')}]")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(cleanup_expired_tokens, "interval", hours=1)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="Contacts API",
    description="API for managing contacts",
    version="0.1.0",
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")


@app.get("/")
async def read_root():
    return {"Welcome to FastAPI"}

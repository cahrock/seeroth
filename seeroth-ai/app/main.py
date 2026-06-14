"""
SeeRoth AI Service — FastAPI entry point
Layer 10: Data Feed + Layer 12: AI Advisory
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints import macro, market, fundamentals


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    from app.services.macro.fred_client import fred_client
    await fred_client.close()


app = FastAPI(
    title="SeeRoth AI Service",
    description="Halal Investment Platform — AI Advisory & Data Feed",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "seeroth-ai", "version": "1.0.0"}


# ── L10 Data Feed Routers ──────────────────────────────────────
app.include_router(
    macro.router,
    prefix="/api/v1/macro",
    tags=["L10 Macro Data (FRED)"]
)
app.include_router(
    market.router,
    prefix="/api/v1/market",
    tags=["L10 Market Data (Polygon.io)"]
)
app.include_router(
    fundamentals.router,
    prefix="/api/v1/fundamentals",
    tags=["L10 Fundamentals (FMP)"]
)

# ── Coming soon ───────────────────────────────────────────────
# app.include_router(screening.router, prefix="/api/v1/screening", tags=["L1-L3 Screening"])
# app.include_router(advisory.router,  prefix="/api/v1/advisory",  tags=["L12 AI Advisory"])
# app.include_router(zakat.router,     prefix="/api/v1/zakat",     tags=["L6 Zakat"])
# app.include_router(decision.router,  prefix="/api/v1/decision",  tags=["L11 Decision Engine"])

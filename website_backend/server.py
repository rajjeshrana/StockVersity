from __future__ import annotations

import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from market_engine import MarketEngine

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("stockversity-web")

engine = MarketEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await engine.start()
    try:
        yield
    finally:
        await engine.stop()


app = FastAPI(
    title="StockVersity Independent Market API",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS",
        "https://stockversity.in,https://www.stockversity.in",
    ).split(",")
    if item.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return engine.health()


@app.get("/api/market")
async def market():
    return engine.payload()


@app.get("/")
async def root():
    return {
        "ok": True,
        "service": "StockVersity Independent Market API",
        "version": "1.0.0",
        "endpoints": ["/api/health", "/api/market"],
    }




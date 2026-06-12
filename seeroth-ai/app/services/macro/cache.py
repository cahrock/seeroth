"""
L10 — Macro data caching layer
Redis TTL: 15 menit untuk snapshot (data FRED update harian, tidak perlu lebih sering)
PostgreSQL: Persistent storage untuk historical tracking
"""

import json
import logging
from datetime import datetime
from typing import Optional

from app.models.macro import MacroSnapshot
from app.services.macro.fred_client import fred_client

logger = logging.getLogger(__name__)

CACHE_KEY_SNAPSHOT = "macro:snapshot:latest"
CACHE_TTL_SECONDS = 900  # 15 menit


async def get_macro_snapshot(redis_client=None) -> MacroSnapshot:
    """
    Get macro snapshot dengan caching:
    1. Cek Redis cache dulu
    2. Kalau miss atau expired → fetch dari FRED
    3. Simpan ke Redis dengan TTL 15 menit
    """

    # ── Try Redis cache ──────────────────────────────────────
    if redis_client:
        try:
            cached = await redis_client.get(CACHE_KEY_SNAPSHOT)
            if cached:
                data = json.loads(cached)
                logger.debug("Macro snapshot served from Redis cache")
                return MacroSnapshot(**data)
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e} — fetching from FRED")

    # ── Cache miss — fetch from FRED ─────────────────────────
    snapshot = await fred_client.fetch_macro_snapshot()

    # ── Store in Redis ───────────────────────────────────────
    if redis_client and snapshot:
        try:
            # Serialize dates to string for JSON
            snapshot_dict = snapshot.model_dump()
            for key, val in snapshot_dict.items():
                if hasattr(val, "isoformat"):
                    snapshot_dict[key] = val.isoformat()

            await redis_client.setex(
                CACHE_KEY_SNAPSHOT,
                CACHE_TTL_SECONDS,
                json.dumps(snapshot_dict),
            )
            logger.debug(f"Macro snapshot cached in Redis (TTL: {CACHE_TTL_SECONDS}s)")
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")

    return snapshot

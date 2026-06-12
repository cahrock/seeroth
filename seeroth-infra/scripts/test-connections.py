"""
test-connections.py
Test PostgreSQL (asyncpg) and Redis connectivity
Run: python seeroth-infra/scripts/test-connections.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv("seeroth-infra/envs/.env.local")

DATABASE_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


async def test_postgres():
    print("1. Testing PostgreSQL (asyncpg)...")
    try:
        import asyncpg
        # Convert jdbc URL to asyncpg format if needed
        url = DATABASE_URL.replace("jdbc:postgresql://", "postgresql://")
        url = url.split("?")[0]  # strip query params
        conn = await asyncpg.connect(url)
        version = await conn.fetchval("SELECT version()")
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        )
        await conn.close()
        print(f"   ✅ PostgreSQL connected")
        print(f"   → {version[:50]}...")
        for t in tables:
            print(f"   → table: {t['tablename']}")
    except Exception as e:
        print(f"   ❌ PostgreSQL FAILED: {e}")


async def test_redis():
    print("\n2. Testing Redis...")
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(REDIS_URL)
        pong = await r.ping()
        info = await r.info("server")
        await r.aclose()
        print(f"   ✅ Redis connected — PING: {pong}")
        print(f"   → redis_version: {info.get('redis_version')}")
    except Exception as e:
        print(f"   ❌ Redis FAILED: {e}")


async def main():
    print("=== SeeRoth Connection Test (Python) ===\n")
    await test_postgres()
    await test_redis()
    print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())

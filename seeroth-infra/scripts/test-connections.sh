#!/bin/bash
# ============================================================
# test-connections.sh
# Test PostgreSQL and Redis connectivity from local
# Usage: ./test-connections.sh
# ============================================================

set -e

# Load from .env.local if exists
if [ -f "seeroth-infra/envs/.env.local" ]; then
  export $(cat seeroth-infra/envs/.env.local | grep -v '^#' | xargs)
fi

echo "=== SeeRoth Connection Test ==="
echo ""

# ── Test PostgreSQL ──────────────────────────────────────────
echo "1. Testing PostgreSQL..."
if psql "$DATABASE_URL" -c "SELECT version();" > /dev/null 2>&1; then
  echo "   ✅ PostgreSQL connected"
  psql "$DATABASE_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;" \
    | grep -v "^--" | grep -v "rows)" | sed 's/^/   → /'
else
  echo "   ❌ PostgreSQL connection FAILED"
  echo "   Check DATABASE_URL in .env.local"
fi

echo ""

# ── Test Redis ───────────────────────────────────────────────
echo "2. Testing Redis..."
REDIS_HOST=$(echo $REDIS_URL | sed 's|redis://||' | cut -d':' -f1)
REDIS_PORT=$(echo $REDIS_URL | sed 's|redis://||' | cut -d':' -f2 | cut -d'/' -f1)

if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q "PONG"; then
  echo "   ✅ Redis connected"
  redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO server | grep "redis_version" | sed 's/^/   → /'
else
  echo "   ❌ Redis connection FAILED"
  echo "   Check REDIS_URL in .env.local"
fi

echo ""
echo "=== Done ==="

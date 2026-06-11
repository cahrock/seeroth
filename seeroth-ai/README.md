# seeroth-ai — Python FastAPI AI & Data Service

## Structure
```
app/
  main.py                     # FastAPI app entry point + lifespan
  api/
    v1/
      endpoints/
        advisory.py           # L12 — Claude streaming advisory
        screening.py          # L1 + L3 — Halal status + stock scoring
        data_feed.py          # L10 — Feed status, cache inspection
        decision.py           # L11 — Decision engine signals
        zakat.py              # L6 — Zakat calculation
  core/
    config.py                 # Settings via pydantic BaseSettings
    redis_client.py           # Async Redis connection pool
    database.py               # SQLAlchemy async engine
  services/
    advisory/                 # Claude API client, system prompt builder
    screening/                # Zoya API client, AAOIFI ratio checker
    zakat/                    # Multi-mazhab calculation engine
    macro/                    # FRED API fetcher + caching
    decision/                 # Composite signal calculator
  models/                     # Pydantic request/response schemas
  utils/
    cache.py                  # Redis cache decorator (@cache_with_ttl)
    logger.py                 # Structured JSON logging
  data/
    islamic_knowledge/        # Static Quran/Hadith reference JSON

tests/
  unit/                       # Isolated unit tests (no external calls)
  integration/                # Tests against live Redis + DB

scripts/
  seed_halal_db.py            # Seed initial halal screening cache
```

## Package Naming
`seeroth_ai.<module>.<submodule>`

## Key Commands
```bash
uvicorn app.main:app --reload --port 8000   # Dev server
pytest                                       # All tests
pytest tests/unit/ -v                       # Unit tests only
ruff check .                                # Linter
black .                                     # Formatter
```

## Key Dependencies
- FastAPI 0.115+
- anthropic (claude-sonnet-4-20250514, streaming, tool use)
- httpx (async HTTP client for Polygon, FMP, Zoya, FRED)
- redis[asyncio]
- SQLAlchemy 2.0 (async)
- pydantic-settings 2.0
- pandas (data normalization)
- pytest + pytest-asyncio

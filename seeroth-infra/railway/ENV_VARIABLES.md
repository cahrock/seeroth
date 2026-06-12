# Railway Environment Variables — SeeRoth

Set these in Railway Dashboard → Service → Variables

---

## seeroth-api (Spring Boot)

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Railway reference variable |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Railway reference variable |
| `JWT_SECRET` | *(generate 256-bit secret)* | `openssl rand -hex 32` |
| `JWT_EXPIRY_MS` | `86400000` | 24 hours |
| `JWT_REFRESH_EXPIRY_MS` | `604800000` | 7 days |
| `CORS_ALLOWED_ORIGINS` | `https://your-web.up.railway.app` | Angular frontend URL |
| `AI_SERVICE_URL` | `https://seeroth-ai.up.railway.app` | Internal service URL |
| `SPRING_PROFILES_ACTIVE` | `prod` | |
| `ACTUATOR_PASSWORD` | *(random string)* | |

---

## seeroth-ai (FastAPI)

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Same PostgreSQL |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Same Redis |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | From console.anthropic.com |
| `CLAUDE_MODEL` | `claude-sonnet-4-20250514` | |
| `CLAUDE_TEMPERATURE` | `0.3` | |
| `POLYGON_API_KEY` | *(from polygon.io)* | |
| `FMP_API_KEY` | *(from financialmodelingprep.com)* | |
| `ZOYA_API_KEY` | *(from zoya.finance)* | |
| `FRED_API_KEY` | *(from fred.stlouisfed.org)* | Free |
| `ALPHA_VANTAGE_API_KEY` | *(from alphavantage.co)* | |
| `CORS_ALLOWED_ORIGINS` | `["https://your-web.up.railway.app"]` | JSON array |
| `APP_ENV` | `production` | |

---

## Generate JWT Secret (run in terminal)

```bash
# Option 1 — OpenSSL
openssl rand -hex 32

# Option 2 — Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 3 — PowerShell (Windows)
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

---

## Railway Reference Variables

Railway allows services to reference each other's variables:
- `${{Postgres.DATABASE_URL}}` — auto-injects PostgreSQL URL
- `${{Redis.REDIS_URL}}` — auto-injects Redis URL

This means you don't hardcode connection strings — Railway manages them.

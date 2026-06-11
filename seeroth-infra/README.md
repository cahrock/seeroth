# seeroth-infra — Infrastructure Configuration

## Structure
```
seeroth-infra/
  railway/
    services/           # Per-service Railway deployment config
    railway.toml        # Railway project root config
  docker/
    docker-compose.yml  # Local dev: PostgreSQL 16 + Redis 7
    web/
      Dockerfile        # Nginx + Angular static build
    api/
      Dockerfile        # Java 21 runtime
    ai/
      Dockerfile        # Python 3.12 runtime
  nginx/
    nginx.conf          # Reverse proxy + static serve config
  scripts/
    setup.sh            # First-time local environment setup
    deploy.sh           # Manual Railway deploy trigger
    db-migrate.sh       # Run Flyway migrations
  envs/
    .env.example        # Template — committed to repo
    .env.local          # Local dev — gitignored
    .env.staging        # Staging — gitignored
```

## Railway Services (MVP)

| Service      | Runtime          | Memory |
|--------------|------------------|--------|
| seeroth-api  | Java 21          | 512 MB |
| seeroth-ai   | Python 3.12      | 512 MB |
| seeroth-web  | Static / Nginx   | 256 MB |
| postgres     | PostgreSQL 16    | 1 GB   |
| redis        | Redis 7          | 256 MB |

## Quick Commands
```bash
# Start local dependencies only
docker-compose -f docker/docker-compose.yml up -d

# Deploy to Railway
railway up

# Run DB migrations
./scripts/db-migrate.sh
```

# SeeRoth — Halal Investment Simulation Platform
> *sirat al-mustaqim — The Straight Path to Halal Wealth*

[![CI](https://github.com/seeroth/seeroth/actions/workflows/ci.yml/badge.svg)](https://github.com/seeroth/seeroth/actions)
[![Version](https://img.shields.io/badge/version-1.0.0--MVP-blue)]()

---

## Overview

SeeRoth is a **halal-first** investment simulation and advisory platform integrating
12 layers of analysis — from Shariah compliance screening to Claude-powered AI advisory.

**v1.0 MVP** — Simulation mode (paper trading). No real broker execution.
**v2+ Roadmap** — Real broker execution via IBKR API.

---

## Monorepo Structure

```
seeroth/
├── seeroth-web/          # Frontend — Angular 18 + TailwindCSS
├── seeroth-api/          # Backend API — Spring Boot 3.5 (Java 21)
├── seeroth-ai/           # AI & Data Service — Python FastAPI
├── seeroth-infra/        # Infrastructure — Railway, Docker, Nginx
├── .github/
│   └── workflows/        # CI/CD — GitHub Actions
├── .gitignore
├── .editorconfig
└── README.md
```

---

## Services

| Service         | Stack                              | Port  | Description              |
|-----------------|------------------------------------|-------|--------------------------|
| seeroth-web     | Angular 18, TailwindCSS, NgRx      | 4200  | Browser-based SPA        |
| seeroth-api     | Spring Boot 3.5, Java 21           | 8080  | REST API + Auth          |
| seeroth-ai      | Python 3.12, FastAPI, Redis        | 8000  | AI Advisory + Data Feed  |
| seeroth-infra   | Railway, Docker, Nginx             | —     | Infrastructure config    |

---

## MVP Build Order

```
1.  Infrastructure         — Railway + PostgreSQL + Redis + CI/CD
2.  L10 Data Feed          — Polygon, FMP, Zoya, FRED, Benzinga
3.  L1  Halal Screening    — AAOIFI Standard 21 via Zoya API
4.  L3  Stock Screening    — Fundamental scoring
5.  L4  Technical Analysis — Chart + indicators
6.  L5  Risk Management    — Portfolio health + drawdown
7.  L11 Decision Engine    — Composite BUY/SELL/HOLD signal
8.  L6  Zakat & Purif.     — Multi-mazhab calculator
9.  L12 AI Advisory        — Claude API integration
10. Frontend Angular       — Connect all layers to UI
```

---

## Quick Start

### Prerequisites

- Node.js 20+ / npm 10+
- Java 21 (GraalVM or Temurin)
- Python 3.12+
- Docker and Docker Compose
- Railway CLI: `npm install -g @railway/cli`

### Local Development

```bash
# 1. Clone
git clone https://github.com/seeroth/seeroth.git
cd seeroth

# 2. Infrastructure
cp seeroth-infra/envs/.env.example seeroth-infra/envs/.env.local
docker-compose -f seeroth-infra/docker/docker-compose.yml up -d

# 3. Backend API
cd seeroth-api && ./mvnw spring-boot:run

# 4. AI Service
cd ../seeroth-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 5. Frontend
cd ../seeroth-web && npm install && ng serve
```

Open: http://localhost:4200

---

## Package Naming

| Service      | Convention              | Example                          |
|--------------|-------------------------|----------------------------------|
| Angular      | @seeroth/feature-name   | @seeroth/halal-screening         |
| Spring Boot  | com.seeroth.api.*       | com.seeroth.api.service          |
| Python       | seeroth_ai.*            | seeroth_ai.services.advisory     |

---

## Conventional Commits

```
<type>(<scope>): <description>

Types:  feat | fix | docs | style | refactor | test | chore | perf | ci

Scopes: web | api | ai | infra
        l1 | l2 | l3 | l4 | l5 | l6 | l7 | l8 | l9 | l10 | l11 | l12
        deps | ci | docs

Examples:
  feat(l10): add Polygon.io real-time price feed
  fix(l1): correct AAOIFI debt ratio threshold to 30 percent
  feat(l12): integrate Claude advisory streaming response
  chore(infra): update Railway service environment variables
  test(l6): add zakat unit tests for Syafii mazhab method
```

---

## Environment Variables

See `seeroth-infra/envs/.env.example` for all required variables.

| Variable            | Service | Description                  |
|---------------------|---------|------------------------------|
| DATABASE_URL        | api     | PostgreSQL connection string |
| REDIS_URL           | ai      | Redis connection string      |
| ANTHROPIC_API_KEY   | ai      | Claude API key               |
| POLYGON_API_KEY     | ai      | Market data                  |
| FMP_API_KEY         | ai      | Fundamentals                 |
| ZOYA_API_KEY        | ai      | Halal screening              |
| FRED_API_KEY        | ai      | Macro economics              |
| JWT_SECRET          | api     | Auth secret (min 256-bit)    |

---

## Tech Stack

```
Frontend : Angular 18 · TailwindCSS · NgRx · TradingView Charts
Backend  : Spring Boot 3.5 · Java 21 · PostgreSQL 16 + TimescaleDB
AI/Data  : Python 3.12 · FastAPI · Redis 7 · Anthropic Claude Sonnet
Infra    : Railway (MVP) · Docker · Nginx · Cloudflare R2
CI/CD    : GitHub Actions -> Railway auto-deploy
```

---

*Bismillah — In the name of Allah, the Most Gracious, the Most Merciful*

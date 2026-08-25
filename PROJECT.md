# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.3.0

Current development phase: Phase 3 - Market Data Engine

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 25%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py (FREE, OSS)

Database: PostgreSQL 16, local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7, local via Homebrew (FREE, OSS)

Market Data: Twelve Data (FREE TIER — 800 calls/day, 8/min, WebSocket testable on free plan)

AI: Not yet implemented

Infrastructure: GitHub, GitHub Actions (FREE TIER)

No paid dependency has been introduced.


---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup
✅ Module 2: Authentication & Authorization
✅ Module 3: Market Data Engine

---

# Current Module

Module 3: Market Data Engine

Purpose: Live streaming prices and historical candle storage for forex majors + XAU/USD.

Completed features: Single shared upstream WebSocket to Twelve Data, Redis pub/sub fan-out, authenticated frontend WebSocket, REST candle retrieval with auto-backfill, admin-only manual backfill, pure-calculation market session detection, Markets page with live ticker.

Files created/modified: See Module 3 file lists above.

Dependencies added: httpx, websockets, redis (Python client), Redis (Homebrew service).

Installation requirements: Redis 7 (Homebrew), free Twelve Data API key.

---

# Pending Modules

Phase 4: Database Layer (TimescaleDB hypertables, ticks, signals, trades, strategies, AI predictions, logs, metrics)
Phase 5: Feature Engineering
Phase 6: Backtesting Engine
Phase 7: AI Engine
Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

**users, refresh_tokens** — see Module 2.

**candles**
- id (UUID, PK)
- symbol (String, indexed)
- interval (String, indexed)
- open, high, low, close (Float)
- volume (Float, nullable)
- timestamp (DateTime, indexed)
- unique constraint on (symbol, interval, timestamp)

Migration: `backend/alembic/versions/0002_create_candles.py`

Note: stored as a plain PostgreSQL table for now. Phase 4 converts this into a TimescaleDB hypertable and adds tick-level storage.

---

# API Endpoints

GET /api/v1/health - health check - no auth
POST /api/v1/auth/register, /login, /refresh, /logout, GET /me - see Module 2
GET /api/v1/market/status - configured instruments + active sessions - requires view_markets permission
GET /api/v1/market/candles/{symbol} - historical candles, auto-backfills if empty - requires view_markets permission
POST /api/v1/market/backfill - manual candle backfill - admin only
WS /api/v1/market/ws/prices?token=<access_token> - live tick stream - requires view_markets permission

---

# WebSocket Events

`/market/ws/prices` streams raw Twelve Data price events, e.g.:
```json
{"event": "price", "symbol": "EUR/USD", "price": "1.08421", "timestamp": 1732450000}
```

---

# AI Models

None yet.

---

# Feature Engineering

None yet.

---

# Environment Variables

Backend (.env): all Module 2 variables, plus:
REDIS_URL - required
TWELVE_DATA_API_KEY - required, free key from twelvedata.com
TWELVE_DATA_REST_URL, TWELVE_DATA_WS_URL - required, have working defaults
MARKET_INSTRUMENTS - required, JSON array, defaults to 4 symbols to respect free-tier limits

Frontend (.env):
VITE_API_BASE_URL - required
VITE_WS_BASE_URL - required

---

# Configuration Files

Unchanged from Module 2, plus new modules under `infrastructure/market_data` and `infrastructure/cache`.

---

# Scripts

Backend: ruff check ., alembic upgrade head, alembic revision --autogenerate -m "message"
Frontend: npm run dev, npm run build, npm run lint, npm run format

No Docker commands are used.

---

# Testing

Unit tests: Not yet added
Integration tests: Not yet added
Coverage: 0%
Pending tests: market session calculation, candle upsert idempotency, WebSocket auth rejection paths

---

# Local Development

See Local Testing & Running section above.

---

# Deployment

Current deployment status: Not deployed
Deployment provider: Not yet selected
CI/CD: GitHub Actions (free tier)
Production readiness: Not production ready

---

# Security

Authentication/Authorization: unchanged from Module 2, extended with `require_admin` and WebSocket token validation.
Secrets: TWELVE_DATA_API_KEY and REDIS_URL added to .env, git-ignored.
Rate limiting: Twelve Data's own free-tier limits are the current backstop; no additional throttling implemented yet on our own endpoints.

---

# Performance

Redis pub/sub fan-out keeps upstream provider connections to exactly one regardless of frontend client count. Candle upserts are single-statement conflict-resolved writes.

---

# Known Issues

Market session detection does not account for Daylight Saving Time shifts — session windows are fixed UTC hours. This is accurate most of the year but drifts by an hour during DST transition periods for London/New York.

---

# Technical Debt

- Candle price columns use Float rather than Numeric/Decimal; acceptable for display purposes now, should move to fixed-point before this data feeds real position sizing.
- Rate limiting on our own auth/market endpoints deferred to a later hardening pass.
- Tick-level (not just candle) historical storage deferred to Phase 4.

---

# Future Improvements

Economic calendar and news feed integration — deferred pending a proper free-tier provider evaluation (see Module 3 Free/Open-Source Validation). DST-aware session calculation.

---

# Next Module

Module: Phase 4 - Database Layer

Objectives: Convert `candles` into a TimescaleDB hypertable, add tick-level storage, and create the schema foundation for signals, trades, strategies, AI predictions, logs, and metrics tables ahead of the feature engineering and backtesting modules.

Expected deliverables: TimescaleDB extension setup (Homebrew tap), hypertable migration, new domain entities and repositories for the additional tables, updated PROJECT.md schema section.
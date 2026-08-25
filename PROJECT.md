# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.4.0

Current development phase: Phase 4 - Database Layer

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 32%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built from source, run manually via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER — 800 calls/day, 8/min)

AI: Not yet implemented

Infrastructure: GitHub, GitHub Actions (FREE TIER)

No paid dependency has been introduced.


---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup
✅ Module 2: Authentication & Authorization
✅ Module 3: Market Data Engine
✅ Module 4: Database Layer

---

# Current Module

Module 4: Database Layer

Purpose: TimescaleDB hypertables for time-series data, tick-level persistence, foundational schema for later phases.

Completed features: `candles` converted to a hypertable (existing data preserved), new `ticks` hypertable with live ingestion wired into the Module 3 stream worker, six new foundational tables (`strategies`, `signals`, `trades`, `ai_predictions`, `logs`, `metrics`).

Files created/modified: See Module 4 file lists above.

Dependencies added: TimescaleDB (Apache-2.0 build) via Homebrew, extending existing PostgreSQL 16.

Installation requirements: `brew tap timescale/tap`, `brew install timescaledb --with-oss-only`.

---

# Pending Modules

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

**candles** (hypertable, partitioned on `timestamp`)
- id, timestamp (composite PK)
- symbol, interval (indexed)
- open, high, low, close, volume
- unique constraint (symbol, interval, timestamp)

**ticks** (hypertable, partitioned on `timestamp`)
- id, timestamp (composite PK)
- symbol (indexed)
- price

**strategies**
- id (PK), name (unique), description, parameters (JSONB), is_active, created_at, updated_at
- Populated starting Phase 6.

**signals**
- id (PK), strategy_id (FK → strategies, nullable), symbol, direction, confidence, reasoning (JSONB), created_at
- Populated starting Phase 8 (Decision Engine). `reasoning` JSONB is structured to hold trend, supporting indicators, risk level, expected reward, alternative scenarios, and invalidation conditions per the project's AI explainability requirements.

**trades**
- id (PK), signal_id (FK → signals, nullable), symbol, side, entry_price, exit_price, quantity, status, is_paper, pnl, opened_at, closed_at
- Populated starting Phase 9 (Paper Trading). `is_paper` distinguishes simulated trades from any future live execution.

**ai_predictions**
- id (PK), model_name, symbol, prediction_type, output (JSONB), created_at
- Populated starting Phase 7 (AI Engine).

**logs**
- id (PK), level, source, message, context (JSONB), created_at
- Structured audit trail; population deferred to a future logging-pipeline enhancement.

**metrics**
- id (PK), name, value, tags (JSONB), recorded_at
- Populated starting Phase 6 (Backtesting) for performance statistics.

Migration: `backend/alembic/versions/0003_timescaledb_and_schema.py`

---

# API Endpoints

Unchanged from Module 3 — this module added no new endpoints.

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

None yet.

---

# Feature Engineering

None yet.

---

# Environment Variables

Unchanged from Module 3.

---

# Configuration Files

Unchanged from Module 3.

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
Pending tests: hypertable migration idempotency, tick persistence failure handling

---

# Local Development

See Local Testing & Running section above. Redis is started manually via `src/redis-server` from a self-built Redis 7.2.16 — not a Homebrew service.

---

# Deployment

Current deployment status: Not deployed
Deployment provider: Not yet selected
CI/CD: GitHub Actions (free tier)
Production readiness: Not production ready

---

# Security

Unchanged from Module 3. No new attack surface introduced in this module.

---

# Performance

Hypertables keep time-range queries on `candles`/`ticks` performant as data grows. Tick persistence is fire-and-forget per tick via `asyncio.create_task`; batching is noted as technical debt below if volume grows.

---

# Known Issues

Market session detection does not account for Daylight Saving Time (unchanged from Module 3).

---

# Technical Debt

- Tick persistence opens one DB session per tick; acceptable at current Twelve Data free-tier update frequency, should move to a buffered/batched writer if instrument count or update frequency grows.
- Candle/tick price columns remain Float, not Numeric/Decimal (unchanged from Module 3).
- `logs` table exists but nothing writes to it yet — current logging is stdout-only; a DB-backed logging handler is a future improvement, not required for now.

---

# Future Improvements

Economic calendar / news integration (deferred from Module 3). DST-aware session calculation. Batched tick writes.

---

# Next Module

Module: Phase 5 - Feature Engineering

Objectives: Compute EMA, SMA, VWAP, ATR, RSI, MACD, ADX, Bollinger Bands, liquidity sweeps, market structure, swing highs/lows, order blocks, Fair Value Gaps, volatility, trend strength, momentum, and session labels from the candle data now stored in TimescaleDB.

Expected deliverables: A feature engineering service reading from `candles`, computed feature storage or on-demand calculation strategy, and the domain/application layers backing it.
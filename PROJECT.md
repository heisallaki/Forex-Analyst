# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.5.0

Current development phase: Phase 5 - Feature Engineering

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 40%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Not yet implemented (feature engineering only in this phase)

Infrastructure: GitHub, GitHub Actions (FREE TIER)

No paid dependency has been introduced.


---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup
✅ Module 2: Authentication & Authorization
✅ Module 3: Market Data Engine
✅ Module 4: Database Layer
✅ Module 5: Feature Engineering

---

# Current Module

Module 5: Feature Engineering

Purpose: Compute EMA, SMA, VWAP, ATR, RSI, MACD, ADX, Bollinger Bands, swing highs/lows, market structure, liquidity sweeps, order blocks, Fair Value Gaps, volatility, trend strength, momentum, and session labels from candle data.

Completed features: `GET /api/v1/features/{symbol}` returning a full per-candle feature series, built entirely in-house on pandas/numpy.

Files created/modified: See Module 5 file lists above.

Dependencies added: pandas, numpy.

Installation requirements: None beyond `pip install pandas numpy`.

---

# Pending Modules

Phase 6: Backtesting Engine
Phase 7: AI Engine
Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

Unchanged from Module 4. Feature engineering is computed on-demand and not persisted in this module; persistence of computed features (if needed for backtest replay speed) will be revisited in Phase 6 if profiling shows it's necessary.

---

# API Endpoints

Unchanged from Module 4, plus:
GET /api/v1/features/{symbol} - full feature series for a symbol/interval - requires view_markets permission

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

None yet — this module produces the inputs future models will consume.

---

# Feature Engineering

**Trend/momentum indicators:** SMA(20), EMA(20), MACD(12,26,9), ADX(14) with +DI/-DI, RSI(14)

**Volatility indicators:** ATR(14), Bollinger Bands(20, 2σ), rolling log-return volatility(14)

**Volume-derived:** VWAP (falls back to cumulative typical price when volume is zero/absent, which is common for forex feeds without real volume — documented limitation below)

**Price action:** swing highs/lows (5-candle window), market structure classification (uptrend/downtrend/undetermined from swing sequences), liquidity sweep detection, order block detection (ATR-relative displacement heuristic), Fair Value Gap detection (3-candle pattern)

**Context:** momentum (rate of change, 10-period), active market sessions per candle timestamp

All indicators and price-action rules are implemented in-house on pandas/numpy — no third-party TA library dependency (see Module 5 Free/Open-Source Validation for why).

---

# Environment Variables

Unchanged from Module 4.

---

# Configuration Files

Unchanged from Module 4.

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
Pending tests: indicator values against known reference calculations, price-action rule edge cases (start/end of series, flat markets)

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

Unchanged from Module 4. No new attack surface.

---

# Performance

Indicator math is fully vectorized. Price-action functions (swing points, structure, sweeps, order blocks, FVGs) use explicit Python loops, acceptable for on-demand REST calls at current limits (up to 5000 rows); flagged as a vectorization candidate if this ever needs to run inside a hot backtesting loop in Phase 6.

---

# Known Issues

Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- VWAP falls back to a cumulative typical-price average when volume data is absent/zero, since most forex feeds (including our current provider) don't report meaningful volume; this is a known approximation, not true VWAP.
- Price-action detection functions are not yet unit-tested against hand-verified reference cases.
- No automated indicator correctness tests yet against a trusted reference implementation.

---

# Future Improvements

Persisting computed feature rows if Phase 6 backtesting shows recomputing on every backtest run is too slow. Vectorizing the price-action loop functions if profiling shows they're a bottleneck.

---

# Next Module

Module: Phase 6 - Backtesting Engine

Objectives: Historical replay across the candle/feature data now available, multi-timeframe testing, transaction cost and spread/slippage simulation, and performance statistics (win rate, Sharpe, Sortino, drawdown, profit factor, R-multiple, monthly performance) — populating the `strategies`, `trades`, and `metrics` tables created in Phase 4.

Expected deliverables: A backtest execution engine, strategy definition schema, and a REST endpoint to run and retrieve backtest results.
# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.9.0

Current development phase: Phase 9 - Paper Trading

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 75%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy, scikit-learn, XGBoost, LightGBM, joblib (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Six local models + deterministic decision engine (Modules 7-8) (FREE, OSS)

Infrastructure: GitHub, GitHub Actions (FREE TIER)

No paid dependency has been introduced.


---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup
✅ Module 2: Authentication & Authorization
✅ Module 3: Market Data Engine
✅ Module 4: Database Layer
✅ Module 5: Feature Engineering
✅ Module 6: Backtesting Engine
✅ Module 7: AI Engine
✅ Module 8: Decision Engine
✅ Module 9: Paper Trading

---

# Current Module

Module 9: Paper Trading

Purpose: Virtual portfolios, real-time trade execution simulation against live prices, performance tracking, trade journal.

Completed features: Portfolio creation/listing, opening trades with explicit or risk-based sizing, automatic stop-loss/take-profit execution driven by the live Twelve Data tick stream, manual close, trade journal, portfolio performance stats.

Files created/modified: See Module 9 file lists above.

Dependencies added: None.

Installation requirements: None beyond what already exists.

---

# Pending Modules

Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

**portfolios**
- id (PK), user_id (FK → users), name, base_currency, initial_balance, current_balance, created_at, updated_at

**trades** (extended)
- Added: portfolio_id (FK → portfolios, nullable — null for backtest-only trades from Module 6), stop_loss, take_profit
- `portfolio_id IS NOT NULL` is the reliable way to distinguish real paper trades from backtest simulation trades; both share `is_paper = true`.

Migration: `backend/alembic/versions/0004_portfolios_and_trade_orders.py`

---

# API Endpoints

Unchanged from Module 8, plus:
POST /api/v1/paper/portfolios - create a portfolio - requires manage_strategies permission
GET /api/v1/paper/portfolios - list current user's portfolios - requires view_markets permission
GET /api/v1/paper/portfolios/{portfolio_id}/performance - performance stats - requires view_markets permission
POST /api/v1/paper/trades - open a trade (explicit quantity or risk-based sizing) - requires manage_strategies permission
POST /api/v1/paper/trades/{trade_id}/close - manually close a trade - requires manage_strategies permission
GET /api/v1/paper/trades?portfolio_id=&status= - trade journal - requires view_markets permission

---

# WebSocket Events

Unchanged from Module 3. Internally, the position monitor (a new background task, not client-facing) also subscribes to the `market:ticks` Redis channel used by that WebSocket.

---

# AI Models

Unchanged from Module 7-8.

---

# Feature Engineering

Unchanged from Module 8.

---

# Environment Variables

Unchanged from Module 7.

---

# Configuration Files

Unchanged from Module 7.

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
Pending tests: stop-loss/take-profit trigger boundary conditions, portfolio balance arithmetic, cross-user portfolio access isolation

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

Portfolio access is scoped by both portfolio ID and requesting user ID at the repository layer — no cross-user data leakage even with a guessed UUID. Trading actions require `manage_strategies`; read access requires only `view_markets`.

---

# Performance

Position monitoring reuses the existing tick Redis channel rather than opening new upstream connections or polling loops.

---

# Known Issues

- Trades opened without a `stop_loss` will never auto-close — they remain open until manually closed via `/paper/trades/{id}/close`. This is documented, intentional behavior, not a bug, but is a real risk-management gap worth being aware of.
- Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- `compute_pnl`/`pip_size` in `trading_math.py` duplicate similar logic already present in `backtest_engine.py`'s private `_pip_size`; a shared module would be cleaner but wasn't worth risking a change to tested Module 6 code for this pass.
- No margin/leverage modeling — position sizing is purely risk-amount-based, not account-leverage-aware.
- No automated tests yet for trigger boundary conditions.

---

# Future Improvements

Shared pip-size/PnL utility module across backtest and paper trading. Leverage/margin modeling. Partial position closes. Trailing stops.

---

# Next Module

Module: Phase 10 - Execution Engine

Objectives: Architecture for future broker integration, initially disabled by default, with robust risk management guardrails. No live trading connection is established automatically.

Expected deliverables: An execution engine interface/abstraction ready for a future broker adapter, a hard "disabled" flag enforced in code (not just configuration), and risk-management checks that would apply even once enabled.
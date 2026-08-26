# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.6.0

Current development phase: Phase 6 - Backtesting Engine

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 48%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Not yet implemented (rule-based backtesting only in this phase)

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

---

# Current Module

Module 6: Backtesting Engine

Purpose: Simulate rule-based strategies against historical data with realistic execution costs, and compute full performance statistics.

Completed features: `POST /api/v1/backtest/run` — multi-interval backtest execution with ATR-based stops/targets, risk-based position sizing, spread/slippage/commission modeling, and win rate / profit factor / Sharpe / Sortino / max drawdown / average R-multiple / monthly performance statistics. Populates `strategies`, `signals`, `trades`, `metrics`.

Files created/modified: See Module 6 file lists above.

Dependencies added: None (standard library only).

Installation requirements: None beyond what already exists.

---

# Pending Modules

Phase 7: AI Engine
Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

Unchanged from Module 4 — this module is the first to actually write into `strategies`, `signals`, `trades`, and `metrics`.

**Backtest write pattern:**
- One `strategies` row per unique `strategy_name` (created once; re-running with the same name does not currently update `parameters` — see Technical Debt).
- One `signals` row per simulated trade, `reasoning` JSONB capturing the matched rule side and the feature snapshot at entry.
- One `trades` row per simulated trade, `signal_id` linking back, `is_paper = true`.
- Several `metrics` rows per backtest run (`win_rate`, `profit_factor`, `sharpe_ratio`, `sortino_ratio`, `max_drawdown_pct`, `average_r_multiple`, `final_equity`), tagged with `{strategy, symbol, interval}`.

---

# API Endpoints

Unchanged from Module 5, plus:
POST /api/v1/backtest/run - run a backtest across one or more intervals - requires manage_strategies permission

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

None yet — strategies in this module are rule-based, not learned.

---

# Feature Engineering

Unchanged from Module 5, with `FeatureRow` extended to include `open`/`high`/`low` (needed for realistic next-bar-open execution in the backtest engine).

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
Pending tests: statistics formulas against hand-verified reference cases, rule evaluator edge cases, no-lookahead correctness

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

Strategy rules are structured JSON evaluated by a fixed, safe interpreter — no `eval()` or dynamic code execution anywhere. `/backtest/run` requires `manage_strategies` permission, not just authentication.

---

# Performance

Backtest simulation is O(n) per interval over the requested candle limit. Signal/trade persistence is per-trade, not batched — acceptable at current typical trade counts, flagged below for high-volume backtests.

---

# Known Issues

Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- Re-running a backtest with an existing `strategy_name` does not update its stored `parameters` — only the first creation is persisted. Strategy versioning will need proper handling before Phase 11 exposes strategy management in the dashboard.
- PnL calculation assumes the quote currency equals the account currency (USD), which holds for EUR/USD, GBP/USD, and XAU/USD but not for USD/JPY-style pairs where USD is the base currency. Proper multi-currency P&L conversion is deferred.
- Slippage is modeled as a fixed, deterministic pip value rather than volatility-based, favoring backtest reproducibility over realism; documented as a future improvement.
- Signal/trade writes are not batched; fine at current volumes, worth revisiting for very large backtests.

---

# Future Improvements

Volatility-based slippage modeling. Multi-currency P&L accounting. Strategy parameter versioning on rerun. Persisting computed feature rows if backtest speed becomes a bottleneck (noted in Module 5).

---

# Next Module

Module: Phase 7 - AI Engine

Objectives: Specialized models — Trend Classification, Entry Quality, Risk Prediction, Reward Prediction, Confidence Scoring, Market Regime Classification — trained on the feature data now available, running locally via free/open-source ML frameworks (scikit-learn, XGBoost, LightGBM, PyTorch).

Expected deliverables: Model training pipeline, model storage/versioning, prediction endpoints populating the `ai_predictions` table from Phase 4.
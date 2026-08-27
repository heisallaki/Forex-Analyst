# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.8.0

Current development phase: Phase 8 - Decision Engine

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 65%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy, scikit-learn, XGBoost, LightGBM, joblib (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Six local models (Module 7) combined by a deterministic decision engine (Module 8) — no external LLM/AI API used anywhere (FREE, OSS)

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

---

# Current Module

Module 8: Decision Engine

Purpose: Combine the six AI Engine predictions into one explainable recommendation, enforcing minimum confidence and reward-to-risk thresholds so the system recommends `no_trade` honestly rather than forcing a directional call.

Completed features: `GET /api/v1/decision/recommend/{symbol}` — full recommendation with trend, confidence, risk level, expected reward, supporting indicators, reasoning, alternative scenarios, invalidation conditions, and a disclaimer. Persists to `signals`.

Files created/modified: See Module 8 file lists above.

Dependencies added: None.

Installation requirements: None beyond what already exists.

---

# Pending Modules

Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

Unchanged from Module 4. This module writes richer `signals` rows than Module 6's rule-based backtest signals — `reasoning` JSONB now includes `risk_level`, `market_regime`, `supporting_indicators`, `alternative_scenarios`, `invalidation_conditions`, and `source: "decision_engine"` to distinguish AI-generated signals from backtest-generated ones.

---

# API Endpoints

Unchanged from Module 7, plus:
GET /api/v1/decision/recommend/{symbol} - combined, explainable recommendation - requires view_markets permission

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

Unchanged from Module 7. This module adds no new models — it combines their outputs.

---

# Feature Engineering

Unchanged from Module 7.

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
Pending tests: threshold-boundary behavior (confidence/RR exactly at the cutoff), missing-model graceful degradation

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

No new attack surface. Reuses existing permission gates and persistence patterns.

---

# Performance

Eliminated a redundant candle/feature fetch by refactoring `predict_market_use_case` into a shared `predict_market_with_features` function, reused by both the `/ai/predict` endpoint and this module's recommendation flow.

---

# Known Issues

Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- `MIN_CONFIDENCE_THRESHOLD` (55%) and `MIN_REWARD_RISK_RATIO` (1.2) are hardcoded constants; making these configurable (per-user risk tolerance, or admin-tunable) is a reasonable future improvement once the dashboard (Phase 11) exists to expose them.
- No automated tests yet for exact threshold-boundary behavior.
- Reasoning templates are in English only; internationalization is out of scope for now.

---

# Future Improvements

Configurable confidence/reward-risk thresholds. Multi-symbol batch recommendations. Historical recommendation accuracy tracking (comparing past `no_trade`/`long`/`short` calls against what actually happened) once enough signals have accumulated.

---

# Next Module

Module: Phase 9 - Paper Trading

Objectives: A virtual portfolio, trade execution simulator, performance tracking, and trade journal — turning Phase 8's recommendations (and Phase 6's backtested strategies) into simulated live positions with `is_paper = true` in the `trades` table.

Expected deliverables: Portfolio balance tracking, simulated order execution against live prices from Phase 3, position management (open/close/stop/target), and a paper trading REST API.
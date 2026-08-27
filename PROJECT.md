# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 1.0.0

Current development phase: Complete — all 11 phases delivered

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 100%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI v6, React Router, React Hook Form, Zod, Zustand, TradingView Lightweight Charts, Recharts (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy, scikit-learn, XGBoost, LightGBM, joblib (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Six local models + deterministic decision engine, no external AI/LLM API used anywhere (FREE, OSS)

Execution: Architecture-only, disabled by default, no broker connected

Infrastructure: GitHub, GitHub Actions (FREE TIER)

No paid dependency exists anywhere in this project.


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
✅ Module 10: Execution Engine
✅ Module 11: Dashboard

---

# Current Module

Module 11: Dashboard (final module)

Purpose: Complete frontend tying together every backend capability from Modules 2-10.

Completed features: Ten-section navigated dashboard — Dashboard, Markets, Charts, AI Analysis, Signals, Strategies, Backtesting, Paper Trading, Analytics, Settings.

Files created/modified: See Module 11 file lists above. Two small read-only backend endpoints added (`GET /decision/signals`, `GET /backtest/strategies`).

Dependencies added: lightweight-charts, recharts.

---

# Pending Modules

None. All 11 phases are complete.

---

# Database Schema

Unchanged from Module 9-10. Full schema: `users`, `refresh_tokens`, `candles` (hypertable), `ticks` (hypertable), `strategies`, `signals`, `trades` (backtest + paper, distinguished by `portfolio_id`), `ai_predictions`, `logs`, `metrics`, `portfolios`.

---

# API Endpoints

All endpoints from Modules 2-10, plus:
GET /api/v1/decision/signals - list recent signals - requires view_markets permission
GET /api/v1/backtest/strategies - list strategies - requires view_markets permission

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

Unchanged from Module 7-8.

---

# Feature Engineering

Unchanged from Module 8.

---

# Environment Variables

Unchanged from Module 10. No new variables in this module.

---

# Configuration Files

Unchanged from Module 10.

---

# Scripts

Backend: ruff check ., alembic upgrade head, alembic revision --autogenerate -m "message"
Frontend: npm run dev, npm run build, npm run lint, npm run format

No Docker commands are used anywhere in this project.

---

# Testing

Unit tests: Not yet added
Integration tests: Not yet added
Coverage: 0%
Pending tests: accumulated across every module's Technical Debt sections — a dedicated testing pass is the clear next priority beyond the original 11-phase plan.

---

# Local Development

See each module's Local Testing & Running section; Module 11's covers the full end-to-end walkthrough.

---

# Deployment

Current deployment status: Not deployed
Deployment provider: Not yet selected
CI/CD: GitHub Actions (free tier) — lint/build only, no deployment pipeline yet
Production readiness: Functionally complete for personal/local use; not hardened for public production deployment (see Security and Technical Debt below)

---

# Security

Full auth/RBAC (Module 2), portfolio isolation by user (Module 9), execution engine locked by two independent layers plus no broker adapter (Module 10). No rate limiting on any endpoint yet. No automated security testing yet.

---

# Performance

TimescaleDB hypertables for time-series data, Redis pub/sub fan-out for live prices, capped result sizes throughout the frontend.

---

# Known Issues

- Market session detection does not account for Daylight Saving Time.
- Trades without a stop-loss never auto-close (documented, intentional).
- Backtest equity curve chart shows only the first requested interval's series when multiple intervals are run.

---

# Technical Debt

Accumulated across all 11 modules — see each module's section in prior versions of this document (preserved in git history). Highest-priority items: automated test coverage (currently 0% throughout), rate limiting, DST-aware session logic, multi-currency P&L accuracy.

---

# Future Improvements

PyTorch models once data volume justifies it. Reinforcement learning once more live paper-trading history accumulates. A real (carefully vetted, free/practice-account) broker adapter for Module 10. Configurable decision-engine thresholds. Full automated test suite.

---

# Next Module

None — the 11-phase build plan is complete. Future work should be scoped as new, explicitly-requested modules following the same workflow used throughout this build.
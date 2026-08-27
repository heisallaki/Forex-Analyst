# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.10.0

Current development phase: Phase 10 - Execution Engine

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 85%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy, scikit-learn, XGBoost, LightGBM, joblib (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: Six local models + deterministic decision engine (Modules 7-8) (FREE, OSS)

Execution: No broker connected. Architecture-only module, disabled by default (see Module 10).

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
✅ Module 10: Execution Engine

---

# Current Module

Module 10: Execution Engine

Purpose: Broker-agnostic execution architecture, disabled by default in code (not just configuration), with risk-management guardrails exercised even though no broker is connected.

Completed features: `BrokerAdapter` interface, `ExecutionGateway` enforcing a four-layer check (config disable → confirmation phrase → risk management → adapter, where the only adapter always rejects), full audit logging to `logs`, admin-only status and order-submission endpoints.

Files created/modified: See Module 10 file lists above.

Dependencies added: None.

Installation requirements: None.

---

# Pending Modules

Phase 11: Dashboard

---

# Database Schema

Unchanged from Module 9. This module is the first to actually write into `logs` — every execution attempt (rejected or, hypothetically, otherwise) produces one row with `source = "execution_engine"`.

---

# API Endpoints

Unchanged from Module 9, plus:
GET /api/v1/execution/status - current execution configuration and limits - admin only
POST /api/v1/execution/orders - submit an order; always rejected in this build (no broker adapter exists) - admin only

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

Unchanged from Module 7, plus:
EXECUTION_ENABLED - required, defaults to `false`, must stay `false` in normal operation
EXECUTION_MAX_POSITION_SIZE - required, default 10000
EXECUTION_MAX_OPEN_POSITIONS - required, default 3
EXECUTION_MAX_DAILY_LOSS_PCT - required, default 5.0

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
Pending tests: each of the four gateway check layers individually, confirmation-phrase exact-match behavior, risk-management violation combinations

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

Execution endpoints require the admin role — the strictest gate in the system. Live execution requires both a configuration flag and an exact hardcoded confirmation phrase, and even then resolves to `NoBrokerConfiguredAdapter`, which unconditionally rejects. Every attempt is audit-logged to `logs`.

---

# Performance

Not applicable — no hot path, no external calls in this module.

---

# Known Issues

- Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- Risk-management checks currently receive `open_positions_count=0` and `daily_loss_pct=0.0` as hardcoded placeholders from `submit_execution_order_use_case`, since there's no real broker to source live position/P&L data from yet. Wiring these to the paper-trading portfolio (or a future live-account feed) as a proxy is worth considering once Phase 11's dashboard needs to display this meaningfully.
- No automated tests yet for the four-layer gateway logic.

---

# Future Improvements

An actual `BrokerAdapter` implementation (e.g. OANDA) would be the natural next real integration, evaluated carefully for free/practice-account terms before ever being connected — and even then, `EXECUTION_ENABLED` would need to be deliberately set by the person running this, never by default.

---

# Next Module

Module: Phase 11 - Dashboard

Objectives: A professional, Bloomberg-style interface tying every previous module together — Dashboard, Markets, Charts, AI Analysis, Signals, Strategies, Backtesting, Paper Trading, Analytics, Performance, Settings.

Expected deliverables: Full frontend build-out consuming every REST/WebSocket endpoint created in Modules 2-10, including TradingView Lightweight Charts and Recharts as specified in the original tech stack. This is the final module — README.md gets its one and only update after this phase completes.
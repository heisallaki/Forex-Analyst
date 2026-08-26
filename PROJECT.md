# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.7.0

Current development phase: Phase 7 - AI Engine

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 58%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, pwdlib[argon2], python-jose, httpx, websockets, redis-py, certifi, pandas, numpy, scikit-learn, XGBoost, LightGBM, joblib (FREE, OSS)

Database: PostgreSQL 16 + TimescaleDB (Apache-2.0 build), local via Homebrew (FREE, OSS)

Cache/Messaging: Redis 7.2.16, self-built, run via `src/redis-server` (FREE, OSS)

Market Data: Twelve Data (FREE TIER)

AI: scikit-learn, XGBoost, LightGBM — six local models trained per symbol/interval, no external AI API (FREE, OSS). PyTorch and Stable-Baselines3 deliberately deferred (see Module 7 Free/Open-Source Validation).

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

---

# Current Module

Module 7: AI Engine

Purpose: Train and serve six specialized local models (trend, entry quality, confidence, risk, reward, market regime), populating `ai_predictions`.

Completed features: `POST /api/v1/ai/train` (admin only) trains and versions all six models per symbol/interval; `GET /api/v1/ai/predict/{symbol}` returns raw predictions from the latest trained models and persists them.

Files created/modified: See Module 7 file lists above.

Dependencies added: scikit-learn, xgboost, lightgbm, joblib; libomp (Homebrew, macOS OpenMP runtime).

Installation requirements: `brew install libomp` before `pip install xgboost lightgbm`.

---

# Pending Modules

Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

Unchanged from Module 4 — this module is the first to write into `ai_predictions`. Each `/ai/predict` call writes six rows (`prediction_type`: trend, entry_quality, confidence, risk, reward, regime), each with a structured `output` JSONB.

---

# API Endpoints

Unchanged from Module 6, plus:
POST /api/v1/ai/train - train all six models for a symbol/interval - admin only
GET /api/v1/ai/predict/{symbol} - raw model predictions (not recommendations) for the latest bar - requires view_markets permission

---

# WebSocket Events

Unchanged from Module 3.

---

# AI Models

**Trend Classification** (XGBoost, multiclass) — Inputs: 14 ATR-normalized technical features. Outputs: predicted trend (up/down/flat) with per-class probability. Training status: trained on demand via `/ai/train`. Evaluation: accuracy, macro F1.

**Entry Quality** (LightGBM, binary) — Inputs: same 14 features. Outputs: probability the current bar precedes a tradeable move (direction-agnostic). Evaluation: accuracy, ROC-AUC.

**Confidence Scoring** (Logistic Regression, binary) — Inputs: same 14 features. Outputs: probability a long-direction trade from this bar hits its ATR-based target before its stop. Evaluation: accuracy, ROC-AUC.

**Risk Prediction** (Gradient Boosting Regressor) — Inputs: same 14 features. Outputs: predicted maximum adverse excursion, in ATR units, over the training horizon. Evaluation: mean absolute error.

**Reward Prediction** (Gradient Boosting Regressor) — Inputs: same 14 features. Outputs: predicted maximum favorable excursion, in ATR units. Evaluation: mean absolute error.

**Market Regime Classification** (KMeans clustering → Random Forest classifier) — Inputs: ADX, volatility, Bollinger bandwidth. Outputs: trending / ranging / volatile. Evaluation: accuracy against cluster-derived labels.

All six are trained per symbol/interval combination and versioned locally under `backend/models/`.

---

# Feature Engineering

Unchanged from Module 6. The AI Engine consumes a derived 14-column ATR-normalized feature set (`rsi_14`, `macd`, `macd_signal`, `macd_histogram`, `adx_14`, `plus_di_14`, `minus_di_14`, `volatility`, `momentum`, `bollinger_bandwidth`, `close_to_ema_atr`, `close_to_vwap_atr`, `swing_high_flag`, `swing_low_flag`) built from the full feature set in `dataset_builder.row_to_ml_features`.

---

# Environment Variables

Unchanged from Module 4, plus:
MODEL_STORAGE_PATH - required, defaults to `./models`, git-ignored

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
Pending tests: dataset labeling correctness (no-lookahead, stop-vs-target ordering), train/serve feature parity

---

# Local Development

See Local Testing & Running section above. `brew install libomp` is a one-time prerequisite for XGBoost/LightGBM on macOS.

---

# Deployment

Current deployment status: Not deployed
Deployment provider: Not yet selected
CI/CD: GitHub Actions (free tier)
Production readiness: Not production ready

---

# Security

Training is admin-only. No dynamic code execution or user-controlled file paths anywhere in the ML pipeline. Model artifacts are git-ignored, generated locally, never fetched from an external source.

---

# Performance

Training runs synchronously in-request; fine at current data volumes (seconds per full six-model training run). Flagged for background-job treatment if dataset sizes grow.

---

# Known Issues

Market session detection does not account for Daylight Saving Time (carried over from Module 3).

---

# Technical Debt

- Risk/Reward/Confidence models are trained assuming a long-direction entry; short-direction values are expected to be used mirrored by the Decision Engine (Phase 8) rather than trained as separate models. Revisit if backtesting shows meaningful long/short asymmetry.
- Training is synchronous within the request; move to a background job if it becomes slow at larger data volumes.
- No automated tests yet for dataset labeling correctness.
- PyTorch and Stable-Baselines3 deliberately deferred (see Free/Open-Source Validation) — revisit once enough historical data and a paper-trading environment exist, respectively.

---

# Future Improvements

Deep learning models (PyTorch) once data volume justifies it. Reinforcement learning (Stable-Baselines3) once Phase 9's paper trading environment exists to train against. Background-job training via Celery.

---

# Next Module

Module: Phase 8 - Decision Engine

Objectives: Combine the six raw model predictions from this module into a single explainable recommendation — trend, confidence, supporting indicators, risk level, expected reward, reasoning, alternative scenarios, and invalidation conditions — never a bare BUY/SELL, populating a richer `signals` record than Phase 6's rule-based ones.

Expected deliverables: A decision engine service that combines AI Engine outputs, a recommendation DTO enforcing the project's explainability requirements, and a REST endpoint.
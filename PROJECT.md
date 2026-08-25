# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.2.0

Current development phase: Phase 2 - Authentication

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 15%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI, React Router, React Hook Form, Zod, Zustand (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings, SQLAlchemy 2.0, Alembic, passlib, python-jose (FREE, OSS)

Database: PostgreSQL 16, installed locally via Homebrew (FREE, OSS)

AI: Not yet implemented

Infrastructure: GitHub, GitHub Actions (FREE TIER)

DevOps: Ruff, ESLint, Prettier (FREE, OSS)

APIs: None external yet

No paid dependency has been introduced.


---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup
✅ Module 2: Authentication & Authorization

---

# Current Module

Module 2: Authentication & Authorization

Purpose: JWT access/refresh authentication with DB-backed refresh token revocation and role/permission model.

Completed features: Register, login, refresh (with rotation), logout, protected `/me` endpoint, frontend login/register pages, protected routing, persisted auth state.

Files created/modified: See Module 2 file lists above.

Dependencies added: sqlalchemy[asyncio], asyncpg, alembic, passlib[bcrypt], python-jose[cryptography], python-multipart, email-validator, zustand, react-router-dom, react-hook-form, zod, @hookform/resolvers.

Installation requirements: PostgreSQL 16 (Homebrew), Python 3.12, Node 20.

---

# Pending Modules

Phase 3: Market Data Engine
Phase 4: Database Layer (extending schema for market data)
Phase 5: Feature Engineering
Phase 6: Backtesting Engine
Phase 7: AI Engine
Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

**users**
- id (UUID, PK)
- email (String, unique, indexed)
- hashed_password (String)
- full_name (String)
- role (String: admin | analyst | viewer)
- permissions (JSONB)
- is_active (Boolean)
- created_at, updated_at (DateTime)

**refresh_tokens**
- id (UUID, PK)
- user_id (UUID, FK → users.id, indexed)
- token_hash (String, unique, indexed)
- expires_at (DateTime)
- revoked (Boolean)
- created_at (DateTime)

Migration: `backend/alembic/versions/0001_create_users_and_refresh_tokens.py`

---

# API Endpoints

GET /api/v1/health - health check - no auth
POST /api/v1/auth/register - create account, returns tokens - no auth
POST /api/v1/auth/login - authenticate, returns tokens - no auth
POST /api/v1/auth/refresh - rotate refresh token - no auth (requires valid refresh token)
POST /api/v1/auth/logout - revoke refresh token - no auth (requires valid refresh token)
GET /api/v1/auth/me - current user profile - requires Bearer access token

---

# WebSocket Events

None yet.

---

# AI Models

None yet.

---

# Feature Engineering

None yet.

---

# Environment Variables

Backend (.env):
APP_NAME, APP_ENV, APP_DEBUG, API_PREFIX, HOST, PORT, CORS_ORIGINS - required
DATABASE_URL - required
JWT_SECRET_KEY - required, generate with `python3 -c "import secrets; print(secrets.token_urlsafe(64))"`
JWT_ALGORITHM - required, default HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES - required, default 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS - required, default 7

Frontend (.env):
VITE_API_BASE_URL - required

No production secrets are present in this repository.

---

# Configuration Files

backend/pyproject.toml, backend/ruff.toml, backend/alembic.ini - backend config
frontend/package.json, tsconfig.json, vite.config.ts, .eslintrc.cjs, .prettierrc - frontend config
.github/workflows/ci.yml - CI pipeline

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
Pending tests: Auth use cases, JWT validity, refresh rotation, protected route behavior

---

# Local Development

See Local Testing & Running section below.

---

# Deployment

Current deployment status: Not deployed
Deployment provider: Not yet selected
CI/CD: GitHub Actions (free tier)
Production readiness: Not production ready

---

# Security

Authentication: JWT access tokens (15 min) + rotating refresh tokens (7 days), refresh tokens stored as SHA-256 hashes, never in plaintext
Authorization: Role-based (admin/analyst/viewer) with per-permission JSONB flags, enforced via FastAPI dependency `require_permission`
Secrets: .env files git-ignored; JWT_SECRET_KEY must be generated locally, never committed
Validation: Pydantic schemas on all auth endpoints
Rate limiting: Not yet implemented
Logging: Basic stdout logging configured

---

# Performance

No caching or background jobs yet. Database access is fully async via SQLAlchemy asyncio + asyncpg.

---

# Known Issues

None currently.

---

# Technical Debt

Rate limiting on auth endpoints deferred to a later hardening pass.

---

# Future Improvements

Email verification, password reset flow, MFA — to be scheduled after core trading features are complete.

---

# Next Module

Module: Phase 3 - Market Data Engine

Objectives: Live price streaming via WebSocket, candle/tick storage, free-tier market data provider integration (Forex + XAU/USD), economic calendar and news feed integration.

Expected deliverables: Provider-agnostic market data service, Redis-backed price broadcaster, authenticated WebSocket endpoint, Markets page on the frontend.
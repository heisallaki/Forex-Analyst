# Project Overview

Project name: Forex Trading Analyst

Purpose: AI-powered forex and gold market analysis platform providing explainable trading recommendations, backtesting, and paper trading. Not a signal-selling or auto-gambling tool.

Goals: Live market monitoring, feature engineering, multi-model AI decision engine, backtesting, paper trading, future execution support.

Current version: 0.1.0

Current development phase: Phase 1 - Project Planning

Overall architecture: Clean Architecture monorepo. Backend: FastAPI (presentation/application/domain/infrastructure). Frontend: React 19 + TypeScript, feature-sliced design.

Current completion percentage: 5%

---

# Technology Stack

Frontend: React 19, TypeScript, Vite, MUI (FREE, OSS)

Backend: Python, FastAPI, Uvicorn, Pydantic Settings (FREE, OSS)

Database: Not yet implemented (planned: PostgreSQL, FREE, OSS)

AI: Not yet implemented

Infrastructure: GitHub, GitHub Actions (FREE TIER)

DevOps: Ruff, ESLint, Prettier (FREE, OSS)

Libraries: See package.json and pyproject.toml

APIs: None integrated yet

No paid dependency has been introduced.

---

# Completed Modules

✅ Module 1: Project Initialization & Repository Setup

---

# Current Module

Module 1: Project Initialization & Repository Setup

Purpose: Establish monorepo skeleton, linting, environment configuration, CI.

Completed features: FastAPI health endpoint, React health-check UI, CI lint/build pipeline.

Files created: See Module 1 file list.

Files modified: None.

Dependencies added: fastapi, uvicorn, pydantic-settings, ruff, react, vite, mui, eslint, prettier.

Installation requirements: Python 3.12, Node.js 20, Git.

---

# Pending Modules

Phase 2: Authentication
Phase 3: Market Data Engine
Phase 4: Database Layer
Phase 5: Feature Engineering
Phase 6: Backtesting Engine
Phase 7: AI Engine
Phase 8: Decision Engine
Phase 9: Paper Trading
Phase 10: Execution Engine (disabled by default)
Phase 11: Dashboard

---

# Database Schema

Not applicable yet.

---

# API Endpoints

GET /api/v1/health - returns {"status": "ok"} - no auth required

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
APP_NAME - required
APP_ENV - required
APP_DEBUG - required
API_PREFIX - required
HOST - required
PORT - required
CORS_ORIGINS - required

Frontend (.env):
VITE_API_BASE_URL - required

No production secrets are present in this repository.

---

# Configuration Files

backend/pyproject.toml - Python project + Ruff config
backend/ruff.toml - Lint rules
frontend/package.json - Node dependencies and scripts
frontend/tsconfig.json - TypeScript compiler config
frontend/vite.config.ts - Vite build config
frontend/.eslintrc.cjs - ESLint rules
frontend/.prettierrc - Formatting rules
.github/workflows/ci.yml - CI pipeline

---

# Scripts

Backend: ruff check . (lint)
Frontend: npm run dev, npm run build, npm run lint, npm run format

No Docker commands are used.

---

# Testing

Unit tests: Not yet added
Integration tests: Not yet added
Coverage: 0%
Pending tests: Health endpoint test, frontend render test

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

Authentication: Not yet implemented (Phase 2)
Authorization: Not yet implemented
Secrets: .env files git-ignored
Validation: Pydantic on backend
Rate limiting: Not yet implemented
Logging: Basic stdout logging configured

---

# Performance

No caching, database, or background jobs implemented yet.

---

# Known Issues

None currently.

---

# Technical Debt

None currently.

---

# Future Improvements

To be tracked as modules progress.

---

# Next Module

Module: Phase 2 - Authentication

Objectives: JWT-based auth, roles, permissions, user profile, PostgreSQL user table.

Expected deliverables: Registration/login endpoints, protected routes, frontend auth context.
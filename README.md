# Forex AI Analyst

An AI-powered market analyst for Forex and Gold (XAU/USD) — built to monitor markets, explain what it sees, and help you evaluate trading ideas with evidence instead of hype.

## What this is

This project watches live currency and gold price action, runs it through a layered feature-engineering and machine-learning pipeline, and produces analysis you can inspect, question, and backtest. Every recommendation the system makes comes with its reasoning attached: the trend it detected, the indicators that support it, the risk involved, the expected reward, and the conditions under which the idea would be invalidated.

## What this is not

This is not a signal-selling service, a "guaranteed win" bot, or a gambling tool. It does not place trades on your behalf unless you explicitly enable and configure an execution module in a future version, and even then it ships with that capability disabled by default. The goal is better-informed decisions, not blind automation.

## Core principles

**Explainability over black boxes.** Every AI output separates prediction, analysis, recommendation, and execution as distinct concepts. A model's confidence score is never presented as a promise.

**Free and open-source by default.** Every tool, library, and service used in this project was chosen because a genuinely free option existed and was sufficient. Where a paid service would have been more convenient, it was rejected in favor of a free alternative, and that decision is documented. Core functionality never depends on a paid subscription.

**No unnecessary infrastructure.** No Docker Desktop, no proprietary cloud lock-in, no license fees. You can clone this repository and run the entire stack on a personal laptop.

**Built one module at a time.** The system is developed and documented in discrete, testable phases — project scaffolding, authentication, market data, the database layer, feature engineering, backtesting, the AI engine, the decision engine, paper trading, an (initially disabled) execution engine, and finally a full trading dashboard. Each phase is production-quality on its own.

## Technology

- **Frontend:** React, TypeScript, Vite, Material UI
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL (with TimescaleDB for time-series market data)
- **AI/ML:** scikit-learn, PyTorch, XGBoost, LightGBM, pandas, NumPy
- **Real-time:** WebSockets
- **Infrastructure:** Native local development, GitHub Actions — no Docker Desktop, no paid cloud dependency for core functionality

See `PROJECT.md` for the current build state, completed modules, database schema, API reference, and exact local setup instructions — that document is updated after every development phase and is the single source of truth for "what exists right now."

## Status

Actively under development, module by module. Check `PROJECT.md` for current progress.

## License

To be determined.
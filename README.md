# Forex AI Analyst

An AI-powered market analyst for Forex and Gold (XAU/USD) — built to monitor markets, explain what it sees, and help you evaluate trading ideas with evidence instead of hype.

## What this is

This project watches live currency and gold price action, runs it through a layered feature-engineering and machine-learning pipeline, and produces analysis you can inspect, question, and backtest. Every recommendation the system makes comes with its reasoning attached: the trend it detected, the indicators that support it, the risk involved, the expected reward, and the conditions under which the idea would be invalidated.

## What this is not

This is not a signal-selling service, a "guaranteed win" bot, or a gambling tool. It does not place trades on your behalf — the execution engine ships disabled by default, with no broker connected at all, and enabling it changes nothing about that, since no broker integration exists yet.

## Core principles

**Explainability over black boxes.** Every AI output separates prediction, analysis, recommendation, and execution as distinct concepts. A model's confidence score is never presented as a promise, and the system explicitly recommends "no trade" when the evidence doesn't clear a minimum confidence and reward-to-risk bar.

**Free and open-source by default.** Every tool, library, and service used in this project was chosen because a genuinely free option existed and was sufficient. Core functionality has never depended on a paid subscription, from the database to the AI models to the market data feed.

**No unnecessary infrastructure.** No Docker Desktop, no proprietary cloud lock-in, no license fees. Clone this repository and run the entire stack on a personal laptop.

**Built one module at a time.** The system was developed and documented in eleven discrete, testable phases — project scaffolding, authentication, market data, the database layer, feature engineering, backtesting, the AI engine, the decision engine, paper trading, an (intentionally disabled) execution engine, and finally this dashboard.

## What's actually in here

- Live streaming prices and historical candles for major forex pairs and Gold, via a free-tier market data provider
- An in-house-built technical indicator and price-action engine (no third-party TA library dependency)
- A rule-based backtesting engine with realistic spread/slippage/commission modeling and a full statistics suite
- Six locally-trained ML models (trend, entry quality, confidence, risk, reward, market regime) — no external AI API calls, ever
- A decision engine that combines those models into an explainable recommendation, never a bare buy/sell
- A real paper trading simulator with live stop-loss/take-profit execution against streaming prices
- An architecturally-complete but functionally inert execution engine, ready for a future broker integration that doesn't exist yet
- A full dashboard tying all of it together

## Technology

- **Frontend:** React, TypeScript, Vite, Material UI, TradingView Lightweight Charts, Recharts
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL with TimescaleDB for time-series market data
- **AI/ML:** scikit-learn, XGBoost, LightGBM, pandas, NumPy
- **Real-time:** WebSockets, Redis pub/sub
- **Infrastructure:** Native local development, GitHub Actions — no Docker Desktop, no paid cloud dependency anywhere

See `PROJECT.md` for the exact database schema, API reference, environment setup, and known limitations — that document reflects the final, complete state of the build.

## Status

Feature-complete across all 11 planned phases. Automated test coverage is the clear next priority beyond the original plan — see `PROJECT.md`'s Technical Debt section.

## License

To be determined.
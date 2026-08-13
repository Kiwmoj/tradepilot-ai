# TradePilot AI

**Autonomous market-analysis and paper-trading agent.**

TradePilot AI continuously monitors real market data, analyzes markets using configurable strategies and AI-assisted analysis, manages a simulated portfolio, performs risk management, backtests strategies, and provides a complete trading dashboard.

> **IMPORTANT:** This system is designed for **paper trading and research only**.  
> It does **not** execute real-money trades or connect to live brokerage order routing.  
> A clearly separated `BrokerAdapter` interface exists for future authorized integrations.

---

## Architecture

```
tradepilot-ai/
├── frontend/          # React + TypeScript + Tailwind (Vite)
├── backend/           # FastAPI + SQLAlchemy (async) + Pydantic
├── worker/            # Background agent execution loop
├── database/          # Migrations / SQL helpers
├── tests/             # Unit + integration tests
├── docs/
├── scripts/
├── docker-compose.yml
└── .env.example
```

### Core components

| Component | Description |
|-----------|-------------|
| **Market Data Provider** | Pluggable interface (`mock`, Alpha Vantage, etc.) |
| **Paper Trading Engine** | Full simulated brokerage: cash, positions, orders, fills, P/L |
| **Strategies** | MA Crossover, RSI, Momentum, Mean Reversion (modular) |
| **Risk Manager** | Max position, exposure, daily loss, drawdown, cooldown, etc. |
| **Trading Agent** | Autonomous loop: data → signals → risk → paper execution |
| **AI Analyst** | Structured market commentary (rule-based + optional LLM) |
| **Backtesting Engine** | Historical simulation with equity curve & metrics |
| **Broker Adapter** | Stub interface – live trading deliberately locked |

---

## Tech Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts, Zustand, Vite
- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2 (async), Pydantic v2
- **Database:** PostgreSQL 16
- **Worker:** Async Python loop
- **Auth:** JWT + bcrypt password hashing
- **Containers:** Docker + docker-compose

---

## Quick Start (Docker)

```bash
# 1. Clone and enter the repository
git clone https://github.com/Kiwmoj/tradepilot-ai.git
cd tradepilot-ai

# 2. Create environment file
cp .env.example .env
# Edit SECRET_KEY and any API keys as needed

# 3. Start the full stack
docker compose up --build

# Services:
# - Frontend:  http://localhost:5173
# - Backend:   http://localhost:8000
# - API docs:  http://localhost:8000/docs
# - Postgres:  localhost:5432
```

Default paper starting cash: **$100,000**.

---

## Local Development (without Docker)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- Redis (optional)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DATABASE_URL=postgresql+asyncpg://tradepilot:change-me@localhost:5432/tradepilot
export SECRET_KEY=dev-secret-key-change-in-production-min-32-chars!!

uvicorn app.main:app --reload --port 8000
```

### Worker

```bash
cd worker
export PYTHONPATH=../backend:$PYTHONPATH
python -m app.main
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

See `.env.example` for the full list. Critical ones:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key (min 32 chars) |
| `DATABASE_URL` | Async PostgreSQL connection string |
| `MARKET_DATA_PROVIDER` | `mock` (default) / `alpha_vantage` / … |
| `ALPHA_VANTAGE_API_KEY` | Optional real market data |
| `AI_ENABLED` / `OPENAI_API_KEY` | Optional LLM analysis |
| `PAPER_STARTING_CASH` | Virtual starting capital |

**Never commit `.env` or real API keys.**

---

## Paper Trading

1. Register / login via the frontend.
2. A paper portfolio is created automatically with the configured starting cash.
3. Place manual orders from the Portfolio / Orders pages, or let the agent trade.
4. All orders pass through the **Risk Manager**.
5. Positions, cash, realized/unrealized P/L, and full transaction history are tracked.

Emergency Stop immediately prevents new trades.

---

## Strategies

| Strategy | Key idea |
|----------|----------|
| `ma_crossover` | Fast/slow moving-average cross |
| `rsi` | Relative Strength Index oversold/overbought |
| `momentum` | Rate-of-change / trend strength |
| `mean_reversion` | Price deviation from mean |

---

## Backtesting

Select symbol, strategy, date range, capital and position size.  
Metrics returned: total return, win rate, profit factor, max drawdown, Sharpe (when appropriate), equity curve.

**Backtesting does not guarantee future performance.**

---

## Security

- Passwords hashed with bcrypt
- JWT access + refresh tokens
- CORS restricted to configured origins
- Security headers middleware
- Parameterized SQL (SQLAlchemy)
- Secrets only via environment variables
- Input validation via Pydantic

---

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest -v --cov=app
```

GitHub Actions workflow (`.github/workflows/tests.yml`) runs the suite on push/PR.

---

## Broker Integration (Future)

The `BrokerAdapter` interface defines the methods for future integration. The UI shows:

```
Broker: Not Connected
Live Trading: Locked
```

No brokerage credentials are requested or stored by this application.

---

## License

MIT – see [LICENSE](LICENSE).

---

## Disclaimer

TradePilot AI is an educational and research tool.  
It is **not** financial advice. Paper-trading results and AI analysis are **not** guarantees of future performance.  
Do your own research and consult licensed professionals before making any real investment decisions.

"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    portfolio,
    market,
    watchlist,
    strategies,
    agent,
    risk,
    backtest,
    ai,
    broker,
    logs,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Paper Portfolio"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(agent.router, prefix="/agent", tags=["Trading Agent"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Management"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["Backtesting"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Analyst"])
api_router.include_router(broker.router, prefix="/broker", tags=["Broker Integration"])
api_router.include_router(logs.router, prefix="/logs", tags=["Agent Logs"])

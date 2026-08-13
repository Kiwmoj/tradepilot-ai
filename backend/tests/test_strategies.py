"""Unit tests for trading strategies."""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.schemas.market import OHLCVBar
from app.services.strategies import get_strategy, list_strategies
from app.models.strategy import SignalAction


def make_bars(n: int = 100, start_price: float = 100.0) -> list[OHLCVBar]:
    bars = []
    price = start_price
    t = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for i in range(n):
        price = price * (1.0 + 0.001 * ((i % 7) - 3))
        bars.append(
            OHLCVBar(
                timestamp=t + timedelta(days=i),
                open=Decimal(str(round(price * 0.99, 4))),
                high=Decimal(str(round(price * 1.01, 4))),
                low=Decimal(str(round(price * 0.98, 4))),
                close=Decimal(str(round(price, 4))),
                volume=1_000_000 + i * 1000,
            )
        )
    return bars


def test_list_strategies():
    strategies = list_strategies()
    assert len(strategies) >= 4
    types = {s["type"] for s in strategies}
    assert "ma_crossover" in types
    assert "rsi" in types
    assert "momentum" in types
    assert "mean_reversion" in types


@pytest.mark.parametrize("name", ["ma_crossover", "rsi", "momentum", "mean_reversion"])
def test_strategy_returns_valid_signal(name):
    strategy = get_strategy(name)
    bars = make_bars(120)
    result = strategy.generate_signal("AAPL", bars)
    assert result.symbol == "AAPL"
    assert result.action in (SignalAction.BUY, SignalAction.SELL, SignalAction.HOLD)
    assert 0 <= float(result.strength) <= 1
    assert result.reasoning
    assert result.strategy_name
    assert result.timestamp


def test_insufficient_bars_hold():
    strategy = get_strategy("ma_crossover")
    bars = make_bars(5)
    result = strategy.generate_signal("TEST", bars)
    assert result.action == SignalAction.HOLD

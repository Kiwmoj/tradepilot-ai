"""Shared pytest fixtures."""

import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.schemas.market import OHLCVBar, Quote


@pytest.fixture
def sample_bars():
    bars = []
    price = 100.0
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for i in range(100):
        price *= 1.001
        bars.append(
            OHLCVBar(
                timestamp=t0.replace(day=min(28, 1 + i % 27)),
                open=Decimal(str(round(price * 0.995, 4))),
                high=Decimal(str(round(price * 1.01, 4))),
                low=Decimal(str(round(price * 0.99, 4))),
                close=Decimal(str(round(price, 4))),
                volume=1_000_000,
            )
        )
    return bars


@pytest.fixture
def sample_quote():
    return Quote(
        symbol="AAPL",
        price=Decimal("190.50"),
        open=Decimal("189.00"),
        high=Decimal("191.20"),
        low=Decimal("188.50"),
        previous_close=Decimal("189.80"),
        volume=50_000_000,
        change=Decimal("0.70"),
        change_pct=Decimal("0.37"),
        timestamp=datetime.now(timezone.utc),
        provider="mock",
    )

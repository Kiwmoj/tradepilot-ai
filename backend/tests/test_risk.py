"""Risk manager unit tests."""

from decimal import Decimal
from datetime import datetime, timezone

from app.models.portfolio import OrderSide, Portfolio, Position
from app.services.risk.manager import RiskManager


def _portfolio(cash: float = 100_000) -> Portfolio:
    p = Portfolio()
    p.cash_balance = Decimal(str(cash))
    p.starting_cash = Decimal(str(cash))
    return p


def _position(symbol: str, qty: float, cost: float, price: float) -> Position:
    pos = Position()
    pos.symbol = symbol
    pos.quantity = Decimal(str(qty))
    pos.average_cost = Decimal(str(cost))
    pos.current_price = Decimal(str(price))
    pos.is_open = True
    return pos


def test_approve_normal_buy():
    rm = RiskManager()
    decision = rm.evaluate_order(
        portfolio=_portfolio(),
        positions=[],
        side=OrderSide.BUY,
        symbol="AAPL",
        quantity=Decimal("10"),
        price=Decimal("150"),
    )
    assert decision.approved is True


def test_reject_zero_quantity():
    rm = RiskManager()
    decision = rm.evaluate_order(
        portfolio=_portfolio(),
        positions=[],
        side=OrderSide.BUY,
        symbol="AAPL",
        quantity=Decimal("0"),
        price=Decimal("150"),
    )
    assert decision.approved is False
    assert any("positive" in r.lower() for r in decision.reasons)


def test_reject_max_open_positions():
    rm = RiskManager()
    positions = [_position(f"S{i}", 1, 100, 100) for i in range(10)]
    decision = rm.evaluate_order(
        portfolio=_portfolio(),
        positions=positions,
        side=OrderSide.BUY,
        symbol="NEW",
        quantity=Decimal("1"),
        price=Decimal("50"),
    )
    assert decision.approved is False
    assert any("max open" in r.lower() for r in decision.reasons)

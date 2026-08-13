"""Risk management engine – every paper trade must pass through here."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.portfolio import OrderSide, Portfolio, Position
from app.models.risk import RiskConfig

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class RiskDecision:
    approved: bool
    reasons: List[str] = field(default_factory=list)
    suggested_quantity: Optional[Decimal] = None


class RiskManager:
    """Evaluates proposed orders against configurable risk rules."""

    def __init__(self, config: Optional[RiskConfig] = None) -> None:
        self.config = config

    def _cfg(self, attr: str, default):
        if self.config is not None:
            return getattr(self.config, attr, default)
        return getattr(settings, f"risk_{attr}", default)

    def evaluate_order(
        self,
        *,
        portfolio: Portfolio,
        positions: List[Position],
        side: OrderSide,
        symbol: str,
        quantity: Decimal,
        price: Decimal,
        recent_trade_count_today: int = 0,
        last_trade_at: Optional[datetime] = None,
        equity_peak: Optional[Decimal] = None,
        current_equity: Optional[Decimal] = None,
        day_start_equity: Optional[Decimal] = None,
    ) -> RiskDecision:
        reasons: List[str] = []
        cash = Decimal(str(portfolio.cash_balance))
        qty = Decimal(str(quantity))
        px = Decimal(str(price))
        notional = qty * px

        # 1. Basic sanity
        if qty <= 0:
            return RiskDecision(False, ["Quantity must be positive"])
        if px <= 0:
            return RiskDecision(False, ["Price must be positive"])

        # Portfolio value approximation
        positions_value = sum(
            (Decimal(str(p.quantity)) * Decimal(str(p.current_price or p.average_cost)))
            for p in positions
            if p.is_open
        )
        total_equity = cash + positions_value
        if current_equity is not None:
            total_equity = Decimal(str(current_equity))

        # 2. Max open positions (for new buys)
        max_pos = int(self._cfg("max_open_positions", 10))
        open_count = sum(1 for p in positions if p.is_open and Decimal(str(p.quantity)) > 0)
        existing = next((p for p in positions if p.symbol == symbol and p.is_open), None)
        if side == OrderSide.BUY and existing is None and open_count >= max_pos:
            reasons.append(f"Max open positions reached ({max_pos})")

        # 3. Max position size %
        max_pos_pct = float(self._cfg("max_position_pct", 10.0))
        if side == OrderSide.BUY and total_equity > 0:
            max_notional = total_equity * Decimal(str(max_pos_pct / 100))
            current_pos_value = Decimal("0")
            if existing:
                current_pos_value = Decimal(str(existing.quantity)) * Decimal(
                    str(existing.current_price or existing.average_cost)
                )
            if current_pos_value + notional > max_notional:
                reasons.append(
                    f"Position size would exceed {max_pos_pct}% of equity"
                )

        # 4. Cash check for buys
        if side == OrderSide.BUY and notional > cash:
            reasons.append(f"Insufficient cash (need {notional:.2f}, have {cash:.2f})")

        # 5. Max portfolio exposure
        max_exp = float(self._cfg("max_portfolio_exposure_pct", 80.0))
        if side == OrderSide.BUY and total_equity > 0:
            new_positions_value = positions_value + notional
            exposure_pct = float(new_positions_value / total_equity * 100)
            if exposure_pct > max_exp:
                reasons.append(f"Portfolio exposure would exceed {max_exp}%")

        # 6. Max trades per day
        max_trades = int(self._cfg("max_trades_per_day", 20))
        if recent_trade_count_today >= max_trades:
            reasons.append(f"Max trades per day reached ({max_trades})")

        # 7. Cooldown
        cooldown = int(self._cfg("trade_cooldown_seconds", 300))
        if last_trade_at is not None and cooldown > 0:
            elapsed = (datetime.now(timezone.utc) - last_trade_at).total_seconds()
            if elapsed < cooldown:
                reasons.append(f"Trade cooldown active ({int(cooldown - elapsed)}s remaining)")

        if reasons:
            return RiskDecision(False, reasons)
        return RiskDecision(True, [])

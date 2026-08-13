"""Price momentum strategy."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from app.models.strategy import SignalAction
from app.schemas.market import OHLCVBar
from app.services.strategies.base import BaseStrategy, StrategyResult
from app.services.strategies.indicators import bars_to_df, last_valid, momentum


class MomentumStrategy(BaseStrategy):
    name = "Momentum"
    strategy_type = "momentum"
    default_params: Dict[str, Any] = {
        "lookback": 10,
        "threshold_pct": 3.0,
    }

    def generate_signal(self, symbol: str, bars: List[OHLCVBar]) -> StrategyResult:
        lookback = int(self.params.get("lookback", 10))
        threshold = float(self.params.get("threshold_pct", 3.0))

        df = bars_to_df(bars)
        if len(df) < lookback + 2:
            return self._hold(symbol, f"Insufficient data for momentum({lookback})")

        df["mom"] = momentum(df["close"], lookback)
        mom_val = last_valid(df["mom"])
        price = float(df["close"].iloc[-1])
        if mom_val is None:
            return self._hold(symbol, "Momentum could not be calculated")

        indicators = {
            "momentum_pct": round(mom_val, 4),
            "lookback": lookback,
            "threshold_pct": threshold,
            "price": round(price, 4),
        }

        if mom_val >= threshold:
            strength = min(1.0, mom_val / (threshold * 3))
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.BUY,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"Strong positive momentum: {mom_val:.2f}% over {lookback} periods",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        if mom_val <= -threshold:
            strength = min(1.0, abs(mom_val) / (threshold * 3))
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.SELL,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"Strong negative momentum: {mom_val:.2f}% over {lookback} periods",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        return StrategyResult(
            symbol=symbol,
            action=SignalAction.HOLD,
            strength=Decimal("0.1"),
            indicator_values=indicators,
            reasoning=f"Momentum {mom_val:.2f}% is within threshold ±{threshold}%",
            strategy_name=self.name,
            strategy_type=self.strategy_type,
        )

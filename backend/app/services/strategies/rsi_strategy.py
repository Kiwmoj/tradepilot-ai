"""RSI overbought/oversold strategy."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from app.models.strategy import SignalAction
from app.schemas.market import OHLCVBar
from app.services.strategies.base import BaseStrategy, StrategyResult
from app.services.strategies.indicators import bars_to_df, last_valid, rsi


class RSIStrategy(BaseStrategy):
    name = "RSI"
    strategy_type = "rsi"
    default_params: Dict[str, Any] = {
        "period": 14,
        "oversold": 30,
        "overbought": 70,
    }

    def generate_signal(self, symbol: str, bars: List[OHLCVBar]) -> StrategyResult:
        period = int(self.params.get("period", 14))
        oversold = float(self.params.get("oversold", 30))
        overbought = float(self.params.get("overbought", 70))

        df = bars_to_df(bars)
        if len(df) < period + 5:
            return self._hold(symbol, f"Insufficient data for RSI({period})")

        df["rsi"] = rsi(df["close"], period)
        current_rsi = last_valid(df["rsi"])
        price = float(df["close"].iloc[-1])
        if current_rsi is None:
            return self._hold(symbol, "RSI could not be calculated")

        indicators = {
            "rsi": round(current_rsi, 2),
            "period": period,
            "oversold": oversold,
            "overbought": overbought,
            "price": round(price, 4),
        }

        if current_rsi < oversold:
            strength = min(1.0, (oversold - current_rsi) / oversold)
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.BUY,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"RSI({period})={current_rsi:.1f} is oversold (<{oversold})",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        if current_rsi > overbought:
            strength = min(1.0, (current_rsi - overbought) / (100 - overbought))
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.SELL,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"RSI({period})={current_rsi:.1f} is overbought (>{overbought})",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        return StrategyResult(
            symbol=symbol,
            action=SignalAction.HOLD,
            strength=Decimal("0.1"),
            indicator_values=indicators,
            reasoning=f"RSI({period})={current_rsi:.1f} is neutral",
            strategy_name=self.name,
            strategy_type=self.strategy_type,
        )

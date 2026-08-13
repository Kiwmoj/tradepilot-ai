"""Moving Average Crossover strategy."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from app.models.strategy import SignalAction
from app.schemas.market import OHLCVBar
from app.services.strategies.base import BaseStrategy, StrategyResult
from app.services.strategies.indicators import bars_to_df, last_valid, sma


class MACrossoverStrategy(BaseStrategy):
    name = "Moving Average Crossover"
    strategy_type = "ma_crossover"
    default_params: Dict[str, Any] = {
        "fast_period": 10,
        "slow_period": 30,
    }

    def generate_signal(self, symbol: str, bars: List[OHLCVBar]) -> StrategyResult:
        fast = int(self.params.get("fast_period", 10))
        slow = int(self.params.get("slow_period", 30))
        if fast >= slow:
            return self._hold(symbol, "Invalid parameters: fast_period must be < slow_period")

        df = bars_to_df(bars)
        if len(df) < slow + 2:
            return self._hold(symbol, f"Insufficient data ({len(df)} bars, need {slow + 2})")

        df["fast"] = sma(df["close"], fast)
        df["slow"] = sma(df["close"], slow)
        df = df.dropna()
        if len(df) < 2:
            return self._hold(symbol, "Not enough data after MA calculation")

        prev_fast, prev_slow = float(df["fast"].iloc[-2]), float(df["slow"].iloc[-2])
        curr_fast, curr_slow = float(df["fast"].iloc[-1]), float(df["slow"].iloc[-1])
        price = float(df["close"].iloc[-1])

        indicators = {
            "fast_ma": round(curr_fast, 4),
            "slow_ma": round(curr_slow, 4),
            "price": round(price, 4),
            "fast_period": fast,
            "slow_period": slow,
        }

        if prev_fast <= prev_slow and curr_fast > curr_slow:
            strength = min(1.0, abs(curr_fast - curr_slow) / price * 50)
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.BUY,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=(
                    f"Bullish MA crossover: fast({fast})={curr_fast:.2f} crossed above "
                    f"slow({slow})={curr_slow:.2f}"
                ),
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        if prev_fast >= prev_slow and curr_fast < curr_slow:
            strength = min(1.0, abs(curr_fast - curr_slow) / price * 50)
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.SELL,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=(
                    f"Bearish MA crossover: fast({fast})={curr_fast:.2f} crossed below "
                    f"slow({slow})={curr_slow:.2f}"
                ),
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        trend = "bullish" if curr_fast > curr_slow else "bearish"
        return StrategyResult(
            symbol=symbol,
            action=SignalAction.HOLD,
            strength=Decimal("0.1"),
            indicator_values=indicators,
            reasoning=f"No crossover. Current trend appears {trend}.",
            strategy_name=self.name,
            strategy_type=self.strategy_type,
        )

"""Bollinger Band mean-reversion strategy."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from app.models.strategy import SignalAction
from app.schemas.market import OHLCVBar
from app.services.strategies.base import BaseStrategy, StrategyResult
from app.services.strategies.indicators import bars_to_df, bollinger_bands, last_valid


class MeanReversionStrategy(BaseStrategy):
    name = "Mean Reversion"
    strategy_type = "mean_reversion"
    default_params: Dict[str, Any] = {
        "window": 20,
        "num_std": 2.0,
    }

    def generate_signal(self, symbol: str, bars: List[OHLCVBar]) -> StrategyResult:
        window = int(self.params.get("window", 20))
        num_std = float(self.params.get("num_std", 2.0))

        df = bars_to_df(bars)
        if len(df) < window + 2:
            return self._hold(symbol, f"Insufficient data for BB({window})")

        lower, mid, upper = bollinger_bands(df["close"], window, num_std)
        df["bb_lower"] = lower
        df["bb_mid"] = mid
        df["bb_upper"] = upper

        price = float(df["close"].iloc[-1])
        lo = last_valid(df["bb_lower"])
        mi = last_valid(df["bb_mid"])
        up = last_valid(df["bb_upper"])
        if lo is None or mi is None or up is None:
            return self._hold(symbol, "Bollinger Bands could not be calculated")

        indicators = {
            "price": round(price, 4),
            "bb_lower": round(lo, 4),
            "bb_mid": round(mi, 4),
            "bb_upper": round(up, 4),
            "window": window,
            "num_std": num_std,
        }

        if price < lo:
            strength = min(1.0, (lo - price) / lo * 20)
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.BUY,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"Price {price:.2f} below lower Bollinger Band {lo:.2f} – mean reversion long",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        if price > up:
            strength = min(1.0, (price - up) / up * 20)
            return StrategyResult(
                symbol=symbol,
                action=SignalAction.SELL,
                strength=Decimal(str(round(strength, 4))),
                indicator_values=indicators,
                reasoning=f"Price {price:.2f} above upper Bollinger Band {up:.2f} – mean reversion short",
                strategy_name=self.name,
                strategy_type=self.strategy_type,
            )

        return StrategyResult(
            symbol=symbol,
            action=SignalAction.HOLD,
            strength=Decimal("0.1"),
            indicator_values=indicators,
            reasoning=f"Price {price:.2f} inside Bollinger Bands [{lo:.2f}, {up:.2f}]",
            strategy_name=self.name,
            strategy_type=self.strategy_type,
        )

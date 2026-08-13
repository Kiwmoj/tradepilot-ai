"""Strategy interface and shared result type."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.models.strategy import SignalAction
from app.schemas.market import OHLCVBar


@dataclass
class StrategyResult:
    symbol: str
    action: SignalAction
    strength: Decimal  # 0–1
    indicator_values: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    strategy_name: str = ""
    strategy_type: str = ""

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "action": self.action.value,
            "strength": float(self.strength),
            "indicator_values": self.indicator_values,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
            "strategy_name": self.strategy_name,
            "strategy_type": self.strategy_type,
        }


class BaseStrategy(ABC):
    name: str = "base"
    strategy_type: str = "base"
    default_params: Dict[str, Any] = {}

    def __init__(self, params: Optional[Dict[str, Any]] = None) -> None:
        self.params = {**self.default_params, **(params or {})}

    @abstractmethod
    def generate_signal(self, symbol: str, bars: List[OHLCVBar]) -> StrategyResult:
        """Produce a BUY / SELL / HOLD signal from OHLCV bars."""
        ...

    def _hold(self, symbol: str, reason: str, indicators: Optional[dict] = None) -> StrategyResult:
        return StrategyResult(
            symbol=symbol,
            action=SignalAction.HOLD,
            strength=Decimal("0"),
            indicator_values=indicators or {},
            reasoning=reason,
            strategy_name=self.name,
            strategy_type=self.strategy_type,
        )

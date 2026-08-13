"""Strategy registry and factory."""

from __future__ import annotations

from typing import Any, Dict, Type

from app.services.strategies.base import BaseStrategy
from app.services.strategies.ma_crossover import MACrossoverStrategy
from app.services.strategies.mean_reversion import MeanReversionStrategy
from app.services.strategies.momentum import MomentumStrategy
from app.services.strategies.rsi_strategy import RSIStrategy

STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "ma_crossover": MACrossoverStrategy,
    "rsi": RSIStrategy,
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
}


def get_strategy(strategy_type: str, params: Dict[str, Any] | None = None) -> BaseStrategy:
    cls = STRATEGY_REGISTRY.get(strategy_type)
    if cls is None:
        raise ValueError(
            f"Unknown strategy_type '{strategy_type}'. "
            f"Available: {list(STRATEGY_REGISTRY.keys())}"
        )
    return cls(params=params)


def list_strategies() -> list[dict]:
    return [
        {
            "type": key,
            "name": cls.name,
            "default_params": cls.default_params,
        }
        for key, cls in STRATEGY_REGISTRY.items()
    ]

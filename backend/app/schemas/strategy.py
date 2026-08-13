"""Strategy schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.strategy import SignalAction


class StrategyConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    strategy_type: str = Field(..., pattern="^(ma_crossover|rsi|momentum|mean_reversion)$")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    symbols: List[str] = Field(default_factory=list)
    is_enabled: bool = True


class StrategyConfigOut(BaseModel):
    id: int
    name: str
    strategy_type: str
    parameters: Dict[str, Any]
    symbols: List[str]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SignalOut(BaseModel):
    id: int
    strategy_name: str
    strategy_type: str
    symbol: str
    action: SignalAction
    strength: Decimal
    indicator_values: Dict[str, Any]
    reasoning: Optional[str]
    price_at_signal: Optional[Decimal]
    was_executed: bool
    reject_reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class StrategyInfo(BaseModel):
    type: str
    name: str
    default_params: Dict[str, Any]


class StrategySignalOut(BaseModel):
    symbol: str
    action: SignalAction
    strength: Decimal
    indicator_values: Dict[str, Any]
    reasoning: str
    timestamp: datetime
    strategy_name: str
    strategy_type: str

"""Market data schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class Quote(BaseModel):
    symbol: str
    price: Decimal
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    volume: Optional[int] = None
    change: Optional[Decimal] = None
    change_pct: Optional[Decimal] = None
    timestamp: datetime
    market_status: Optional[str] = None
    provider: str = "unknown"


class OHLCVBar(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class MarketStatus(BaseModel):
    is_open: bool
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None
    timezone: str = "America/New_York"
    exchange: str = "US"


class HistoricalRequest(BaseModel):
    symbol: str
    start_date: date
    end_date: date
    interval: str = Field(default="1d", pattern="^(1m|5m|15m|1h|1d)$")


class HistoricalResponse(BaseModel):
    symbol: str
    interval: str
    bars: List[OHLCVBar]
    provider: str
    retrieved_at: datetime

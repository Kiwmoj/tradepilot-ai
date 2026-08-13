"""Backtest run storage."""

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    strategy_type: Mapped[str] = mapped_column(String(50), nullable=False)
    strategy_params: Mapped[dict] = mapped_column(JSON, default=dict)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    starting_capital: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("100000"))
    position_size_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=10.0)
    total_return_pct: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="backtest_runs")

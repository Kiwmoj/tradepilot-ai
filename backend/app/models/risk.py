"""Per-user risk configuration."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RiskConfig(Base):
    __tablename__ = "risk_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    max_position_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=10.0)
    max_portfolio_exposure_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=80.0)
    max_risk_per_trade_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=2.0)
    max_daily_loss_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=5.0)
    max_drawdown_pct: Mapped[float] = mapped_column(Numeric(8, 4), default=15.0)
    max_open_positions: Mapped[int] = mapped_column(Integer, default=10)
    require_stop_loss: Mapped[bool] = mapped_column(Boolean, default=True)
    trade_cooldown_seconds: Mapped[int] = mapped_column(Integer, default=300)
    max_trades_per_day: Mapped[int] = mapped_column(Integer, default=20)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="risk_configs")

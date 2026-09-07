from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class UserBehavior(Base):
    __tablename__ = "user_behavior"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), index=True, nullable=False
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"), index=True
    )
    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    traffic_source: Mapped[str] = mapped_column(String(100), nullable=False)

    customer = relationship("Customer", back_populates="behavior_events")
    product = relationship("Product", back_populates="behavior_events")

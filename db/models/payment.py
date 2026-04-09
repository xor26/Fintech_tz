import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, Text, JSON, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    uid: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)
    meta_data: Mapped[dict | None] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(20), default="pending")

    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    webhook_url: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)





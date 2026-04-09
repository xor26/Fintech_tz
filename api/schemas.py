from decimal import Decimal

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    description: str | None = None
    meta_data: dict = Field(default_factory=dict)
    webhook_url: HttpUrl


class PaymentCreateResponse(BaseModel):
    uid: UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    uid: UUID
    amount: Decimal
    currency: str

    description: str | None
    meta_data: dict | None

    status: str
    webhook_url: HttpUrl

    created_at: datetime
    processed_at: datetime | None = None

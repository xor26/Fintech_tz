from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, FastAPI, Header
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.schemas import PaymentCreateResponse, PaymentCreateRequest, PaymentResponse
from db.models.payment import Payment
from db.models.outbox import Outbox
from db.base import get_session, get_session_for_local

app = FastAPI()

X_API_KEY = "TRUST_ME_BRO_IM_AUTHORIZED"


def is_authorized(key: str) -> bool:
    return key == X_API_KEY


@app.post("/api/v1/payments", response_model=PaymentCreateResponse)
async def create_payment(
        payload: PaymentCreateRequest,
        idempotency_key: Annotated[str, Header()],
        x_api_key: Annotated[str, Header()],
        session: AsyncSession = Depends(get_session),
):
    if not is_authorized(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not today mr Hacker",
        )

    async with session.begin():
        payment = Payment(
            uid=uuid4(),
            idempotency_key=idempotency_key,
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            meta_data=payload.meta_data,
            status="pending",
            webhook_url=str(payload.webhook_url),
        )

        try:
            session.add(payment)
        except IntegrityError:
            return "fuck up"


        outbox = Outbox(
            event_type="payment_created",
            payload={
                "payment_uid": str(payment.uid),
                "amount": str(payload.amount),
                "currency": payload.currency,
                "webhook_url": str(payload.webhook_url),
            },
            status="pending",
        )
        session.add(outbox)
        await session.flush()
        resp = PaymentCreateResponse(
            uid=payment.uid,
            status=payment.status,
            created_at=payment.created_at,
        )

    return resp


@app.get("/api/v1/payments", response_model=list[PaymentResponse])
async def list_payments(x_api_key: Annotated[str, Header()], session: AsyncSession = Depends(get_session)):
    if not is_authorized(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not today mr Hacker",
        )
    result = await session.execute(select(Payment))
    payments = result.scalars().all()
    return [
        PaymentResponse(
            uid=p.uid,
            amount=p.amount,
            currency=p.currency,
            description=p.description,
            meta_data=dict(p.meta_data),
            status=p.status,
            webhook_url=p.webhook_url,
            created_at=p.created_at,
            processed_at=p.processed_at,
        )
        for p in payments
    ]


@app.get("/api/v1/payments/{uid}", response_model=PaymentResponse)
async def get_payment(
        uid: str | None,
        session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Payment).where(Payment.uid == uid)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


# todo delete
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

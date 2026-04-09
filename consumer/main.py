import os
import random
import logging
from datetime import datetime

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitRouter
from sqlalchemy import select

from consts import PAYMENTS_NEW_QUEUE, PAYMENTS_DLQ
from db.base import session_maker
from db.models.payment import Payment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBIT_URL = os.getenv("RABBIT_URL")

MAX_RETRIES = 3

broker = RabbitBroker(RABBIT_URL)
router = RabbitRouter()

broker.include_router(router)

app = FastStream(broker)


async def emulate_processing():
    await asyncio.sleep(random.uniform(2, 5))
    return "succeeded" if random.random() < 0.9 else "failed"


async def send_webhook(url: str, payload: dict):
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()


async def webhook_with_retry(url: str, payload: dict):
    delay = 1
    attempt = 1
    while attempt <= MAX_RETRIES:
        try:
            await send_webhook(url, payload)
            return True
        except Exception as e:
            logger.warning(f"Webhook attempt {attempt} failed: {e}")
            if attempt == MAX_RETRIES:
                return False
            await asyncio.sleep(delay)
            delay *= 2  # exponential waiting
            attempt += 1


@router.subscriber(PAYMENTS_NEW_QUEUE)
async def handle_payment(msg: dict):
    async with session_maker() as session:
        logger.info(f"Starting handling payment: {msg}")
        payment_uid = msg["payment_uid"]
        result = await session.execute(
            select(Payment).where(Payment.uid == payment_uid)
        )
        payment = result.scalar_one_or_none()
        status = await emulate_processing()
        payment.status = status
        payment.processed_at = datetime.utcnow()
        session.add(payment)
        payload = {
            "payment_uid": str(payment.uid),
            "status": payment.status,
        }
        webhook_url = payment.webhook_url
        await session.commit()

        is_send = await webhook_with_retry(webhook_url, payload)
        if not is_send:
            # отправка в DLQ
            await broker.publish(
                message=payload,
                queue=PAYMENTS_DLQ,
            )
            logger.error(f"Webhook failed, msg sent to DLQ: {payment_uid}")
        else:
            logger.info(f"Payment processed: {payment_uid} -> {status}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())

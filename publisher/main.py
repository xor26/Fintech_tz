import os
import asyncio
import logging

from faststream.rabbit import RabbitBroker
from sqlalchemy import select

from consts import PAYMENTS_NEW_QUEUE
from db.base import get_session
from db.models.outbox import Outbox

BATCH_SIZE = 50
MAX_RETRIES = 3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker = RabbitBroker(os.getenv("RABBIT_URL"))


async def fetch_batch(session):
    result = await session.execute(
        select(Outbox)
        .where(
            Outbox.status == "pending",
            Outbox.retry_count < MAX_RETRIES
        )
        .order_by(Outbox.created_at)
        .limit(BATCH_SIZE)
        .with_for_update(skip_locked=True)
    )
    return result.scalars().all()


async def process_event(event: Outbox):
    try:
        await broker.publish(
            message=event.payload,
            queue=PAYMENTS_NEW_QUEUE,
        )

        event.status = "sent"

        logger.info(f"Event sent: {event.uid}")

    except Exception as e:
        event.retry_count += 1
        if event.retry_count >= MAX_RETRIES:
            event.status = "failed"
            logger.error(f"Event failed: {event.uid}")


async def publish_loop():
    await broker.start()
    session = await anext(get_session())

    while True:
        async with session.begin():
            events = await fetch_batch(session)
            if not events:
                await asyncio.sleep(1)
                continue

            # тут надо прикинуть сколько у консумера займет обрабоать 50 сообщений и жать чуть больше этого времени
            await asyncio.sleep(1)

            for event in events:
                await process_event(event)


if __name__ == "__main__":
    asyncio.run(publish_loop())

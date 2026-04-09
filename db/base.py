import os

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(DATABASE_URL, echo=True)

session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


async def get_session():
    async with session_maker() as session:
        yield session


# todo delete
loc_engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/payments", echo=True)
local_session_maker = async_sessionmaker(
    bind=loc_engine,
    autoflush=False,
    autocommit=False,
)


async def get_session_for_local():
    async with local_session_maker() as session:
        yield session

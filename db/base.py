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

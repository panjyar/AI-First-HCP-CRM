from app.database.base import Base
from app.database.session import engine

# Import models so SQLAlchemy registers all tables before create_all runs.
from app.database import models  # noqa: F401


async def init_db() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

# Create async database connection
engine = create_async_engine(settings.DB_URL, echo=True)

# Create Session factory
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# DB Session
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# engine asíncrono, es el motor
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
)

# session factory asíncrona, es la fábrica de sesiones
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# engine síncrono para Celery workers
engine_sync = create_engine(
    settings.SQLALCHEMY_DATABASE_URI_SYNC,
    echo=True,
    future=True,
)

# session factory síncrona para Celery workers
SessionLocalSync = sessionmaker(
    bind=engine_sync,
    expire_on_commit=False
)

# base para modelos ORM
Base = declarative_base()

# dependencia para FastAPI, para inyectar la sesión de base de datos
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
    await session.close()

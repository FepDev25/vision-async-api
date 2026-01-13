from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
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

# base para modelos ORM
Base = declarative_base()

# dependencia para FastAPI, para inyectar la sesión de base de datos
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
    await session.close()

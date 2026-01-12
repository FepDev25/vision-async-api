import pytest
from app.core.config import settings


def test_settings_loaded():
    # verificar que las configuraciones se carguen correctamente desde el archivo .env
    assert settings.PROJECT_NAME
    assert settings.POSTGRES_SERVER == "localhost"
    assert settings.POSTGRES_PORT == 5433
    assert settings.POSTGRES_USER == "admin"
    assert settings.POSTGRES_DB == "vision_db"


def test_database_uri():
    # verificar la generación correcta de la URI de la base de datos
    uri = settings.SQLALCHEMY_DATABASE_URI
    assert "postgresql+asyncpg://" in uri
    assert "admin:password123" in uri
    assert "localhost:5433" in uri
    assert "vision_db" in uri


def test_minio_settings():
    # verificar la configuración de MinIO
    assert settings.MINIO_ENDPOINT == "localhost:9000"
    assert settings.MINIO_ACCESS_KEY == "minioadmin"
    assert settings.MINIO_BUCKET_NAME == "images-input"
    assert settings.MINIO_SECURE == False

from celery import Celery
from app.core.config import settings

# instanciar Celery
celery_app = Celery(
    "app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True
)

# configuración adicional
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    include=["app.worker"]  # Importar módulos con tareas
)

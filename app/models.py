from app.core.database import Base
from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
import uuid
import enum

# Estados posibles de una tarea
class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# Modelo de tarea para procesamiento de imágenes
class Task(Base):
    __tablename__ = 'tasks'
    
    # ID como UUID (no enteros autoincrementales)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # estado de la tarea
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    # nombre del archivo en MinIO
    filename = Column(String(255), nullable=False)
    # resultado del procesamiento (JSON nullable)
    result = Column(JSON, nullable=True)
    # timestamps automáticos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
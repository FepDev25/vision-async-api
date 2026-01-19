from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class TaskResponse(BaseModel):
    # Schema de respuesta para una tarea
    
    id: UUID
    status: str
    filename: str
    result: dict | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

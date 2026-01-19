from app.core.database import get_async_db
from app.services.storage import MinioService, MinioServiceError
from app.models import Task, TaskStatus
from app.schemas import TaskResponse
from app.worker import process_image
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid

router = APIRouter(
    prefix="/vision",
    tags=["vision"]
)


# Dependencia para MinioService
def get_minio_service() -> MinioService:
    return MinioService()

# Endpoint para analizar una imagen de forma asíncrona.
# 1. Valida que el archivo sea una imagen
# 2. Sube el archivo a MinIO
# 3. Crea una tarea en la base de datos
# 4. Encola la tarea para procesamiento
# 5. Retorna la tarea creada
@router.post("/analyze", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_image(file: UploadFile = File(...),

    db: AsyncSession = Depends(get_async_db),
    minio_service: MinioService = Depends(get_minio_service)):
    
    # Validar que el archivo es una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        
        # Generar un nombre único para el archivo
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Subir a MinIO
        stored_filename = minio_service.upload_file(file_content, unique_filename)
        
        # Crear la tarea en la base de datos
        task = Task(
            status=TaskStatus.PENDING,
            filename=stored_filename
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # Encolar la tarea para procesamiento
        process_image.delay(str(task.id))
        
        # Retornar la tarea creada
        return task
        
    except MinioServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al almacenar la imagen: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )

# Endpoint para consultar el estado de una tarea por su ID.
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_async_db)):
    
    # Buscar la tarea en la base de datos
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    # Si no existe, retornar 404
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {task_id} no encontrada"
        )
    
    return task

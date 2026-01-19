from app.core.celery_app import celery_app
from app.core.database import SessionLocalSync
from app.services.storage import MinioService
from app.models import Task, TaskStatus
import time
from uuid import UUID

# Procesa una imagen de forma asíncrona
# Args: task_id: ID de la tarea a procesar (UUID como string)
# Returns: bool: True si el procesamiento fue exitoso
@celery_app.task(name="process_image")
def process_image(task_id: str) -> bool:
    print(f"Procesando tarea {task_id}")
    
    # Abrir sesión síncrona de base de datos
    with SessionLocalSync() as db:
        # Buscar la tarea por ID
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        
        if not task:
            print(f"Tarea {task_id} no encontrada")
            return False
        
        # Actualizar status a PROCESSING
        task.status = TaskStatus.PROCESSING
        db.commit()
        
        # Bloque try/except para el procesamiento
        try:
            # Instanciar MinioService
            minio_service = MinioService()
            
            # Descargar la imagen
            print(f"Descargando imagen: {task.filename}")
            image_data = minio_service.get_file(task.filename)
            
            # Simular procesamiento con GPU
            print(f"Procesando imagen (simulación)...")
            time.sleep(5)
            
            # Transformar el nombre del archivo
            filename_parts = task.filename.rsplit('.', 1)
            if len(filename_parts) == 2:
                processed_filename = f"processed_{filename_parts[0]}.{filename_parts[1]}"
            else:
                processed_filename = f"processed_{task.filename}"
            
            # Subir el archivo procesado (por ahora los mismos bytes)
            print(f"Subiendo imagen procesada: {processed_filename}")
            minio_service.upload_file(image_data, processed_filename)
            
            # Actualizar la tarea como completada
            task.status = TaskStatus.COMPLETED
            task.result = {"processed_file": processed_filename}
            db.commit()
            
            print(f"Tarea {task_id} completada exitosamente")
            return True
            
        except Exception as e:
            # Actualizar la tarea como fallida
            print(f"Error procesando tarea {task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
            db.commit()
            
            return False

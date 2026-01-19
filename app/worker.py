from app.core.celery_app import celery_app
from app.core.database import SessionLocalSync
from app.services.storage import MinioService
from app.models import Task, TaskStatus
from uuid import UUID
import numpy as np
import cv2

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
            
            # Procesamiento con OpenCV (in-memory)
            print(f"Procesando imagen con OpenCV...")
            
            # Paso 1: Convertir bytes a numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Paso 2: Decodificar a imagen BGR
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("No se pudo decodificar la imagen")
            
            # Paso 3: Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Paso 4: Aplicar detección de bordes Canny
            edges = cv2.Canny(gray, 100, 200)
            
            # Paso 5: Codificar de vuelta a bytes (como PNG)
            # cv2.imencode devuelve (success, buffer) donde buffer es un array numpy
            success, buffer = cv2.imencode('.png', edges)
            
            if not success:
                raise ValueError("No se pudo codificar la imagen procesada")
            
            # Convertir el buffer numpy a bytes del PNG
            processed_image_data = bytes(buffer)
            
            # Transformar el nombre del archivo
            filename_parts = task.filename.rsplit('.', 1)
            if len(filename_parts) == 2:
                processed_filename = f"processed_{filename_parts[0]}.png"
            else:
                processed_filename = f"processed_{task.filename}.png"
            
            # Subir el archivo procesado
            minio_service.upload_file(processed_image_data, processed_filename)
            
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

from app.core.celery_app import celery_app

# Procesa una imagen de forma asíncrona.
# Args: task_id: ID de la tarea a procesar (UUID como string)
# Returns: bool: True si el procesamiento fue exitoso
@celery_app.task(name="process_image")
def process_image(task_id: str) -> bool:
    print(f"Procesando tarea {task_id}")
    return True

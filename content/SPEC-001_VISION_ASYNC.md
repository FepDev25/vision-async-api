# TICKET-01: Implementación de Pipeline de Procesamiento de Imágenes Asíncrono

Status: EN PROGRESO
Fecha Límite: Sprint Actual

## 1. Contexto y Objetivo

Actualmente, el procesamiento de imágenes en nuestros prototipos bloquea el hilo principal del servidor. Si un modelo de PyTorch tarda 5 segundos en inferir, la API deja de responder a otros usuarios durante ese tiempo.

Objetivo: Desacoplar la recepción de la imagen de su procesamiento. Necesitamos una arquitectura Non-blocking usando colas de tareas. El usuario debe recibir una respuesta inmediata (HTTP 202 Accepted) con un ID de seguimiento, mientras el trabajo pesado ocurre en segundo plano.

## 2. Stack Tecnológico Definido

* API: FastAPI (Python 3.10+)
* Cola de Mensajes (Broker): Redis (o RabbitMQ). Usaremos Redis por simplicidad inicial en Docker.
* Worker: Celery.
* Almacenamiento de Objetos: MinIO (Compatible con S3 API).
* Base de Datos: PostgreSQL (Para metadatos de tareas y usuarios).
* Librerías Clave: `boto3` (para MinIO), `opencv-python` / `torch` (para la lógica).

## 3. Arquitectura del Sistema

Cliente  --->  [FastAPI]  ---> (Sube Img) ---> [MinIO]
                  |
                  +----------> (Encola Tarea) -> [Redis/RabbitMQ]
                                                      |
                                                      v
                                                 [Celery Worker]
                                                      |
                                                      +---> (Descarga Img) ---> [MinIO]
                                                      +---> (Procesa Img)
                                                      +---> (Guarda Resultado) -> [PostgreSQL]

## 4. Requerimientos Funcionales (Entregables)

### Fase 1: Infraestructura (Docker Compose)

Necesito un archivo `docker-compose.yml` que levante:

1. Redis: Puerto 6379.
2. MinIO: Puerto 9000 (API) y 9001 (Consola). User/Pass: `minioadmin`.
3. PostgreSQL: Puerto 5432.

### Fase 2: Módulo de Storage (MinIO)

Implementar una clase `StorageService` en Python que use `boto3`.

* Debe verificar si el "Bucket" existe al iniciar.
* Método `upload_file(file_bytes, filename) -> url/path`.
* Método `get_file(filename) -> bytes`.

### Fase 3: API Endpoints (FastAPI)

* `POST /api/v1/analyze`:
  * Recibe: `UploadFile` (imagen).
  * Acción: Sube a MinIO -> Crea registro en DB (Status: PENDING) -> Llama a `celery_task.delay(task_id)`.
  * Retorna: `{"task_id": "uuid", "status": "processing"}`. Código HTTP 202.
* `GET /api/v1/tasks/{task_id}`:
  * Consulta la DB y devuelve el estado actual y el resultado si existe.

### Fase 4: Celery Worker

* Crear una tarea `process_image(task_id)`.
* Lógica:
    1. Recuperar metadata de DB.
    2. Descargar imagen de MinIO.
    3. Simulación de IA: Convertir a escala de grises (Grayscale) con OpenCV y esperar 5 segundos (`time.sleep(5)`) para simular carga pesada.
    4. Subir la imagen procesada a un bucket `processed`.
    5. Actualizar DB: Status `COMPLETED`, Result URL `...`.

## 5. Criterios de Aceptación (Definition of Done)

* [ ] El servidor NUNCA se bloquea, incluso si subo 50 imágenes seguidas.
* [ ] Puedo ver la imagen original y la procesada en la consola de MinIO.
* [ ] El código sigue PEP8 y tiene Type Hints.
* [ ] Manejo de errores: Si MinIO cae, el worker debe reintentar o marcar la tarea como `FAILED`.

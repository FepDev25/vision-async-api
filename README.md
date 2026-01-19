# Vision Async API

API asíncrona para procesamiento de imágenes con detección de bordes utilizando FastAPI, Celery y OpenCV.

**Autor:** Felipe Peralta  
**Perfil:** Estudiante de Ingeniería en Ciencias de la Computación

## Descripción del Proyecto

Vision Async API es una aplicación web full-stack diseñada para procesar imágenes de forma asíncrona aplicando técnicas de visión por computadora. El sistema cuenta con un backend robusto (FastAPI + Celery) y un frontend interactivo (React + TypeScript) que permite a los usuarios subir imágenes, visualizar el progreso del procesamiento en tiempo real, y comparar los resultados del algoritmo de detección de bordes Canny.

El proyecto implementa una arquitectura moderna basada en microservicios, con separación clara entre la API REST, el procesamiento asíncrono de tareas, el almacenamiento de datos e imágenes, y una interfaz de usuario que demuestra todo el flujo de trabajo.

## Tecnologías Utilizadas

### Backend & Framework

- **FastAPI**: Framework web moderno y de alto rendimiento para construir APIs con Python
- **Celery**: Sistema de cola de tareas distribuidas para procesamiento asíncrono
- **Redis**: Broker de mensajes para Celery y caché

### Base de Datos & ORM

- **PostgreSQL**: Base de datos relacional para persistencia de tareas
- **SQLAlchemy**: ORM con soporte asíncrono (AsyncPG)
- **Alembic**: Herramienta de migraciones de base de datos

### Almacenamiento & Procesamiento

- **MinIO**: Almacenamiento de objetos compatible con S3 para imágenes
- **OpenCV**: Biblioteca de visión por computadora para procesamiento de imágenes
- **NumPy**: Procesamiento numérico para manipulación de arrays de imágenes

### Frontend

- **React 19**: Biblioteca de UI con TypeScript
- **Vite**: Build tool y dev server de última generación
- **Tailwind CSS v4**: Framework de estilos utility-first

### Herramientas de Desarrollo

- **Pytest**: Framework de testing con soporte asíncrono
- **UV**: Gestor de paquetes y entornos virtuales de Python
- **Docker & Docker Compose**: Containerización y orquestación de servicios

## Arquitectura del Sistema

```bash
Cliente (HTTP)
    ↓
FastAPI (API REST)
    ↓
PostgreSQL (Estado de tareas) ← → MinIO (Almacenamiento de imágenes)
    ↓
Redis (Cola de mensajes)
    ↓
Celery Worker (Procesamiento)
    ↓
OpenCV (Detección de bordes)
```

### Flujo de Procesamiento

1. El usuario sube una imagen vía POST `/api/v1/vision/analyze`
2. La imagen se almacena en MinIO y se crea un registro en PostgreSQL con estado PENDING
3. Se encola una tarea en Celery a través de Redis
4. Un worker de Celery toma la tarea y actualiza el estado a PROCESSING
5. El worker descarga la imagen de MinIO, aplica el algoritmo Canny y sube el resultado
6. El estado se actualiza a COMPLETED con la referencia al archivo procesado
7. El usuario consulta el estado con GET `/api/v1/vision/tasks/{task_id}`
8. El usuario descarga el resultado con GET `/api/v1/vision/tasks/{task_id}/result`

## Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose
- 2GB RAM disponible
- Puertos libres: 8000, 5433, 6379, 9000, 9001

### Instalación con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd vision-async-api

# 2. Construir imágenes
docker-compose build

# 3. Iniciar todos los servicios
docker-compose up -d

# 4. Verificar que todo esté corriendo
docker-compose ps

# 5. Ver logs
docker-compose logs -f api
```

**Accesos:**

- Frontend: <http://localhost:5173> (después de `npm run dev`)
- API: <http://localhost:8000>
- Documentación: <http://localhost:8000/docs>
- MinIO Console: <http://localhost:9001> (minioadmin/minioadmin)

### Configuración Inicial de MinIO

1. Accede a <http://localhost:9001>
2. Login: `minioadmin` / `minioadmin`
3. Crea el bucket `images-input`

### Frontend (React)

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Visitar http://localhost:5173
```

### Probar la Aplicación

1. Backend: <http://localhost:8000/docs> - Documentación interactiva
2. Frontend: <http://localhost:5173> - Interfaz web para subir y visualizar imágenes
3. MinIO: <http://localhost:9001> - Ver archivos almacenados

Ver [Guía de Docker Compose](docs/docker-compose-guide.md) para comandos adicionales.

---

## Desarrollo Local

Si prefieres ejecutar la API localmente (sin Docker):

### Requisitos

- Python 3.12+
- UV package manager

### Instalación

```bash
# 1. Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependencias
uv sync

# 3. Iniciar solo infraestructura
docker-compose up -d db redis minio

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

### Variables de Entorno

Crear archivo `.env`:

```env
# API
PROJECT_NAME="Vision Async API"
API_V1_STR="/api/v1"

# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_PORT=5433
POSTGRES_USER=admin
POSTGRES_PASSWORD=password123
POSTGRES_DB=vision_db

# MinIO
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False
MINIO_BUCKET_NAME=images-input

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Ejecutar Aplicación

```bash
# Terminal 1 - Aplicar migraciones
uv run alembic -c app/alembic.ini upgrade head

# Terminal 1 - API
uv run uvicorn app.main:app --reload

# Terminal 2 - Worker
uv run celery -A app.core.celery_app worker --loglevel=info

# Terminal 3 - Frontend
cd frontend && npm run dev
```

---

---

## Endpoints de la API

### POST /api/v1/vision/analyze

Sube una imagen para procesamiento asíncrono.

**Request:**

- Content-Type: multipart/form-data
- Body: file (imagen)

**Response (202 Accepted):**

```json
{
  "id": "uuid",
  "status": "PENDING",
  "filename": "nombre_archivo.jpg",
  "result": null,
  "created_at": "2026-01-19T00:00:00Z"
}
```

### GET /api/v1/vision/tasks/{task_id}

Consulta el estado de una tarea de procesamiento.

**Response (200 OK):**

```json
{
  "id": "uuid",
  "status": "COMPLETED",
  "filename": "nombre_archivo.jpg",
  "result": {
    "processed_file": "processed_nombre_archivo.png"
  },
  "created_at": "2026-01-19T00:00:00Z"
}
```

### GET /api/v1/vision/tasks/{task_id}/result

Descarga la imagen procesada.

**Response (200 OK):**

- Content-Type: application/octet-stream
- Body: bytes de la imagen procesada

## Testing

### Con Docker

```bash
# Ejecutar todos los tests
docker-compose exec api uv run pytest -v

# Con cobertura
docker-compose exec api uv run pytest --cov=app --cov-report=html

# Tests específicos
docker-compose exec api uv run pytest app/tests/test_api.py -v
docker-compose exec api uv run pytest app/tests/test_worker.py -v
```

### Local

```bash
# Todos los tests
uv run pytest app/tests/ -v

# Tests específicos
uv run pytest app/tests/test_vision_endpoints.py -v
uv run pytest app/tests/test_worker.py -v
uv run pytest app/tests/test_storage.py -v

# Con cobertura
uv run pytest app/tests/ -v --cov=app
```

## Estructura del Proyecto

```bash
vision-async-api/
├── app/                   # Backend (Python/FastAPI)
│   ├── core/              # Configuración central (DB, Celery, Config)
│   ├── models.py          # Modelos de base de datos
│   ├── schemas.py         # Esquemas de validación (Pydantic)
│   ├── routers/           # Endpoints de la API
│   ├── services/          # Lógica de negocio (MinIO, etc.)
│   ├── worker.py          # Worker de Celery para procesamiento
│   ├── alembic/           # Migraciones de base de datos
│   └── tests/             # Suite de tests
├── frontend/              # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── api/           # Cliente API
│   │   ├── components/    # Componentes React
│   │   ├── App.tsx        # Componente principal
│   │   ├── types.ts       # Tipos TypeScript
│   │   └── index.css      # Estilos Tailwind
│   ├── package.json
│   └── vite.config.ts     # Configuración Vite
├── docs/                  # Documentación del proyecto
│   ├── docker-compose-guide.md
│   └── alembic-setup.md
├── scripts/               # Scripts de utilidad
│   └── start.sh           # Script de inicio con migraciones
├── docker-compose.yml     # Orquestación de servicios
├── Dockerfile             # Imagen Docker de la aplicación
├── .dockerignore          # Archivos ignorados en build
├── .env                   # Variables de entorno
├── pyproject.toml         # Dependencias del proyecto
└── README.md              # Este archivo
```

## Comandos Útiles

### Docker Compose

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f api worker

# Reiniciar
docker-compose restart api worker

# Detener
docker-compose down

# Limpiar todo (⚠️ BORRA DATOS)
docker-compose down -v
```

### Desarrollo

```bash
# Shell en contenedor
docker-compose exec api bash

# Crear migración
docker-compose exec api uv run alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose exec api uv run alembic upgrade head

# Ver estado DB
docker-compose exec api uv run alembic current
```

## Troubleshooting

### La API no inicia

```bash
# Ver logs completos
docker-compose logs --tail=100 api

# Verificar salud de servicios
docker-compose ps
```

### Worker no procesa tareas

```bash
# Ver logs del worker
docker-compose logs -f worker

# Verificar conexión a Redis
docker-compose exec redis redis-cli ping
```

### Errores de base de datos

```bash
# Verificar que las migraciones se aplicaron
docker-compose exec api uv run alembic current

# Aplicar migraciones manualmente
docker-compose exec api uv run alembic upgrade head
```

Consulta la [Guía de Docker Compose](docs/docker-compose-guide.md) para más soluciones.

## Decisiones Técnicas

### Frontend con Polling

El frontend implementa polling automático cada 2 segundos para actualizar el estado de las tareas en tiempo real, permitiendo al usuario visualizar el progreso del procesamiento sin necesidad de WebSockets. El polling se detiene automáticamente cuando la tarea se completa o falla.

### Procesamiento In-Memory

El procesamiento de imágenes se realiza completamente en memoria, sin escribir archivos temporales en disco. Los bytes se descargan de MinIO, se procesan con OpenCV usando NumPy arrays, y se suben de vuelta a MinIO, optimizando el rendimiento y evitando problemas de I/O.

### Base de Datos Dual

Se utilizan dos configuraciones de SQLAlchemy:

- **Asíncrona (asyncpg)**: Para la API REST de FastAPI
- **Síncrona (psycopg2)**: Para los workers de Celery

Esto evita complejidades innecesarias al mezclar código asíncrono y síncrono en Celery.

### UUIDs como Identificadores

Se utilizan UUIDs en lugar de enteros autoincrementales para mayor seguridad al exponer IDs públicamente y evitar ataques de enumeración.

### Vite Proxy

El frontend usa el proxy de Vite para redirigir peticiones `/api` al backend, evitando problemas de CORS durante el desarrollo y simplificando la configuración.

## Contacto

Felipe Peralta  
Estudiante de Ingeniería en Ciencias de la Computación

## Notas

Este proyecto fue desarrollado con fines educativos como parte del aprendizaje de arquitecturas backend modernas, procesamiento asíncrono y desarrollo full-stack.

# Guía Docker Compose - Vision Async API

Esta guía cubre los comandos esenciales de Docker Compose para trabajar con el proyecto.

## Servicios Disponibles

El proyecto incluye 5 servicios:

| Servicio | Descripción | Puerto |
| ---------- | ------------- | -------- |
| `api` | FastAPI REST API | 8000 |
| `worker` | Celery worker (procesamiento) | - |
| `db` | PostgreSQL 15 | 5433 |
| `redis` | Redis (cola de mensajes) | 6379 |
| `minio` | MinIO (almacenamiento S3) | 9000, 9001 |

## Comandos Básicos

### Construir imágenes

```bash
docker-compose build
```

Reconstruir sin caché:

```bash
docker-compose build --no-cache
```

### Iniciar servicios

```bash
# Todos los servicios en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose up

# Solo infraestructura (para desarrollo local)
docker-compose up -d db redis minio
```

### Detener servicios

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA DATOS)
docker-compose down -v
```

### Reiniciar servicios

```bash
# Reiniciar todos
docker-compose restart

# Reiniciar servicio específico
docker-compose restart api
docker-compose restart worker
```

## Monitoreo

### Ver estado de servicios

```bash
docker-compose ps
```

### Ver logs

```bash
# Todos los servicios (follow)
docker-compose logs -f

# Servicio específico
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f db

# Últimas N líneas
docker-compose logs --tail=50 api
```

### Ver estadísticas de recursos

```bash
docker stats
```

## Desarrollo

### Acceder a un contenedor

```bash
# Shell en el contenedor de la API
docker-compose exec api bash

# Shell en el worker
docker-compose exec worker bash

# PostgreSQL CLI
docker-compose exec db psql -U admin -d vision_db

# Redis CLI
docker-compose exec redis redis-cli
```

### Ejecutar comandos en contenedor

```bash
# Ejecutar tests
docker-compose exec api uv run pytest

# Crear migración
docker-compose exec api uv run alembic revision -m "descripcion"

# Aplicar migraciones
docker-compose exec api uv run alembic upgrade head

# Ver versión de Python
docker-compose exec api python --version
```

### Hot Reload

Los servicios `api` y `worker` tienen volúmenes montados, por lo que detectan cambios automáticamente:

```yaml
volumes:
  - .:/app  # Tu código se sincroniza con el contenedor
```

Si cambias dependencias en `pyproject.toml`, necesitas reconstruir:

```bash
docker-compose build api worker
docker-compose restart api worker
```

## Base de Datos

### Migraciones

```bash
# Ver estado actual
docker-compose exec api uv run alembic current

# Historial de migraciones
docker-compose exec api uv run alembic history

# Crear nueva migración
docker-compose exec api uv run alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
docker-compose exec api uv run alembic upgrade head

# Rollback
docker-compose exec api uv run alembic downgrade -1
```

### Backup y Restore

```bash
# Backup
docker-compose exec db pg_dump -U admin vision_db > backup.sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U admin vision_db
```

## MinIO (Almacenamiento)

### Acceso

- **API**: <http://localhost:9000>
- **Console**: <http://localhost:9001>
- **Credenciales**: minioadmin / minioadmin

### Crear bucket desde CLI

```bash
docker-compose exec api uv run python -c "
from app.services.storage import MinioService
from app.core.config import settings
minio = MinioService()
print('Bucket creado con éxito!')
"
```

## Testing

### Ejecutar todos los tests

```bash
docker-compose exec api uv run pytest
```

### Tests con cobertura

```bash
docker-compose exec api uv run pytest --cov=app --cov-report=html
```

### Test específico

```bash
docker-compose exec api uv run pytest app/tests/test_api.py::test_analyze_image
```

## Troubleshooting

### Ver logs de error

```bash
# API crasheando
docker-compose logs --tail=100 api

# Worker con problemas
docker-compose logs --tail=100 worker
```

### Reinicio completo

```bash
# Detener todo
docker-compose down

# Limpiar volúmenes (⚠️ BORRA DATOS)
docker-compose down -v

# Reconstruir desde cero
docker-compose build --no-cache

# Iniciar
docker-compose up -d
```

### Problemas de red

```bash
# Ver redes
docker network ls

# Inspeccionar red del proyecto
docker network inspect vision-async-api_default
```

### Limpiar sistema Docker

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes sin usar
docker image prune -a

# Limpiar todo (⚠️ CUIDADO)
docker system prune -a --volumes
```

## Health Checks

El docker-compose tiene health checks configurados:

```bash
# Ver salud de servicios
docker-compose ps

# Servicios "healthy" indican que pasaron el health check
```

Los servicios `api` y `worker` esperan a que `db`, `redis` y `minio` estén healthy antes de iniciar.

## Workflow Típico

### Desarrollo diario

```bash
# 1. Iniciar todo
docker-compose up -d

# 2. Ver logs
docker-compose logs -f api worker

# 3. Hacer cambios en código (hot reload automático)

# 4. Si cambias dependencias
docker-compose build api worker
docker-compose restart api worker

# 5. Ejecutar tests
docker-compose exec api uv run pytest

# 6. Al terminar
docker-compose down
```

## Referencias

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

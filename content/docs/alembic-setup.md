# Configuración de Alembic para Migraciones de Base de Datos

## Descripción General

Este documento describe la configuración de Alembic para el manejo de migraciones de base de datos en el proyecto Vision Async API. Se incluyen las modificaciones realizadas para soportar SQLAlchemy con drivers asíncronos y síncronos.

## Arquitectura de Base de Datos

### Configuración Dual de URLs

El proyecto utiliza dos URLs de conexión a PostgreSQL:

**URL Asíncrona** (runtime de la aplicación):

```bash
postgresql+asyncpg://user:password@host:port/database
```

**URL Síncrona** (migraciones con Alembic):

```bash
postgresql+psycopg2://user:password@host:port/database
```

Esta configuración dual se implementa en `app/core/config.py` mediante computed fields:

```python
@computed_field
@property
def SQLALCHEMY_DATABASE_URI(self) -> str:
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:..."

@computed_field
@property
def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
    return f"postgresql+psycopg2://{self.POSTGRES_USER}:..."
```

## Configuración de Alembic

### Archivo env.py

El archivo `app/alembic/env.py` fue configurado para:

1. Importar la configuración del proyecto desde `app.core.config`
2. Importar la clase Base y todos los modelos
3. Establecer dinámicamente la URL de conexión síncrona
4. Configurar el metadata para autogenerate

```python
from app.core.config import settings
from app.core.database import Base
from app.models import Task

config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI_SYNC)
target_metadata = Base.metadata
```

## Modelo Task

Se creó el modelo `Task` en `app/models.py` con las siguientes características:

### Campos

- `id`: UUID v4 (primary key, no autoincremental)
- `status`: Enum (PENDING, PROCESSING, COMPLETED, FAILED)
- `filename`: String (255 caracteres)
- `result`: JSON nullable
- `created_at`: DateTime (automático)
- `updated_at`: DateTime (automático con onupdate)

### Índices

- Índice en `id` (primary key)
- Índice en `status` (optimización de búsquedas)

## Ejecución de Migraciones

### Comandos desde el directorio raíz

**Generar migración:**

```bash
uv run alembic -c app/alembic.ini revision --autogenerate -m "mensaje"
```

**Aplicar migraciones:**

```bash
uv run alembic -c app/alembic.ini upgrade head
```

**Ver historial:**

```bash
uv run alembic -c app/alembic.ini history
```

**Revertir última migración:**

```bash
uv run alembic -c app/alembic.ini downgrade -1
```

## Dependencias Requeridas

```toml
dependencies = [
    "sqlalchemy",
    "asyncpg",        # Driver asíncrono
    "psycopg2-binary", # Driver síncrono para Alembic
    "alembic"
]
```

## Ubicación de Archivos

```bash
vision-async-api/
├── app/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 7213effa643d_create_task_table.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   └── models.py
```

## Notas Importantes

1. Los comandos de Alembic deben ejecutarse desde el directorio raíz del proyecto para que las importaciones de módulos funcionen correctamente.

2. El archivo de configuración de Alembic se encuentra en `app/alembic.ini`, por lo que se debe especificar con la opción `-c`.

3. La URL de conexión se establece dinámicamente desde las variables de entorno del archivo `.env`, no desde `alembic.ini`.

4. El modelo Task utiliza UUID en lugar de enteros autoincrementales por razones de seguridad al exponer IDs públicamente.

## Troubleshooting

Error: No module named 'app'

- Solución: Ejecutar comandos desde el directorio raíz, no desde `app/`

Error: Can't load plugin sqlalchemy.dialects:driver

- Solución: Instalar `psycopg2-binary`

Error: target_metadata is None

- Solución: Verificar que los modelos estén importados en `env.py`

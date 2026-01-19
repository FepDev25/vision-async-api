FROM python:3.12-slim

# Instalar dependencias del sistema para OpenCV y uv
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de uv
COPY pyproject.toml .
COPY .python-version .
COPY uv.lock .

# Instalar dependencias con uv
RUN uv sync --frozen

# Copiar el código fuente
COPY . .

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1

# Este comando se sobreescribe desde el docker-compose
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
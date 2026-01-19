# Vision Async API - Frontend

Aplicación web en React + TypeScript + Tailwind CSS para visualizar el procesamiento asíncrono de imágenes.

## Características

- Interfaz moderna con Tailwind CSS
- Polling automático para actualizar estados en tiempo real
- Drag & Drop para subir imágenes
- Visualización del pipeline de procesamiento
- Comparación lado a lado de imagen original vs procesada
- Feedback en tiempo real del estado del worker

## Tecnologías

- **React 19** - Biblioteca UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS v4** - Framework de estilos
- **Fetch API** - Cliente HTTP

## Estructura del Proyecto

```bash
frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # Cliente API con fetch
│   ├── components/
│   │   ├── UploadZone.tsx     # Zona de carga drag & drop
│   │   ├── TaskCard.tsx       # Tarjeta de tarea con comparación
│   │   └── ProcessingSteps.tsx # Pipeline visual de procesamiento
│   ├── hooks/
│   │   └── useTaskPolling.ts  # Hook para polling de estado
│   ├── App.tsx                # Componente principal con polling
│   ├── types.ts               # Tipos TypeScript
│   ├── index.css              # Estilos globales con Tailwind
│   └── main.tsx               # Entry point
├── package.json
├── vite.config.ts             # Configuración Vite con proxy
└── tsconfig.json
```

## Instalación y Uso

### Requisitos Previos

- Node.js 18+ (recomendado 20+)
- npm o pnpm
- Backend corriendo en `http://localhost:8000`

### Instalación

```bash
# Instalar dependencias
npm install
```

### Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# La app estará disponible en http://localhost:5173
```

El proxy de Vite redirige las peticiones `/api` al backend en `http://localhost:8000`.

### Build de Producción

```bash
# Compilar para producción
npm run build

# Vista previa del build
npm run preview
```

## Flujo de la Aplicación

1. **Carga de Imagen**
   - Usuario arrastra o selecciona una imagen
   - Se crea una URL local para previsualización
   - Se sube al backend vía `POST /api/v1/vision/analyze`

2. **Polling Automático**
   - El componente inicia polling cada 2 segundos
   - Consulta el estado vía `GET /api/v1/vision/tasks/{id}`
   - Actualiza la UI en tiempo real

3. **Estados Visualizados**
   - **PENDING** - En cola esperando worker
   - **PROCESSING** - Worker aplicando algoritmo Canny
   - **COMPLETED** - Resultado listo para descargar
   - **FAILED** - Error en el procesamiento

4. **Resultado**
   - Se muestra la imagen procesada al completarse
   - Comparación lado a lado con la original
   - Botón de descarga disponible

## Componentes Principales

### App.tsx

Componente principal que maneja:

- Estado global de la aplicación
- Lógica de polling con `setInterval`
- Subida de imágenes
- Limpieza de intervalos al desmontar

### UploadZone.tsx

Zona de carga con:

- Soporte drag & drop
- Click para seleccionar archivo
- Validación de tipo de archivo
- Estados de carga

### ProcessingSteps.tsx

Pipeline visual que muestra:

- 4 pasos del procesamiento
- Estado actual con animaciones
- Tiempo transcurrido
- Barra de progreso

### TaskCard.tsx

Tarjeta de tarea con:

- Header con estado y badge
- Pipeline de procesamiento
- Comparación de imágenes
- Detalles técnicos expandibles
- Botón de descarga

## API Client

El cliente API (`src/api/client.ts`) proporciona:

```typescript
// Subir imagen
uploadImage(file: File): Promise<Task>

// Obtener estado de tarea
getTaskStatus(taskId: string): Promise<Task>

// Obtener URL de descarga
getResultDownloadUrl(taskId: string): string

// Descargar resultado
downloadResult(taskId: string): Promise<Blob>
```

## Configuración del Proxy

El archivo `vite.config.ts` está configurado para hacer proxy de las peticiones API:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

Esto permite hacer peticiones a `/api/v1/...` desde el frontend sin problemas de CORS.

## Desarrollo Guía

### Agregar Nuevas Funcionalidades

1. Crear el componente en `src/components/`
2. Agregar tipos necesarios en `src/types.ts`
3. Extender el cliente API si es necesario
4. Importar y usar en `App.tsx`

### Estilos

El proyecto usa Tailwind CSS v4. Las clases de utilidad están disponibles directamente:

```tsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Contenido
</div>
```

## Scripts Disponibles

```bash
npm run dev      # Servidor de desarrollo
npm run build    # Build de producción
npm run preview  # Preview del build
npm run lint     # Linter ESLint
```

## Consideraciones

- El polling se detiene automáticamente cuando la tarea está COMPLETED o FAILED
- Los intervalos se limpian al desmontar el componente
- Las URLs de imágenes locales se crean con `URL.createObjectURL()`
- El componente maneja errores de red y API

## Autor

Felipe Peralta  
Estudiante de Ingeniería en Ciencias de la Computación

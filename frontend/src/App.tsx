import { useState, useEffect, useRef } from 'react';
import { UploadZone } from './components/UploadZone';
import { TaskCard } from './components/TaskCard';
import { uploadImage, getTaskStatus } from './api/client';
import type { Task } from './types';

function App() {
  const [isUploading, setIsUploading] = useState(false);
  const [currentTask, setCurrentTask] = useState<Task | null>(null);
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  // Función para hacer polling del estado de la tarea
  const startPolling = (taskId: string) => {
    // Limpiar intervalo anterior si existe
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Polling cada 2 segundos
    pollingIntervalRef.current = window.setInterval(async () => {
      try {
        const updatedTask = await getTaskStatus(taskId);
        setCurrentTask(updatedTask);

        // Detener polling si la tarea terminó (COMPLETED o FAILED)
        if (updatedTask.status === 'COMPLETED' || updatedTask.status === 'FAILED') {
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      } catch (err) {
        console.error('Error en polling:', err);
      }
    }, 2000);
  };

  // Limpiar intervalo al desmontar
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Handler para cuando se selecciona un archivo
  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setError(null);
    
    // Crear URL local para previsualización
    const localUrl = URL.createObjectURL(file);
    setOriginalImageUrl(localUrl);

    try {
      // Subir la imagen
      const task = await uploadImage(file);
      setCurrentTask(task);

      // Iniciar polling para actualizar el estado
      startPolling(task.id);

    } catch (err: any) {
      setError(err.message || 'Error al subir la imagen');
      setOriginalImageUrl(null);
    } finally {
      setIsUploading(false);
    }
  };

  // Handler para resetear y procesar nueva imagen
  const handleReset = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setCurrentTask(null);
    setOriginalImageUrl(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
              Vision Async API
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Detección de bordes con procesamiento asíncrono
              </p>
            </div>
            <div className="flex items-center gap-3">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                📖 API Docs
              </a>
              {currentTask && (
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Nueva Imagen
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-red-500 text-xl">❌</span>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700 font-medium">Error</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {!currentTask ? (
          /* Upload Zone - Pantalla inicial */
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-12">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-3">
                  Sube una imagen para comenzar
                </h2>
                <p className="text-gray-600 text-lg">
                  El sistema procesará tu imagen usando OpenCV en un worker asíncrono
                </p>
              </div>
              
              <UploadZone 
                onFileSelect={handleFileSelect} 
                isUploading={isUploading}
              />

              {/* Info Cards */}
              <div className="grid md:grid-cols-3 gap-6 mt-8">
                <div className="bg-blue-50 p-6 rounded-lg text-center">
                  <h3 className="font-semibold text-gray-800 mb-2">Asíncrono</h3>
                  <p className="text-sm text-gray-600">
                    Procesamiento en background con Celery
                  </p>
                </div>
                <div className="bg-green-50 p-6 rounded-lg text-center">
                  <h3 className="font-semibold text-gray-800 mb-2">Canny Edge</h3>
                  <p className="text-sm text-gray-600">
                    Algoritmo de detección de bordes
                  </p>
                </div>
                <div className="bg-purple-50 p-6 rounded-lg text-center">
                  <h3 className="font-semibold text-gray-800 mb-2">Almacenamiento</h3>
                  <p className="text-sm text-gray-600">
                    MinIO S3-compatible storage
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Task Card - Cuando hay una tarea activa */
          <TaskCard task={currentTask} originalImageUrl={originalImageUrl} />
        )}

        {/* Footer Info */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 bg-white px-6 py-3 rounded-full shadow-sm border border-gray-200">
            <span className="text-sm text-gray-600">Desarrollado por</span>
            <span className="font-bold text-gray-800">Felipe Peralta</span>
            <span className="text-gray-400">|</span>
            <span className="text-sm text-gray-600">FastAPI + React + TypeScript</span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

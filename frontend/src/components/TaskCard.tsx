// Componente para mostrar la tarjeta de una tarea

import { useEffect, useState } from 'react';
import type { Task } from '../types';
import { getResultDownloadUrl } from '../api/client';
import { ProcessingSteps } from './ProcessingSteps';

interface TaskCardProps {
  task: Task;
  originalImageUrl: string | null;
}

export function TaskCard({ task, originalImageUrl }: TaskCardProps) {
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);

  useEffect(() => {
    // Cuando la tarea se completa, cargar la imagen procesada
    if (task.status === 'COMPLETED' && task.result?.processed_file) {
      const url = getResultDownloadUrl(task.id);
      setProcessedImageUrl(url);
    }
  }, [task.status, task.result, task.id]);

  const isProcessing = task.status === 'PENDING' || task.status === 'PROCESSING';
  const isCompleted = task.status === 'COMPLETED';

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Tarea de Procesamiento</h2>
            <p className="text-blue-100 text-sm mt-1">
              ID: {task.id.slice(0, 8)}...
            </p>
          </div>
          <div className="text-right">
            <div className={`
              inline-block px-4 py-2 rounded-full font-semibold text-sm
              ${task.status === 'PENDING' ? 'bg-yellow-400 text-yellow-900' : ''}
              ${task.status === 'PROCESSING' ? 'bg-blue-400 text-blue-900' : ''}
              ${task.status === 'COMPLETED' ? 'bg-green-400 text-green-900' : ''}
              ${task.status === 'FAILED' ? 'bg-red-400 text-red-900' : ''}
            `}>
              {task.status}
            </div>
          </div>
        </div>
      </div>

      {/* Processing Steps */}
      <div className="p-6">
        <ProcessingSteps status={task.status} createdAt={task.created_at} />
      </div>

      {/* Images Comparison */}
      <div className="p-6 border-t border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {isCompleted ? 'Comparación de Resultados' : 'Vista Previa'}
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          {/* Original Image */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-600">
                Imagen Original
              </span>
              <span className="text-xs text-gray-500">{task.filename}</span>
            </div>
            <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-300">
              {originalImageUrl ? (
                <img 
                  src={originalImageUrl} 
                  alt="Original" 
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
                  <span>Cargando...</span>
                </div>
              )}
            </div>
          </div>

          {/* Processed Image */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-600">
                Detección de Bordes (Canny)
              </span>
              {isCompleted && task.result?.processed_file && (
                <a 
                  href={getResultDownloadUrl(task.id)}
                  download={task.result.processed_file}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  Descargar
                </a>
              )}
            </div>
            <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 border-gray-300">
              {isProcessing && (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mb-4"></div>
                  <span className="text-sm">Procesando con OpenCV...</span>
                  <span className="text-xs mt-2">Worker Celery en acción</span>
                </div>
              )}
              {isCompleted && processedImageUrl && (
                <img 
                  src={processedImageUrl} 
                  alt="Processed" 
                  className="w-full h-full object-contain"
                />
              )}
              {task.status === 'FAILED' && (
                <div className="flex items-center justify-center h-full text-red-500">
                  <span>❌ Error en procesamiento</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="p-6 bg-gray-50 border-t border-gray-200">
        <details className="group">
          <summary className="cursor-pointer font-semibold text-gray-700 flex items-center gap-2">
            <span className="transform group-open:rotate-90 transition-transform"></span>
            Detalles Técnicos del Backend
          </summary>
          <div className="mt-4 space-y-2 text-sm text-gray-600 bg-white p-4 rounded-lg border border-gray-200">
            <div className="flex justify-between">
              <span className="font-medium">Stack:</span>
              <span>FastAPI + Celery + Redis + PostgreSQL + MinIO</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Algoritmo:</span>
              <span>OpenCV Canny Edge Detection</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Procesamiento:</span>
              <span>In-memory (sin archivos temporales)</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Storage:</span>
              <span>MinIO S3-compatible</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Base de Datos:</span>
              <span>SQLAlchemy Async (AsyncPG) + Sync (psycopg2)</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Cola de Tareas:</span>
              <span>Celery con Redis broker</span>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}

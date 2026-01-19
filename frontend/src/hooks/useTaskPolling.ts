// Hook personalizado para manejar el polling de tareas

import { useEffect, useRef, useCallback } from 'react';
import { getTaskStatus } from '../api/client';
import type { Task } from '../types';

interface UseTaskPollingOptions {
  taskId: string | null;
  onUpdate: (task: Task) => void;
  interval?: number; // milisegundos
  enabled?: boolean;
}

// Hook para hacer polling del estado de una tarea
// Se detiene automáticamente cuando la tarea está COMPLETED o FAILED
export function useTaskPolling({
  taskId,
  onUpdate,
  interval = 2000,
  enabled = true
}: UseTaskPollingOptions) {
  const intervalRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startPolling = useCallback(() => {
    if (!taskId || !enabled) return;

    // Limpiar intervalo anterior
    stopPolling();

    // Crear nuevo intervalo
    intervalRef.current = window.setInterval(async () => {
      try {
        const updatedTask = await getTaskStatus(taskId);
        onUpdate(updatedTask);

        // Detener si terminó
        if (updatedTask.status === 'COMPLETED' || updatedTask.status === 'FAILED') {
          stopPolling();
        }
      } catch (error) {
        console.error('Error en polling:', error);
      }
    }, interval);
  }, [taskId, enabled, interval, onUpdate, stopPolling]);

  // Iniciar/reiniciar polling cuando cambian las dependencias
  useEffect(() => {
    if (enabled && taskId) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => {
      stopPolling();
    };
  }, [taskId, enabled, startPolling, stopPolling]);

  return { stopPolling, startPolling };
}

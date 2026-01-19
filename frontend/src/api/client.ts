// Cliente API para comunicarse con el backend

import type { Task, UploadResponse } from '../types';

const API_BASE_URL = '/api/v1';

export class APIError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'APIError';
  }
}

// Sube una imagen para procesamiento
export async function uploadImage(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/vision/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new APIError(response.status, error.detail || 'Error al subir la imagen');
  }

  return response.json();
}

// Obtiene el estado de una tarea
export async function getTaskStatus(taskId: string): Promise<Task> {
  const response = await fetch(`${API_BASE_URL}/vision/tasks/${taskId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new APIError(response.status, error.detail || 'Error al obtener el estado');
  }

  return response.json();
}

// Obtiene la URL para descargar el resultado procesado
export function getResultDownloadUrl(taskId: string): string {
  return `${API_BASE_URL}/vision/tasks/${taskId}/result`;
}

// Descarga el archivo procesado
export async function downloadResult(taskId: string): Promise<Blob> {
  const response = await fetch(getResultDownloadUrl(taskId));

  if (!response.ok) {
    throw new APIError(response.status, 'Error al descargar el resultado');
  }

  return response.blob();
}

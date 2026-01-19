// Tipos TypeScript para la API

export type TaskStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface Task {
  id: string;
  status: TaskStatus;
  filename: string;
  result: {
    processed_file?: string;
    error?: string;
  } | null;
  created_at: string;
}

export interface UploadResponse extends Task {}

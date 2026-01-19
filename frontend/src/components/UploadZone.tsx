// Componente para zona de carga de archivos (drag & drop)

import { useCallback, useState } from 'react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
}

export function UploadZone({ onFileSelect, isUploading }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      className={`
        relative border-2 border-dashed rounded-xl p-12 text-center transition-all
        ${isDragging 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-gray-400 bg-white'
        }
        ${isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      onDragEnter={handleDragIn}
      onDragLeave={handleDragOut}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept="image/*"
        onChange={handleFileInput}
        disabled={isUploading}
      />
      
      <label htmlFor="file-upload" className="cursor-pointer">
        <div className="flex flex-col items-center gap-4">
          <svg 
            className="w-16 h-16 text-gray-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
            />
          </svg>
          
          <div>
            <p className="text-lg font-semibold text-gray-700">
              {isUploading ? 'Subiendo imagen...' : 'Arrastra una imagen aquí'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              o haz clic para seleccionar
            </p>
          </div>

          <div className="text-xs text-gray-400">
            Formatos soportados: JPG, PNG, GIF
          </div>
        </div>
      </label>
    </div>
  );
}

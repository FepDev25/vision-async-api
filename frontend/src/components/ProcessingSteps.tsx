// Componente para mostrar los pasos del procesamiento

import type { TaskStatus } from '../types';

interface Step {
  label: string;
  description: string;
  icon: string;
}

const STEPS: Step[] = [
  {
    label: 'Subiendo',
    description: 'Almacenando imagen en MinIO',
    icon: '📤'
  },
  {
    label: 'En Cola',
    description: 'Esperando worker disponible',
    icon: '⏳'
  },
  {
    label: 'Procesando',
    description: 'Aplicando detección de bordes Canny',
    icon: '🔄'
  },
  {
    label: 'Completado',
    description: 'Imagen procesada lista',
    icon: '✅'
  }
];

interface ProcessingStepsProps {
  status: TaskStatus;
  createdAt: string;
}

export function ProcessingSteps({ status, createdAt }: ProcessingStepsProps) {
  const getCurrentStep = (): number => {
    switch (status) {
      case 'PENDING':
        return 1;
      case 'PROCESSING':
        return 2;
      case 'COMPLETED':
        return 3;
      case 'FAILED':
        return -1;
      default:
        return 0;
    }
  };

  const currentStep = getCurrentStep();
  const elapsedTime = Math.floor((Date.now() - new Date(createdAt).getTime()) / 1000);

  if (status === 'FAILED') {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
        <div className="flex items-center gap-3">
          <span className="text-3xl">❌</span>
          <div>
            <p className="font-semibold text-red-800">Error en el procesamiento</p>
            <p className="text-sm text-red-600">La imagen no pudo ser procesada</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-800">
          Pipeline de Procesamiento
        </h3>
        <div className="text-sm text-gray-600">
          ⏱️ {elapsedTime}s
        </div>
      </div>

      <div className="space-y-4">
        {STEPS.map((step, index) => {
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;
          const isPending = index > currentStep;

          return (
            <div key={index} className="flex items-start gap-4">
              <div className={`
                flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl
                transition-all duration-300
                ${isActive ? 'bg-blue-500 shadow-lg scale-110 animate-pulse' : ''}
                ${isCompleted ? 'bg-green-500' : ''}
                ${isPending ? 'bg-gray-200' : ''}
              `}>
                {step.icon}
              </div>

              <div className="flex-1 pt-2">
                <div className={`
                  font-semibold transition-colors
                  ${isActive ? 'text-blue-700' : ''}
                  ${isCompleted ? 'text-green-700' : ''}
                  ${isPending ? 'text-gray-400' : ''}
                `}>
                  {step.label}
                  {isActive && <span className="ml-2 text-sm font-normal">(en progreso...)</span>}
                  {isCompleted && <span className="ml-2 text-sm font-normal">✓</span>}
                </div>
                <div className={`
                  text-sm mt-1
                  ${isActive ? 'text-blue-600' : ''}
                  ${isCompleted ? 'text-green-600' : ''}
                  ${isPending ? 'text-gray-400' : ''}
                `}>
                  {step.description}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Barra de progreso */}
      <div className="mt-6 bg-gray-200 rounded-full h-2 overflow-hidden">
        <div 
          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full transition-all duration-500 ease-out"
          style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  );
}

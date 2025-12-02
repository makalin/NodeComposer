/**
 * Zustand store for global state management
 */

import { create } from 'zustand';
import { GenerationTask, ModelCheckpoint, TrainingStatus } from '@/lib/api';

interface AppState {
  tasks: GenerationTask[];
  models: ModelCheckpoint[];
  trainingStatus: TrainingStatus | null;
  selectedModel: string | null;
  currentTask: GenerationTask | null;
  
  setTasks: (tasks: GenerationTask[]) => void;
  addTask: (task: GenerationTask) => void;
  updateTask: (taskId: string, updates: Partial<GenerationTask>) => void;
  setModels: (models: ModelCheckpoint[]) => void;
  setSelectedModel: (modelId: string | null) => void;
  setTrainingStatus: (status: TrainingStatus) => void;
  setCurrentTask: (task: GenerationTask | null) => void;
}

export const useStore = create<AppState>((set) => ({
  tasks: [],
  models: [],
  trainingStatus: null,
  selectedModel: null,
  currentTask: null,

  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ tasks: [task, ...state.tasks] })),
  updateTask: (taskId, updates) =>
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === taskId ? { ...task, ...updates } : task
      ),
    })),
  setModels: (models) => set({ models }),
  setSelectedModel: (modelId) => set({ selectedModel: modelId }),
  setTrainingStatus: (status) => set({ trainingStatus: status }),
  setCurrentTask: (task) => set({ currentTask: task }),
}));


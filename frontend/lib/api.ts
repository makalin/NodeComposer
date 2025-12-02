/**
 * API client for NodeComposer backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface GenerationTask {
  id: string;
  prompt: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  file_path?: string;
  duration: number;
}

export interface ModelCheckpoint {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  file_path: string;
  is_base: boolean;
}

export interface TrainingStatus {
  status: 'idle' | 'processing_dataset' | 'training' | 'completed' | 'failed';
  progress: number;
  epoch: number;
  total_epochs: number;
  loss?: number;
  message: string;
}

export interface GenerationRequest {
  prompt: string;
  duration?: number;
  model_id?: string;
  guidance_scale?: number;
  temperature?: number;
}

export const apiClient = {
  // Health check
  async health() {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Generation
  async generate(request: GenerationRequest) {
    const response = await api.post('/api/generate', request);
    return response.data;
  },

  async generateFromAudio(
    prompt: string,
    audioFile: File,
    duration?: number,
    modelId?: string
  ) {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('prompt', prompt);
    if (duration) formData.append('duration', duration.toString());
    if (modelId) formData.append('model_id', modelId);

    const response = await api.post('/api/generate/audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getTasks(): Promise<GenerationTask[]> {
    const response = await api.get('/api/tasks');
    return response.data;
  },

  async getTask(taskId: string): Promise<GenerationTask> {
    const response = await api.get(`/api/tasks/${taskId}`);
    return response.data;
  },

  getTaskAudioUrl(taskId: string): string {
    return `${API_BASE_URL}/api/tasks/${taskId}/audio`;
  },

  async deleteTask(taskId: string) {
    const response = await api.delete(`/api/tasks/${taskId}`);
    return response.data;
  },

  // Models
  async getModels(): Promise<ModelCheckpoint[]> {
    const response = await api.get('/api/models');
    return response.data;
  },

  // Training
  async processDataset() {
    const response = await api.post('/api/train/process-dataset');
    return response.data;
  },

  async getTrainingStatus(): Promise<TrainingStatus> {
    const response = await api.get('/api/train/status');
    return response.data;
  },

  async startTraining(epochs?: number, learningRate?: number, batchSize?: number) {
    const response = await api.post('/api/train/start', {
      epochs,
      learning_rate: learningRate,
      batch_size: batchSize,
    });
    return response.data;
  },

  async stopTraining() {
    const response = await api.post('/api/train/stop');
    return response.data;
  },

  // Stem Separation
  async separateStems(taskId: string, stems?: string[]) {
    const response = await api.post(`/api/tasks/${taskId}/separate`, { stems });
    return response.data;
  },

  // Audio Export
  async exportAudio(taskId: string, format: string = 'mp3', bitrate: string = '320k') {
    const response = await api.post(`/api/tasks/${taskId}/export`, { format, bitrate });
    return response.data;
  },

  // Batch Generation
  async batchGenerate(prompts: string[], duration?: number, modelId?: string) {
    const response = await api.post('/api/batch/generate', {
      prompts,
      duration,
      model_id: modelId,
    });
    return response.data;
  },

  async generateVariations(prompt: string, numVariations?: number, duration?: number, modelId?: string) {
    const response = await api.post('/api/batch/variations', {
      prompt,
      num_variations: numVariations,
      duration,
      model_id: modelId,
    });
    return response.data;
  },

  // Prompt Templates
  async getTemplates(category?: string) {
    const response = await api.get('/api/prompts/templates', {
      params: { category },
    });
    return response.data;
  },

  async getTemplate(category: string, name: string) {
    const response = await api.get(`/api/prompts/templates/${category}/${name}`);
    return response.data;
  },

  async createTemplate(category: string, name: string, prompt: string) {
    const response = await api.post('/api/prompts/templates', {
      category,
      name,
      prompt,
    });
    return response.data;
  },

  async searchTemplates(query: string) {
    const response = await api.get('/api/prompts/search', {
      params: { query },
    });
    return response.data;
  },

  // Audio Analysis
  async analyzeAudio(taskId: string) {
    const response = await api.get(`/api/tasks/${taskId}/analyze`);
    return response.data;
  },

  async getWaveform(taskId: string) {
    const response = await api.get(`/api/tasks/${taskId}/waveform`);
    return response.data;
  },

  // Configuration
  async getConfig() {
    const response = await api.get('/api/config');
    return response.data;
  },

  async updateConfig(updates: Record<string, any>) {
    const response = await api.post('/api/config', updates);
    return response.data;
  },
};


import { useState } from 'react';
import { apiClient, GenerationRequest } from '@/lib/api';
import { useStore } from '@/store/useStore';
import { Play, Loader2 } from 'lucide-react';
import PromptTemplates from './PromptTemplates';
import BatchGenerator from './BatchGenerator';
import AudioTools from './AudioTools';

export default function ComposeTab() {
  const { tasks, models, selectedModel, setSelectedModel, addTask } = useStore();
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(30);
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [showTemplates, setShowTemplates] = useState(false);
  const [showBatch, setShowBatch] = useState(false);
  const [selectedTaskForTools, setSelectedTaskForTools] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    try {
      let result;
      if (audioFile) {
        result = await apiClient.generateFromAudio(
          prompt,
          audioFile,
          duration,
          selectedModel || undefined
        );
      } else {
        const request: GenerationRequest = {
          prompt,
          duration,
          model_id: selectedModel || undefined,
        };
        result = await apiClient.generate(request);
      }

      // Task will be added via polling
      setPrompt('');
      setAudioFile(null);
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to generate music. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAudioFile(e.target.files[0]);
    }
  };

  return (
    <div className="h-full flex flex-col p-8">
      <div className="max-w-4xl mx-auto w-full">
        <h2 className="text-3xl font-bold mb-6">Compose Music</h2>

        {/* Model Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Model</label>
          <select
            value={selectedModel || ''}
            onChange={(e) => setSelectedModel(e.target.value || null)}
            className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white"
          >
            <option value="">Base Model (MusicGen Medium)</option>
            {models
              .filter((m) => !m.is_base)
              .map((model) => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
          </select>
        </div>

        {/* Prompt Input */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Prompt</label>
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="text-sm text-blue-500 hover:text-blue-400"
            >
              {showTemplates ? 'Hide Templates' : 'Browse Templates'}
            </button>
          </div>
          {showTemplates && (
            <div className="mb-4">
              <PromptTemplates
                onSelectTemplate={(templatePrompt) => {
                  setPrompt(templatePrompt);
                  setShowTemplates(false);
                }}
              />
            </div>
          )}
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="A cyber-noir synthwave track with heavy bass and slow tempo..."
            className="w-full px-4 py-3 bg-dark-surface border border-dark-border rounded-lg text-white placeholder-dark-muted resize-none"
            rows={4}
          />
        </div>

        {/* Batch Generator Toggle */}
        <div className="mb-6">
          <button
            onClick={() => setShowBatch(!showBatch)}
            className="text-sm text-blue-500 hover:text-blue-400"
          >
            {showBatch ? 'Hide Batch Generator' : 'Show Batch Generator'}
          </button>
          {showBatch && (
            <div className="mt-4">
              <BatchGenerator onGenerated={() => setShowBatch(false)} />
            </div>
          )}
        </div>

        {/* Duration */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            Duration: {duration}s
          </label>
          <input
            type="range"
            min="10"
            max="120"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Audio Upload (Optional) */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">
            Audio Conditioning (Optional)
          </label>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            className="w-full px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white"
          />
          {audioFile && (
            <p className="mt-2 text-sm text-dark-muted">
              Selected: {audioFile.name}
            </p>
          )}
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-border disabled:cursor-not-allowed text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          {isGenerating ? (
            <>
              <Loader2 className="animate-spin" size={20} />
              Generating...
            </>
          ) : (
            <>
              <Play size={20} />
              Generate Music
            </>
          )}
        </button>

        {/* Task Queue */}
        <div className="mt-12">
          <h3 className="text-xl font-semibold mb-4">Generation Queue</h3>
          <div className="space-y-3">
            {tasks.length === 0 ? (
              <p className="text-dark-muted text-center py-8">
                No generations yet. Start creating!
              </p>
            ) : (
              tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  selectedTaskForTools={selectedTaskForTools}
                  setSelectedTaskForTools={setSelectedTaskForTools}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function TaskCard({ task, selectedTaskForTools, setSelectedTaskForTools }: { task: any; selectedTaskForTools: string | null; setSelectedTaskForTools: (id: string | null) => void }) {
  const { setCurrentTask } = useStore();
  const audioUrl = task.file_path
    ? apiClient.getTaskAudioUrl(task.id)
    : null;

  const getStatusColor = () => {
    switch (task.status) {
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      case 'processing':
        return 'text-blue-500';
      default:
        return 'text-dark-muted';
    }
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-white font-medium mb-1">{task.prompt}</p>
          <div className="flex items-center gap-4 text-sm">
            <span className={getStatusColor()}>{task.status}</span>
            <span className="text-dark-muted">
              {task.progress > 0 ? `${Math.round(task.progress * 100)}%` : 'Queued'}
            </span>
            <span className="text-dark-muted">{task.duration}s</span>
          </div>
          {task.status === 'processing' && (
            <div className="mt-2 w-full bg-dark-border rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full transition-all"
                style={{ width: `${task.progress * 100}%` }}
              />
            </div>
          )}
        </div>
        {task.status === 'completed' && audioUrl && (
          <div className="ml-4 flex gap-2">
            <button
              onClick={() => setCurrentTask(task)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors"
            >
              Play
            </button>
            <button
              onClick={() => setSelectedTaskForTools(selectedTaskForTools === task.id ? null : task.id)}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors"
            >
              Tools
            </button>
          </div>
        )}
      </div>
      {selectedTaskForTools === task.id && (
        <div className="mt-4">
          <AudioTools taskId={task.id} onComplete={() => setSelectedTaskForTools(null)} />
        </div>
      </div>
    </div>
  );
}


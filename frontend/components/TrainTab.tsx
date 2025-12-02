import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { useStore } from '@/store/useStore';
import { Play, Square, Loader2 } from 'lucide-react';

export default function TrainTab() {
  const { trainingStatus } = useStore();
  const [epochs, setEpochs] = useState(10);
  const [learningRate, setLearningRate] = useState(0.0001);
  const [batchSize, setBatchSize] = useState(4);

  const handleProcessDataset = async () => {
    try {
      await apiClient.processDataset();
    } catch (error) {
      console.error('Error processing dataset:', error);
      alert('Failed to process dataset. Please try again.');
    }
  };

  const handleStartTraining = async () => {
    try {
      await apiClient.startTraining(epochs, learningRate, batchSize);
    } catch (error) {
      console.error('Error starting training:', error);
      alert('Failed to start training. Please try again.');
    }
  };

  const handleStopTraining = async () => {
    try {
      await apiClient.stopTraining();
    } catch (error) {
      console.error('Error stopping training:', error);
    }
  };

  const isTraining = trainingStatus?.status === 'training';
  const isProcessingDataset = trainingStatus?.status === 'processing_dataset';

  return (
    <div className="h-full flex flex-col p-8">
      <div className="max-w-4xl mx-auto w-full">
        <h2 className="text-3xl font-bold mb-6">Train Custom Model</h2>

        <div className="bg-dark-surface border border-dark-border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Dataset Setup</h3>
          <p className="text-dark-muted mb-4">
            Place your audio files (WAV/MP3) in the <code className="bg-dark-bg px-2 py-1 rounded">dataset/</code> folder.
            Then click "Process Dataset" to slice and caption your audio files.
          </p>
          <button
            onClick={handleProcessDataset}
            disabled={isProcessingDataset}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-border disabled:cursor-not-allowed text-white font-medium rounded-lg flex items-center gap-2 transition-colors"
          >
            {isProcessingDataset ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Processing...
              </>
            ) : (
              'Process Dataset'
            )}
          </button>
        </div>

        <div className="bg-dark-surface border border-dark-border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Training Parameters</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Epochs: {epochs}
              </label>
              <input
                type="range"
                min="5"
                max="50"
                value={epochs}
                onChange={(e) => setEpochs(Number(e.target.value))}
                className="w-full"
                disabled={isTraining}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Learning Rate: {learningRate}
              </label>
              <input
                type="range"
                min="0.00001"
                max="0.001"
                step="0.00001"
                value={learningRate}
                onChange={(e) => setLearningRate(Number(e.target.value))}
                className="w-full"
                disabled={isTraining}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Batch Size: {batchSize}
              </label>
              <input
                type="range"
                min="1"
                max="8"
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                className="w-full"
                disabled={isTraining}
              />
            </div>
          </div>
        </div>

        <div className="bg-dark-surface border border-dark-border rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Training Control</h3>
          <div className="flex gap-4">
            {!isTraining ? (
              <button
                onClick={handleStartTraining}
                disabled={isProcessingDataset}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-dark-border disabled:cursor-not-allowed text-white font-medium rounded-lg flex items-center gap-2 transition-colors"
              >
                <Play size={20} />
                Start Training
              </button>
            ) : (
              <button
                onClick={handleStopTraining}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg flex items-center gap-2 transition-colors"
              >
                <Square size={20} />
                Stop Training
              </button>
            )}
          </div>
        </div>

        {/* Training Status */}
        {trainingStatus && trainingStatus.status !== 'idle' && (
          <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Training Status</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-dark-muted">Status:</span>
                <span className="text-white capitalize">{trainingStatus.status}</span>
              </div>
              {trainingStatus.total_epochs > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-dark-muted">Epoch:</span>
                  <span className="text-white">
                    {trainingStatus.epoch} / {trainingStatus.total_epochs}
                  </span>
                </div>
              )}
              {trainingStatus.progress > 0 && (
                <div className="mt-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-dark-muted">Progress</span>
                    <span className="text-white">
                      {Math.round(trainingStatus.progress * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-dark-border rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${trainingStatus.progress * 100}%` }}
                    />
                  </div>
                </div>
              )}
              {trainingStatus.message && (
                <p className="mt-4 text-sm text-dark-muted">
                  {trainingStatus.message}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


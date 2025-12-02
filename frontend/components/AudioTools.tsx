import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { Download, Scissors, BarChart3, Loader2 } from 'lucide-react';

interface AudioToolsProps {
  taskId: string;
  onComplete?: () => void;
}

export default function AudioTools({ taskId, onComplete }: AudioToolsProps) {
  const [exporting, setExporting] = useState(false);
  const [separating, setSeparating] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [exportFormat, setExportFormat] = useState('mp3');

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = await apiClient.exportAudio(taskId, exportFormat);
      alert(`Exported to ${result.file_path}`);
      onComplete?.();
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export audio');
    } finally {
      setExporting(false);
    }
  };

  const handleSeparate = async () => {
    setSeparating(true);
    try {
      const result = await apiClient.separateStems(taskId);
      alert(`Stems separated! Check: ${JSON.stringify(result.stems)}`);
      onComplete?.();
    } catch (error) {
      console.error('Separation error:', error);
      alert('Failed to separate stems. Make sure Demucs or Spleeter is installed.');
    } finally {
      setSeparating(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await apiClient.analyzeAudio(taskId);
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze audio');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Export */}
      <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Download size={18} />
          Export Audio
        </h4>
        <div className="flex gap-2">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
            className="px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
          >
            <option value="mp3">MP3</option>
            <option value="flac">FLAC</option>
            <option value="wav">WAV</option>
            <option value="ogg">OGG</option>
          </select>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-border rounded-lg text-sm flex items-center gap-2"
          >
            {exporting ? <Loader2 className="animate-spin" size={16} /> : <Download size={16} />}
            Export
          </button>
        </div>
      </div>

      {/* Stem Separation */}
      <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <Scissors size={18} />
          Stem Separation
        </h4>
        <p className="text-sm text-dark-muted mb-3">
          Separate audio into drums, bass, vocals, and other stems
        </p>
        <button
          onClick={handleSeparate}
          disabled={separating}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-dark-border rounded-lg text-sm flex items-center gap-2"
        >
          {separating ? <Loader2 className="animate-spin" size={16} /> : <Scissors size={16} />}
          Separate Stems
        </button>
      </div>

      {/* Audio Analysis */}
      <div className="bg-dark-surface border border-dark-border rounded-lg p-4">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <BarChart3 size={18} />
          Audio Analysis
        </h4>
        <button
          onClick={handleAnalyze}
          disabled={analyzing}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-dark-border rounded-lg text-sm flex items-center gap-2 mb-3"
        >
          {analyzing ? <Loader2 className="animate-spin" size={16} /> : <BarChart3 size={16} />}
          Analyze
        </button>

        {analysis && (
          <div className="mt-4 p-3 bg-dark-bg rounded-lg space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-dark-muted">Duration:</span>
                <span className="ml-2 text-white">{analysis.duration?.toFixed(2)}s</span>
              </div>
              <div>
                <span className="text-dark-muted">Tempo:</span>
                <span className="ml-2 text-white">{analysis.tempo?.toFixed(0)} BPM</span>
              </div>
              <div>
                <span className="text-dark-muted">Key:</span>
                <span className="ml-2 text-white">{analysis.key || 'Unknown'}</span>
              </div>
              <div>
                <span className="text-dark-muted">Energy:</span>
                <span className="ml-2 text-white">{(analysis.energy * 100)?.toFixed(1)}%</span>
              </div>
              <div>
                <span className="text-dark-muted">Danceability:</span>
                <span className="ml-2 text-white">{(analysis.danceability * 100)?.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


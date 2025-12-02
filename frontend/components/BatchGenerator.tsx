import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { Loader2, Plus, X } from 'lucide-react';

export default function BatchGenerator({ onGenerated }: { onGenerated: () => void }) {
  const [prompts, setPrompts] = useState<string[]>(['']);
  const [duration, setDuration] = useState(30);
  const [isGenerating, setIsGenerating] = useState(false);
  const [variationMode, setVariationMode] = useState(false);
  const [basePrompt, setBasePrompt] = useState('');
  const [numVariations, setNumVariations] = useState(5);

  const addPrompt = () => {
    setPrompts([...prompts, '']);
  };

  const removePrompt = (index: number) => {
    setPrompts(prompts.filter((_, i) => i !== index));
  };

  const updatePrompt = (index: number, value: string) => {
    const newPrompts = [...prompts];
    newPrompts[index] = value;
    setPrompts(newPrompts);
  };

  const handleGenerate = async () => {
    if (variationMode) {
      if (!basePrompt.trim()) {
        alert('Please enter a base prompt');
        return;
      }
      setIsGenerating(true);
      try {
        await apiClient.generateVariations(basePrompt, numVariations, duration);
        onGenerated();
        setBasePrompt('');
      } catch (error) {
        console.error('Error generating variations:', error);
        alert('Failed to generate variations');
      } finally {
        setIsGenerating(false);
      }
    } else {
      const validPrompts = prompts.filter((p) => p.trim());
      if (validPrompts.length === 0) {
        alert('Please enter at least one prompt');
        return;
      }
      setIsGenerating(true);
      try {
        await apiClient.batchGenerate(validPrompts, duration);
        onGenerated();
        setPrompts(['']);
      } catch (error) {
        console.error('Error in batch generation:', error);
        alert('Failed to generate batch');
      } finally {
        setIsGenerating(false);
      }
    }
  };

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Batch Generation</h3>

      {/* Mode Toggle */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setVariationMode(false)}
          className={`px-4 py-2 rounded-lg text-sm transition-colors ${
            !variationMode
              ? 'bg-blue-600 text-white'
              : 'bg-dark-border text-dark-text hover:bg-dark-border/80'
          }`}
        >
          Multiple Prompts
        </button>
        <button
          onClick={() => setVariationMode(true)}
          className={`px-4 py-2 rounded-lg text-sm transition-colors ${
            variationMode
              ? 'bg-blue-600 text-white'
              : 'bg-dark-border text-dark-text hover:bg-dark-border/80'
          }`}
        >
          Variations
        </button>
      </div>

      {variationMode ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Base Prompt</label>
            <textarea
              value={basePrompt}
              onChange={(e) => setBasePrompt(e.target.value)}
              placeholder="Enter a prompt to generate variations of..."
              className="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Number of Variations: {numVariations}
            </label>
            <input
              type="range"
              min="2"
              max="20"
              value={numVariations}
              onChange={(e) => setNumVariations(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {prompts.map((prompt, index) => (
            <div key={index} className="flex gap-2">
              <textarea
                value={prompt}
                onChange={(e) => updatePrompt(index, e.target.value)}
                placeholder={`Prompt ${index + 1}...`}
                className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                rows={2}
              />
              {prompts.length > 1 && (
                <button
                  onClick={() => removePrompt(index)}
                  className="px-3 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
                >
                  <X size={18} />
                </button>
              )}
            </div>
          ))}
          <button
            onClick={addPrompt}
            className="w-full px-4 py-2 bg-dark-border hover:bg-dark-border/80 rounded-lg flex items-center justify-center gap-2"
          >
            <Plus size={18} />
            Add Prompt
          </button>
        </div>
      )}

      <div className="mt-4">
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

      <button
        onClick={handleGenerate}
        disabled={isGenerating}
        className="w-full mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-dark-border disabled:cursor-not-allowed text-white font-medium rounded-lg flex items-center justify-center gap-2"
      >
        {isGenerating ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Generating...
          </>
        ) : (
          `Generate ${variationMode ? numVariations : prompts.filter((p) => p.trim()).length} Track${variationMode ? 's' : prompts.filter((p) => p.trim()).length !== 1 ? 's' : ''}`
        )}
      </button>
    </div>
  );
}


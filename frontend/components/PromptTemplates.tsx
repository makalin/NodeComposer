import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Sparkles, Search, Plus } from 'lucide-react';

interface Template {
  [key: string]: string;
}

export default function PromptTemplates({ onSelectTemplate }: { onSelectTemplate: (prompt: string) => void }) {
  const [templates, setTemplates] = useState<Record<string, Template>>({});
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Record<string, Template>>({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTemplate, setNewTemplate] = useState({ category: '', name: '', prompt: '' });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await apiClient.getTemplates();
      setTemplates(data);
      if (!selectedCategory && Object.keys(data).length > 0) {
        setSelectedCategory(Object.keys(data)[0]);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults({});
      return;
    }
    try {
      const results = await apiClient.searchTemplates(searchQuery);
      setSearchResults(results);
    } catch (error) {
      console.error('Error searching templates:', error);
    }
  };

  const handleCreateTemplate = async () => {
    if (!newTemplate.category || !newTemplate.name || !newTemplate.prompt) {
      alert('Please fill in all fields');
      return;
    }
    try {
      await apiClient.createTemplate(newTemplate.category, newTemplate.name, newTemplate.prompt);
      setNewTemplate({ category: '', name: '', prompt: '' });
      setShowAddForm(false);
      loadTemplates();
    } catch (error) {
      console.error('Error creating template:', error);
      alert('Failed to create template');
    }
  };

  const displayTemplates = searchQuery ? searchResults : templates;
  const categories = Object.keys(displayTemplates);

  return (
    <div className="bg-dark-surface border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles size={20} />
          Prompt Templates
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm flex items-center gap-2"
        >
          <Plus size={16} />
          Add Template
        </button>
      </div>

      {/* Search */}
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder="Search templates..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="flex-1 px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
        />
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-dark-border hover:bg-dark-border/80 rounded-lg"
        >
          <Search size={18} />
        </button>
      </div>

      {/* Add Template Form */}
      {showAddForm && (
        <div className="mb-4 p-4 bg-dark-bg rounded-lg border border-dark-border">
          <input
            type="text"
            placeholder="Category (e.g., genres, moods)"
            value={newTemplate.category}
            onChange={(e) => setNewTemplate({ ...newTemplate, category: e.target.value })}
            className="w-full mb-2 px-3 py-2 bg-dark-surface border border-dark-border rounded text-white"
          />
          <input
            type="text"
            placeholder="Template name"
            value={newTemplate.name}
            onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
            className="w-full mb-2 px-3 py-2 bg-dark-surface border border-dark-border rounded text-white"
          />
          <textarea
            placeholder="Prompt text"
            value={newTemplate.prompt}
            onChange={(e) => setNewTemplate({ ...newTemplate, prompt: e.target.value })}
            className="w-full mb-2 px-3 py-2 bg-dark-surface border border-dark-border rounded text-white"
            rows={3}
          />
          <div className="flex gap-2">
            <button
              onClick={handleCreateTemplate}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm"
            >
              Create
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 bg-dark-border hover:bg-dark-border/80 rounded-lg text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Categories */}
      {categories.length > 0 && (
        <div className="flex gap-2 mb-4 flex-wrap">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-dark-border text-dark-text hover:bg-dark-border/80'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      )}

      {/* Templates */}
      {selectedCategory && displayTemplates[selectedCategory] && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(displayTemplates[selectedCategory]).map(([name, prompt]) => (
            <div
              key={name}
              className="p-3 bg-dark-bg border border-dark-border rounded-lg hover:border-blue-600 cursor-pointer transition-colors"
              onClick={() => onSelectTemplate(prompt)}
            >
              <div className="font-medium text-white mb-1">{name}</div>
              <div className="text-sm text-dark-muted line-clamp-2">{prompt}</div>
            </div>
          ))}
        </div>
      )}

      {categories.length === 0 && (
        <p className="text-center text-dark-muted py-8">No templates found</p>
      )}
    </div>
  );
}


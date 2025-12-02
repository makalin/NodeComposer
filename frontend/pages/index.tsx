import { useState } from 'react';
import Layout from '@/components/Layout';
import ComposeTab from '@/components/ComposeTab';
import TrainTab from '@/components/TrainTab';
import LibraryTab from '@/components/LibraryTab';

type Tab = 'compose' | 'train' | 'library';

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('compose');

  return (
    <Layout>
      <div className="flex h-full">
        {/* Sidebar */}
        <div className="w-64 bg-dark-surface border-r border-dark-border flex flex-col">
          <div className="p-6 border-b border-dark-border">
            <h1 className="text-2xl font-bold text-white">🎵 NodeComposer</h1>
            <p className="text-sm text-dark-muted mt-1">Local AI Music Generator</p>
          </div>
          
          <nav className="flex-1 p-4">
            <button
              onClick={() => setActiveTab('compose')}
              className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition-colors ${
                activeTab === 'compose'
                  ? 'bg-blue-600 text-white'
                  : 'text-dark-text hover:bg-dark-border'
              }`}
            >
              Compose
            </button>
            <button
              onClick={() => setActiveTab('train')}
              className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition-colors ${
                activeTab === 'train'
                  ? 'bg-blue-600 text-white'
                  : 'text-dark-text hover:bg-dark-border'
              }`}
            >
              Train
            </button>
            <button
              onClick={() => setActiveTab('library')}
              className={`w-full text-left px-4 py-3 rounded-lg mb-2 transition-colors ${
                activeTab === 'library'
                  ? 'bg-blue-600 text-white'
                  : 'text-dark-text hover:bg-dark-border'
              }`}
            >
              Library
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          {activeTab === 'compose' && <ComposeTab />}
          {activeTab === 'train' && <TrainTab />}
          {activeTab === 'library' && <LibraryTab />}
        </div>
      </div>
    </Layout>
  );
}


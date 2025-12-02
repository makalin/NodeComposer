import { useStore } from '@/store/useStore';
import { apiClient } from '@/lib/api';
import { Play, Trash2 } from 'lucide-react';
import { useState } from 'react';

export default function LibraryTab() {
  const { tasks, setCurrentTask } = useStore();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const completedTasks = tasks.filter((task) => task.status === 'completed');

  const handleDelete = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this generation?')) return;

    setDeletingId(taskId);
    try {
      await apiClient.deleteTask(taskId);
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="h-full flex flex-col p-8">
      <div className="max-w-6xl mx-auto w-full">
        <h2 className="text-3xl font-bold mb-6">Library</h2>

        {completedTasks.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-dark-muted text-lg">
              No completed generations yet.
            </p>
            <p className="text-dark-muted text-sm mt-2">
              Go to the Compose tab to create your first track!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {completedTasks.map((task) => {
              const audioUrl = apiClient.getTaskAudioUrl(task.id);
              return (
                <div
                  key={task.id}
                  className="bg-dark-surface border border-dark-border rounded-lg p-4 hover:border-blue-600 transition-colors"
                >
                  <div className="mb-3">
                    <p className="text-white font-medium line-clamp-2 mb-2">
                      {task.prompt}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-dark-muted">
                      <span>{task.duration}s</span>
                      <span>
                        {new Date(task.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentTask(task)}
                      className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                    >
                      <Play size={16} />
                      Play
                    </button>
                    <button
                      onClick={() => handleDelete(task.id)}
                      disabled={deletingId === task.id}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-dark-border disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


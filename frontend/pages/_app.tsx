import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { useStore } from '@/store/useStore';

export default function App({ Component, pageProps }: AppProps) {
  const { setTasks, setModels, setTrainingStatus } = useStore();

  useEffect(() => {
    // Poll for updates
    const pollInterval = setInterval(async () => {
      try {
        const [tasks, models, trainingStatus] = await Promise.all([
          apiClient.getTasks(),
          apiClient.getModels(),
          apiClient.getTrainingStatus(),
        ]);
        setTasks(tasks);
        setModels(models);
        setTrainingStatus(trainingStatus);
      } catch (error) {
        console.error('Error polling API:', error);
      }
    }, 2000); // Poll every 2 seconds

    // Initial load
    Promise.all([
      apiClient.getTasks(),
      apiClient.getModels(),
      apiClient.getTrainingStatus(),
    ]).then(([tasks, models, trainingStatus]) => {
      setTasks(tasks);
      setModels(models);
      setTrainingStatus(trainingStatus);
    });

    return () => clearInterval(pollInterval);
  }, [setTasks, setModels, setTrainingStatus]);

  return <Component {...pageProps} />;
}


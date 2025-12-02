import { useEffect, useRef, useState } from 'react';
import { useStore } from '@/store/useStore';
import { apiClient } from '@/lib/api';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX } from 'lucide-react';

export default function AudioPlayer() {
  const { currentTask, setCurrentTask } = useStore();
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [currentTask]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.play();
    } else {
      audio.pause();
    }
  }, [isPlaying]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.volume = isMuted ? 0 : volume;
  }, [volume, isMuted]);

  if (!currentTask || currentTask.status !== 'completed') {
    return null;
  }

  const audioUrl = apiClient.getTaskAudioUrl(currentTask.id);
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleSkip = (seconds: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(duration, audio.currentTime + seconds));
  };

  return (
    <div className="bg-dark-surface border-t border-dark-border p-4">
      <audio ref={audioRef} src={audioUrl} />
      
      <div className="max-w-6xl mx-auto">
        {/* Progress Bar */}
        <div
          className="h-1 bg-dark-border rounded-full mb-4 cursor-pointer"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-blue-600 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="flex items-center gap-4">
          {/* Track Info */}
          <div className="flex-1 min-w-0">
            <p className="text-white font-medium truncate">{currentTask.prompt}</p>
            <p className="text-sm text-dark-muted">
              {formatTime(currentTime)} / {formatTime(duration)}
            </p>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleSkip(-10)}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              <SkipBack size={20} />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-3 bg-blue-600 hover:bg-blue-700 rounded-full transition-colors"
            >
              {isPlaying ? <Pause size={20} /> : <Play size={20} />}
            </button>
            <button
              onClick={() => handleSkip(10)}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              <SkipForward size={20} />
            </button>
          </div>

          {/* Volume */}
          <div className="flex items-center gap-2 w-32">
            <button
              onClick={() => setIsMuted(!isMuted)}
              className="p-2 hover:bg-dark-border rounded-lg transition-colors"
            >
              {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
              className="flex-1"
            />
          </div>

          {/* Close */}
          <button
            onClick={() => setCurrentTask(null)}
            className="px-4 py-2 text-dark-muted hover:text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}


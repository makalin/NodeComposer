"""
Audio processing utilities
"""

import librosa
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import soundfile as sf

class AudioProcessor:
    def __init__(self):
        self.sample_rate = 32000  # MusicGen default sample rate

    def load_audio(self, file_path: Path, target_sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        if target_sr is None:
            target_sr = self.sample_rate
        
        y, sr = librosa.load(str(file_path), sr=target_sr)
        return y, sr

    def save_audio(self, audio: np.ndarray, file_path: Path, sample_rate: int = 32000):
        """Save audio file"""
        sf.write(str(file_path), audio, sample_rate)

    def slice_audio(self, audio: np.ndarray, sample_rate: int, duration: float = 30.0) -> list:
        """Slice audio into chunks of specified duration"""
        chunk_samples = int(duration * sample_rate)
        chunks = []
        
        for i in range(0, len(audio), chunk_samples):
            chunk = audio[i:i + chunk_samples]
            if len(chunk) >= chunk_samples * 0.8:  # Only include chunks that are at least 80% of target duration
                chunks.append(chunk)
        
        return chunks

    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio

    def resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)


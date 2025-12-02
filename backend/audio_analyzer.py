"""
Audio analysis tools for analyzing generated music
"""

import librosa
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import json

class AudioAnalyzer:
    """Analyze audio files and extract features"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
    
    def analyze(self, audio_path: Path) -> Dict:
        """
        Perform comprehensive audio analysis
        
        Returns:
            Dictionary with analysis results
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
        
        analysis = {
            "duration": len(y) / sr,
            "sample_rate": sr,
            "tempo": self._estimate_tempo(y, sr),
            "key": self._estimate_key(y, sr),
            "energy": self._calculate_energy(y),
            "danceability": self._calculate_danceability(y, sr),
            "spectral_features": self._spectral_analysis(y, sr),
            "rhythm_features": self._rhythm_analysis(y, sr),
            "harmonic_features": self._harmonic_analysis(y, sr)
        }
        
        return analysis
    
    def _estimate_tempo(self, y: np.ndarray, sr: int) -> float:
        """Estimate tempo in BPM"""
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        except:
            return 0.0
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> str:
        """Estimate musical key"""
        try:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            key_idx = np.argmax(chroma_mean)
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            return keys[key_idx]
        except:
            return "Unknown"
    
    def _calculate_energy(self, y: np.ndarray) -> float:
        """Calculate energy level (RMS)"""
        rms = librosa.feature.rms(y=y)[0]
        return float(np.mean(rms))
    
    def _calculate_danceability(self, y: np.ndarray, sr: int) -> float:
        """Calculate danceability score"""
        try:
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            if len(onset_times) < 2:
                return 0.0
            
            # Calculate regularity of beats
            intervals = np.diff(onset_times)
            if len(intervals) == 0:
                return 0.0
            
            # Regularity score (lower std = more regular = more danceable)
            regularity = 1.0 / (1.0 + np.std(intervals))
            
            # Energy component
            energy = self._calculate_energy(y)
            energy_norm = min(energy * 10, 1.0)  # Normalize
            
            danceability = (regularity * 0.6 + energy_norm * 0.4)
            return float(np.clip(danceability, 0.0, 1.0))
        except:
            return 0.0
    
    def _spectral_analysis(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze spectral features"""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        return {
            "centroid_mean": float(np.mean(spectral_centroids)),
            "centroid_std": float(np.std(spectral_centroids)),
            "rolloff_mean": float(np.mean(spectral_rolloff)),
            "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate))
        }
    
    def _rhythm_analysis(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze rhythm features"""
        try:
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)
            
            if len(onset_times) < 2:
                return {
                    "onset_count": 0,
                    "onset_rate": 0.0,
                    "rhythm_regularity": 0.0
                }
            
            intervals = np.diff(onset_times)
            duration = len(y) / sr
            
            return {
                "onset_count": len(onset_times),
                "onset_rate": len(onset_times) / duration,
                "rhythm_regularity": float(1.0 / (1.0 + np.std(intervals)))
            }
        except:
            return {
                "onset_count": 0,
                "onset_rate": 0.0,
                "rhythm_regularity": 0.0
            }
    
    def _harmonic_analysis(self, y: np.ndarray, sr: int) -> Dict:
        """Analyze harmonic features"""
        try:
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            harmonic_ratio = np.sum(np.abs(y_harmonic)) / (np.sum(np.abs(y)) + 1e-10)
            percussive_ratio = np.sum(np.abs(y_percussive)) / (np.sum(np.abs(y)) + 1e-10)
            
            return {
                "harmonic_ratio": float(harmonic_ratio),
                "percussive_ratio": float(percussive_ratio)
            }
        except:
            return {
                "harmonic_ratio": 0.0,
                "percussive_ratio": 0.0
            }
    
    def get_waveform_data(self, audio_path: Path, num_samples: int = 1000) -> Dict:
        """
        Get waveform data for visualization
        
        Returns:
            Dictionary with time and amplitude arrays
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
        duration = len(y) / sr
        
        # Downsample for visualization
        step = max(1, len(y) // num_samples)
        y_downsampled = y[::step]
        time = np.linspace(0, duration, len(y_downsampled))
        
        return {
            "time": time.tolist(),
            "amplitude": y_downsampled.tolist(),
            "duration": duration
        }
    
    def get_spectrogram_data(
        self,
        audio_path: Path,
        n_fft: int = 2048,
        hop_length: int = 512
    ) -> Dict:
        """
        Get spectrogram data for visualization
        
        Returns:
            Dictionary with frequency, time, and magnitude arrays
        """
        y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
        
        D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(D)
        magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
        
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        times = librosa.frames_to_time(np.arange(magnitude_db.shape[1]), sr=sr, hop_length=hop_length)
        
        return {
            "frequencies": frequencies.tolist(),
            "times": times.tolist(),
            "magnitude_db": magnitude_db.tolist()
        }


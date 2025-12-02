"""
Stem separation service for extracting drums, bass, vocals, and other instruments
Uses Demucs or Spleeter for source separation
"""

import torch
import torchaudio
from pathlib import Path
import subprocess
import os
from typing import Dict, Optional, List
import json

class StemSeparator:
    def __init__(self, method: str = "demucs"):
        """
        Initialize stem separator
        
        Args:
            method: "demucs" or "spleeter"
        """
        self.method = method
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        
        if method == "demucs":
            self._init_demucs()
        elif method == "spleeter":
            self._init_spleeter()
    
    def _init_demucs(self):
        """Initialize Demucs model"""
        try:
            import demucs
            # Load pre-trained model
            self.model = demucs.pretrained.get_model('htdemucs')
            self.model.to(self.device)
            self.model.eval()
        except ImportError:
            print("Demucs not installed. Install with: pip install demucs")
            self.model = None
        except Exception as e:
            print(f"Error loading Demucs model: {e}")
            self.model = None
    
    def _init_spleeter(self):
        """Initialize Spleeter (uses command-line)"""
        # Spleeter is typically used via command line
        self.model = "spleeter"
    
    def separate(
        self,
        audio_path: Path,
        output_dir: Optional[Path] = None,
        stems: List[str] = ["drums", "bass", "other", "vocals"]
    ) -> Dict[str, str]:
        """
        Separate audio into stems
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save stems (default: same as input)
            stems: List of stems to extract
            
        Returns:
            Dictionary mapping stem names to file paths
        """
        if output_dir is None:
            output_dir = audio_path.parent / f"{audio_path.stem}_stems"
        output_dir.mkdir(exist_ok=True)
        
        if self.method == "demucs" and self.model:
            return self._separate_demucs(audio_path, output_dir, stems)
        elif self.method == "spleeter":
            return self._separate_spleeter(audio_path, output_dir, stems)
        else:
            raise RuntimeError(f"Stem separation method '{self.method}' not available")
    
    def _separate_demucs(
        self,
        audio_path: Path,
        output_dir: Path,
        stems: List[str]
    ) -> Dict[str, str]:
        """Separate using Demucs"""
        try:
            import demucs.separate
            
            # Demucs separates into: drums, bass, other, vocals
            demucs.separate.main([
                "--mp3",  # Output as MP3
                "--two-stems=vocals",  # Separate vocals
                str(audio_path),
                "-o", str(output_dir)
            ])
            
            # Map Demucs output to our stem names
            stem_files = {}
            demucs_stems = ["drums", "bass", "other", "vocals"]
            
            for stem in stems:
                if stem in demucs_stems:
                    # Demucs creates: output_dir/htdemucs/track_name/stem.wav
                    # Find the actual output structure
                    for subdir in output_dir.iterdir():
                        if subdir.is_dir():
                            stem_file = subdir / f"{stem}.wav"
                            if stem_file.exists():
                                stem_files[stem] = str(stem_file)
                                break
            
            return stem_files
            
        except Exception as e:
            print(f"Error in Demucs separation: {e}")
            raise
    
    def _separate_spleeter(
        self,
        audio_path: Path,
        output_dir: Path,
        stems: List[str]
    ) -> Dict[str, str]:
        """Separate using Spleeter (command-line)"""
        try:
            # Spleeter command: spleeter separate -p spleeter:4stems-16kHz -o output input.wav
            cmd = [
                "spleeter", "separate",
                "-p", "spleeter:4stems-16kHz",
                "-o", str(output_dir),
                str(audio_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Spleeter error: {result.stderr}")
            
            # Spleeter creates: output_dir/track_name/stem.wav
            track_name = audio_path.stem
            stem_files = {}
            
            for stem in stems:
                stem_file = output_dir / track_name / f"{stem}.wav"
                if stem_file.exists():
                    stem_files[stem] = str(stem_file)
            
            return stem_files
            
        except FileNotFoundError:
            raise RuntimeError("Spleeter not found. Install with: pip install spleeter")
        except Exception as e:
            print(f"Error in Spleeter separation: {e}")
            raise
    
    def separate_to_wav(
        self,
        audio_path: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """Separate and convert all stems to WAV format"""
        stems = self.separate(audio_path, output_dir)
        
        # Convert to WAV if needed
        wav_stems = {}
        for stem_name, stem_path in stems.items():
            stem_path_obj = Path(stem_path)
            if stem_path_obj.suffix != ".wav":
                # Convert to WAV using ffmpeg
                wav_path = stem_path_obj.with_suffix(".wav")
                self._convert_to_wav(stem_path_obj, wav_path)
                wav_stems[stem_name] = str(wav_path)
            else:
                wav_stems[stem_name] = stem_path
        
        return wav_stems
    
    def _convert_to_wav(self, input_path: Path, output_path: Path):
        """Convert audio file to WAV using ffmpeg"""
        try:
            subprocess.run(
                ["ffmpeg", "-i", str(input_path), "-y", str(output_path)],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg conversion failed: {e}")
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")


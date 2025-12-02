"""
Audio export utilities for converting and exporting audio files
Supports MP3, FLAC, OGG, and other formats
"""

import subprocess
from pathlib import Path
from typing import Optional, Dict
import json

class AudioExporter:
    """Handle audio format conversion and export"""
    
    SUPPORTED_FORMATS = ["wav", "mp3", "flac", "ogg", "m4a", "aac"]
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg to use audio export features."
            )
    
    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        format: str = "mp3",
        bitrate: str = "320k",
        sample_rate: Optional[int] = None,
        normalize: bool = True
    ) -> Path:
        """
        Convert audio file to different format
        
        Args:
            input_path: Input audio file path
            output_path: Output file path (auto-generated if None)
            format: Output format (mp3, flac, wav, ogg, etc.)
            bitrate: Audio bitrate (e.g., "320k", "192k")
            sample_rate: Target sample rate (None = keep original)
            normalize: Normalize audio levels
            
        Returns:
            Path to converted file
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")
        
        if output_path is None:
            output_path = input_path.with_suffix(f".{format}")
        
        cmd = ["ffmpeg", "-i", str(input_path)]
        
        # Audio codec based on format
        if format == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-b:a", bitrate])
        elif format == "flac":
            cmd.extend(["-codec:a", "flac"])
        elif format == "ogg":
            cmd.extend(["-codec:a", "libvorbis", "-b:a", bitrate])
        elif format == "m4a" or format == "aac":
            cmd.extend(["-codec:a", "aac", "-b:a", bitrate])
        elif format == "wav":
            cmd.extend(["-codec:a", "pcm_s16le"])
        
        # Sample rate
        if sample_rate:
            cmd.extend(["-ar", str(sample_rate)])
        
        # Normalize
        if normalize:
            cmd.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])
        
        cmd.extend(["-y", str(output_path)])
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio conversion failed: {e.stderr.decode()}")
    
    def export_multiple_formats(
        self,
        input_path: Path,
        output_dir: Optional[Path] = None,
        formats: Optional[list] = None,
        bitrate: str = "320k"
    ) -> Dict[str, Path]:
        """
        Export audio in multiple formats
        
        Args:
            input_path: Input audio file
            output_dir: Output directory (default: same as input)
            formats: List of formats to export (default: ["mp3", "flac", "wav"])
            bitrate: Audio bitrate
            
        Returns:
            Dictionary mapping format names to file paths
        """
        if formats is None:
            formats = ["mp3", "flac", "wav"]
        
        if output_dir is None:
            output_dir = input_path.parent
        else:
            output_dir.mkdir(exist_ok=True)
        
        exported = {}
        base_name = input_path.stem
        
        for fmt in formats:
            output_path = output_dir / f"{base_name}.{fmt}"
            exported[fmt] = self.convert(
                input_path,
                output_path,
                format=fmt,
                bitrate=bitrate
            )
        
        return exported
    
    def extract_metadata(self, audio_path: Path) -> Dict:
        """
        Extract metadata from audio file using ffprobe
        
        Returns:
            Dictionary with audio metadata
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(audio_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            metadata = json.loads(result.stdout.decode())
            return metadata
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract metadata: {e}")
        except json.JSONDecodeError:
            raise RuntimeError("Failed to parse metadata")
    
    def get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        metadata = self.extract_metadata(audio_path)
        duration = float(metadata.get("format", {}).get("duration", 0))
        return duration
    
    def trim_audio(
        self,
        input_path: Path,
        output_path: Path,
        start_time: float,
        end_time: Optional[float] = None,
        duration: Optional[float] = None
    ) -> Path:
        """
        Trim audio file
        
        Args:
            input_path: Input audio file
            output_path: Output file path
            start_time: Start time in seconds
            end_time: End time in seconds (or use duration)
            duration: Duration in seconds (alternative to end_time)
        """
        cmd = ["ffmpeg", "-i", str(input_path)]
        
        if end_time:
            cmd.extend(["-ss", str(start_time), "-to", str(end_time)])
        elif duration:
            cmd.extend(["-ss", str(start_time), "-t", str(duration)])
        else:
            raise ValueError("Either end_time or duration must be provided")
        
        cmd.extend(["-c", "copy", "-y", str(output_path)])
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio trimming failed: {e}")


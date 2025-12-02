"""
Batch generation service for generating multiple tracks from prompts
"""

from typing import List, Dict, Optional
from pathlib import Path
import asyncio
from database import get_db
from models import GenerationTask
from musicgen_service import MusicGenService
import uuid

class BatchGenerator:
    """Handle batch music generation from multiple prompts"""
    
    def __init__(self, musicgen_service: MusicGenService):
        self.musicgen_service = musicgen_service
    
    def generate_batch(
        self,
        prompts: List[str],
        duration: float = 30.0,
        model_id: Optional[str] = None,
        guidance_scale: float = 3.0,
        temperature: float = 1.0,
        max_concurrent: int = 1
    ) -> List[str]:
        """
        Generate multiple tracks from a list of prompts
        
        Args:
            prompts: List of text prompts
            duration: Duration for each track
            model_id: Optional model checkpoint ID
            guidance_scale: Guidance scale for generation
            temperature: Temperature for generation
            max_concurrent: Maximum concurrent generations (1 for sequential)
            
        Returns:
            List of task IDs
        """
        task_ids = []
        
        if max_concurrent == 1:
            # Sequential generation
            for prompt in prompts:
                task = self.musicgen_service.queue_generation(
                    prompt=prompt,
                    duration=duration,
                    model_id=model_id,
                    guidance_scale=guidance_scale,
                    temperature=temperature
                )
                task_ids.append(task.id)
        else:
            # Concurrent generation (limited by max_concurrent)
            # This would require async implementation
            for prompt in prompts:
                task = self.musicgen_service.queue_generation(
                    prompt=prompt,
                    duration=duration,
                    model_id=model_id,
                    guidance_scale=guidance_scale,
                    temperature=temperature
                )
                task_ids.append(task.id)
        
        return task_ids
    
    def generate_from_file(
        self,
        prompts_file: Path,
        duration: float = 30.0,
        model_id: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate tracks from prompts in a text file (one per line)
        
        Args:
            prompts_file: Path to text file with prompts (one per line)
            duration: Duration for each track
            model_id: Optional model checkpoint ID
            **kwargs: Additional generation parameters
            
        Returns:
            List of task IDs
        """
        with open(prompts_file, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        return self.generate_batch(
            prompts=prompts,
            duration=duration,
            model_id=model_id,
            **kwargs
        )
    
    def generate_variations(
        self,
        base_prompt: str,
        num_variations: int = 5,
        duration: float = 30.0,
        model_id: Optional[str] = None,
        temperature_range: tuple = (0.8, 1.2)
    ) -> List[str]:
        """
        Generate variations of a base prompt with different temperatures
        
        Args:
            base_prompt: Base prompt text
            num_variations: Number of variations to generate
            duration: Duration for each track
            model_id: Optional model checkpoint ID
            temperature_range: (min, max) temperature range
            
        Returns:
            List of task IDs
        """
        import random
        
        task_ids = []
        min_temp, max_temp = temperature_range
        
        for i in range(num_variations):
            temperature = random.uniform(min_temp, max_temp)
            task = self.musicgen_service.queue_generation(
                prompt=base_prompt,
                duration=duration,
                model_id=model_id,
                temperature=temperature
            )
            task_ids.append(task.id)
        
        return task_ids
    
    def generate_playlist(
        self,
        theme: str,
        num_tracks: int = 10,
        duration: float = 30.0,
        model_id: Optional[str] = None
    ) -> List[str]:
        """
        Generate a themed playlist
        
        Args:
            theme: Theme for the playlist (e.g., "cyberpunk", "ambient")
            num_tracks: Number of tracks in playlist
            duration: Duration for each track
            model_id: Optional model checkpoint ID
            
        Returns:
            List of task IDs
        """
        # Generate prompts based on theme
        prompts = self._generate_theme_prompts(theme, num_tracks)
        
        return self.generate_batch(
            prompts=prompts,
            duration=duration,
            model_id=model_id
        )
    
    def _generate_theme_prompts(self, theme: str, num_tracks: int) -> List[str]:
        """Generate prompts based on a theme"""
        # Simple prompt variations - could be enhanced with LLM
        variations = [
            f"A {theme} track with",
            f"An energetic {theme} song featuring",
            f"A mellow {theme} composition with",
            f"A dark {theme} piece with",
            f"An uplifting {theme} melody with",
            f"A cinematic {theme} soundtrack with",
            f"A rhythmic {theme} beat with",
            f"An atmospheric {theme} soundscape with",
            f"A powerful {theme} anthem with",
            f"A gentle {theme} ballad with"
        ]
        
        elements = [
            "heavy bass",
            "synthesizers",
            "drums",
            "piano",
            "strings",
            "guitar",
            "electronic elements",
            "ambient textures",
            "rhythmic patterns",
            "melodic hooks"
        ]
        
        import random
        prompts = []
        for i in range(num_tracks):
            variation = random.choice(variations)
            element = random.choice(elements)
            prompts.append(f"{variation} {element}.")
        
        return prompts


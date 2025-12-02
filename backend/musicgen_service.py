"""
MusicGen service for music generation
"""

import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write, audio_read
import os
from pathlib import Path
from typing import Optional
import threading
from queue import Queue
from database import get_db
from models import GenerationTask
import uuid

class MusicGenService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.model_name = "facebook/musicgen-medium"
        self.generation_queue = Queue()
        self.is_processing = False
        self.load_model()
        self._start_worker()

    def load_model(self, model_path: Optional[str] = None):
        """Load MusicGen model"""
        try:
            if model_path and os.path.exists(model_path):
                # Load custom fine-tuned model
                self.model = MusicGen.get_pretrained(model_path, device=self.device)
            else:
                # Load base model
                self.model = MusicGen.get_pretrained(self.model_name, device=self.device)
            self.model.set_generation_params(duration=30)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None

    def is_gpu_available(self) -> bool:
        """Check if GPU is available"""
        return torch.cuda.is_available()

    def queue_generation(
        self,
        prompt: str,
        duration: float = 30.0,
        model_id: Optional[str] = None,
        guidance_scale: float = 3.0,
        temperature: float = 1.0,
        audio_conditioning: Optional[Path] = None
    ) -> GenerationTask:
        """Queue a generation task"""
        db = next(get_db())
        
        task = GenerationTask(
            id=str(uuid.uuid4()),
            prompt=prompt,
            duration=duration,
            status="queued",
            model_id=model_id
        )
        
        db.add(task)
        db.commit()
        
        # Add to queue
        self.generation_queue.put({
            "task_id": task.id,
            "prompt": prompt,
            "duration": duration,
            "model_id": model_id,
            "guidance_scale": guidance_scale,
            "temperature": temperature,
            "audio_conditioning": audio_conditioning
        })
        
        return task

    def _start_worker(self):
        """Start background worker thread"""
        def worker():
            while True:
                try:
                    if not self.generation_queue.empty():
                        self.is_processing = True
                        task_data = self.generation_queue.get()
                        self._process_generation(task_data)
                        self.is_processing = False
                except Exception as e:
                    print(f"Error in generation worker: {e}")
                    self.is_processing = False

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _process_generation(self, task_data: dict):
        """Process a generation task"""
        db = next(get_db())
        task = db.query(GenerationTask).filter(GenerationTask.id == task_data["task_id"]).first()
        
        if not task:
            return

        try:
            task.status = "processing"
            task.progress = 0.1
            db.commit()

            # Load model if needed
            if task_data.get("model_id"):
                # Load custom model checkpoint
                # This would need to be implemented based on your checkpoint storage
                pass

            # Set generation parameters
            self.model.set_generation_params(
                duration=task_data["duration"],
                temperature=task_data["temperature"],
                cfg_coef=task_data["guidance_scale"]
            )

            task.progress = 0.3
            db.commit()

            # Generate music
            if task_data.get("audio_conditioning"):
                # Audio-to-audio generation
                # Load conditioning audio
                from audiocraft.data.audio import audio_read
                melody, sr = audio_read(task_data["audio_conditioning"])
                wav = self.model.generate_with_chroma(
                    descriptions=[task_data["prompt"]],
                    melody_wavs=melody[None],
                    melody_sample_rate=sr,
                    progress=True
                )
            else:
                # Text-to-music generation
                wav = self.model.generate(
                    descriptions=[task_data["prompt"]],
                    progress=True
                )

            task.progress = 0.8
            db.commit()

            # Save audio file
            output_dir = Path("generations")
            output_dir.mkdir(exist_ok=True)
            
            filename = f"generation_{task.id}"
            audio_write(
                str(output_dir / filename),
                wav[0].cpu(),
                self.model.sample_rate,
                format="wav"
            )

            file_path = str(output_dir / f"{filename}.wav")
            task.file_path = file_path
            task.status = "completed"
            task.progress = 1.0
            db.commit()

        except Exception as e:
            print(f"Error generating music: {e}")
            task.status = "failed"
            task.progress = 0.0
            db.commit()


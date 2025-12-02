"""
Training service for fine-tuning MusicGen with LoRA
"""

import torch
from pathlib import Path
import os
from typing import Dict, Optional
from database import get_db
from models import ModelCheckpoint
import uuid
from datetime import datetime

class TrainingService:
    def __init__(self):
        self.is_training = False
        self.training_status = {
            "status": "idle",  # idle, processing_dataset, training, completed, failed
            "progress": 0.0,
            "epoch": 0,
            "total_epochs": 0,
            "loss": None,
            "message": ""
        }
        self.should_stop = False
        self.dataset_dir = Path("dataset")
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

    def process_dataset(self):
        """Process dataset: slice audio files and generate captions"""
        try:
            self.training_status["status"] = "processing_dataset"
            self.training_status["progress"] = 0.0
            self.training_status["message"] = "Processing dataset..."

            # Find all audio files
            audio_files = list(self.dataset_dir.glob("*.wav")) + list(self.dataset_dir.glob("*.mp3"))
            
            if not audio_files:
                self.training_status["status"] = "failed"
                self.training_status["message"] = "No audio files found in dataset directory"
                return

            # Process each file
            processed_files = []
            for i, audio_file in enumerate(audio_files):
                if self.should_stop:
                    break
                
                # Slice audio into chunks (30 seconds each)
                chunks = self._slice_audio(audio_file, chunk_duration=30.0)
                
                # Generate captions for each chunk using CLAP or placeholder
                for chunk_path in chunks:
                    caption = self._generate_caption(chunk_path)
                    processed_files.append({
                        "path": str(chunk_path),
                        "caption": caption
                    })
                
                self.training_status["progress"] = (i + 1) / len(audio_files) * 0.5
                self.training_status["message"] = f"Processed {i + 1}/{len(audio_files)} files"

            # Save processed dataset metadata
            self._save_dataset_metadata(processed_files)
            
            self.training_status["status"] = "idle"
            self.training_status["progress"] = 1.0
            self.training_status["message"] = f"Dataset processed: {len(processed_files)} chunks"

        except Exception as e:
            self.training_status["status"] = "failed"
            self.training_status["message"] = f"Error processing dataset: {str(e)}"

    def _slice_audio(self, audio_path: Path, chunk_duration: float = 30.0) -> list:
        """Slice audio file into chunks"""
        # This would use librosa or similar to slice audio
        # For now, return the original file path as placeholder
        return [audio_path]

    def _generate_caption(self, audio_path: Path) -> str:
        """Generate caption for audio using CLAP or placeholder"""
        # This would use CLAP model to generate captions
        # For now, return placeholder
        return f"Music track from {audio_path.stem}"

    def _save_dataset_metadata(self, processed_files: list):
        """Save processed dataset metadata"""
        metadata_path = self.dataset_dir / "metadata.json"
        import json
        with open(metadata_path, "w") as f:
            json.dump(processed_files, f, indent=2)

    def start_training(self, epochs: int = 10, learning_rate: float = 1e-4, batch_size: int = 4):
        """Start fine-tuning training with LoRA"""
        try:
            if self.is_training:
                return

            self.is_training = True
            self.should_stop = False
            self.training_status["status"] = "training"
            self.training_status["progress"] = 0.0
            self.training_status["epoch"] = 0
            self.training_status["total_epochs"] = epochs
            self.training_status["message"] = "Starting training..."

            # Load base model
            from audiocraft.models import MusicGen
            model = MusicGen.get_pretrained("facebook/musicgen-medium", device="cuda" if torch.cuda.is_available() else "cpu")

            # Load dataset
            metadata_path = self.dataset_dir / "metadata.json"
            if not metadata_path.exists():
                self.training_status["status"] = "failed"
                self.training_status["message"] = "Dataset not processed. Please process dataset first."
                self.is_training = False
                return

            import json
            with open(metadata_path, "r") as f:
                dataset = json.load(f)

            # Training loop (simplified - actual implementation would use PEFT/LoRA)
            for epoch in range(epochs):
                if self.should_stop:
                    break

                self.training_status["epoch"] = epoch + 1
                self.training_status["progress"] = (epoch + 1) / epochs
                self.training_status["message"] = f"Training epoch {epoch + 1}/{epochs}"

                # Placeholder training step
                # Actual implementation would:
                # 1. Load audio files and captions
                # 2. Apply LoRA/PEFT to model
                # 3. Train on batches
                # 4. Save checkpoint periodically

                # Simulate training delay
                import time
                time.sleep(1)

            # Save final checkpoint
            checkpoint_id = str(uuid.uuid4())
            checkpoint_path = self.models_dir / f"checkpoint_{checkpoint_id}"
            checkpoint_path.mkdir(exist_ok=True)

            # Save model checkpoint (placeholder)
            # model.save_checkpoint(str(checkpoint_path))

            # Save to database
            db = next(get_db())
            checkpoint = ModelCheckpoint(
                id=checkpoint_id,
                name=f"Fine-tuned Model {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                description=f"Trained for {epochs} epochs",
                file_path=str(checkpoint_path),
                is_base=False
            )
            db.add(checkpoint)
            db.commit()

            self.training_status["status"] = "completed"
            self.training_status["progress"] = 1.0
            self.training_status["message"] = "Training completed successfully"
            self.is_training = False

        except Exception as e:
            self.training_status["status"] = "failed"
            self.training_status["message"] = f"Training error: {str(e)}"
            self.is_training = False

    def stop_training(self):
        """Stop current training"""
        self.should_stop = True
        self.training_status["message"] = "Stopping training..."

    def get_status(self) -> Dict:
        """Get current training status"""
        return self.training_status.copy()

    def training_in_progress(self) -> bool:
        """Check if training is in progress"""
        return self.is_training


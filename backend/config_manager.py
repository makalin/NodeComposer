"""
Configuration management for NodeComposer
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
from pydantic import BaseModel

class GenerationConfig(BaseModel):
    """Generation configuration"""
    default_duration: float = 30.0
    default_guidance_scale: float = 3.0
    default_temperature: float = 1.0
    max_duration: float = 120.0
    min_duration: float = 10.0

class TrainingConfig(BaseModel):
    """Training configuration"""
    default_epochs: int = 10
    default_learning_rate: float = 1e-4
    default_batch_size: int = 4
    max_epochs: int = 100
    min_epochs: int = 1

class AudioConfig(BaseModel):
    """Audio processing configuration"""
    sample_rate: int = 32000
    default_format: str = "wav"
    export_formats: list = ["mp3", "flac", "wav"]
    default_bitrate: str = "320k"

class UIConfig(BaseModel):
    """UI configuration"""
    theme: str = "dark"
    auto_refresh_interval: int = 2000  # milliseconds
    max_queue_display: int = 50

class Config(BaseModel):
    """Main configuration"""
    generation: GenerationConfig = GenerationConfig()
    training: TrainingConfig = TrainingConfig()
    audio: AudioConfig = AudioConfig()
    ui: UIConfig = UIConfig()
    paths: Dict[str, str] = {
        "generations": "./generations",
        "models": "./models",
        "dataset": "./dataset",
        "exports": "./exports"
    }

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Config:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Config(**data)
            except Exception as e:
                print(f"Error loading config: {e}")
                return Config()
        return Config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config.dict(), f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split(".")
        value = self.config.dict()
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split(".")
        config_dict = self.config.dict()
        
        # Navigate to the nested dict
        current = config_dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        # Reconstruct config object
        self.config = Config(**config_dict)
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = Config()
        self.save_config()


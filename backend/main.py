"""
NodeComposer Backend API
FastAPI server for music generation and training
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from pathlib import Path

from database import init_db, get_db
from models import GenerationTask, ModelCheckpoint
from musicgen_service import MusicGenService
from training_service import TrainingService
from audio_processor import AudioProcessor
from stem_separator import StemSeparator
from audio_export import AudioExporter
from batch_generator import BatchGenerator
from prompt_templates import PromptTemplates
from audio_analyzer import AudioAnalyzer
from config_manager import ConfigManager

app = FastAPI(title="NodeComposer API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
musicgen_service = MusicGenService()
training_service = TrainingService()
audio_processor = AudioProcessor()
stem_separator = StemSeparator()
audio_exporter = AudioExporter()
batch_generator = BatchGenerator(musicgen_service)
prompt_templates = PromptTemplates()
audio_analyzer = AudioAnalyzer()
config_manager = ConfigManager()

# Initialize database
init_db()

# Directories
GENERATIONS_DIR = Path("generations")
GENERATIONS_DIR.mkdir(exist_ok=True)
DATASET_DIR = Path("dataset")
DATASET_DIR.mkdir(exist_ok=True)
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)


# Request Models
class GenerationRequest(BaseModel):
    prompt: str
    duration: float = 30.0
    model_id: Optional[str] = None
    guidance_scale: float = 3.0
    temperature: float = 1.0


class TrainingRequest(BaseModel):
    epochs: int = 10
    learning_rate: float = 1e-4
    batch_size: int = 4


# API Endpoints

@app.get("/")
async def root():
    return {"message": "NodeComposer API", "status": "running"}


@app.get("/api/health")
async def health():
    return {"status": "healthy", "gpu_available": musicgen_service.is_gpu_available()}


@app.post("/api/generate")
async def generate_music(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Queue a music generation task"""
    try:
        task = musicgen_service.queue_generation(
            prompt=request.prompt,
            duration=request.duration,
            model_id=request.model_id,
            guidance_scale=request.guidance_scale,
            temperature=request.temperature
        )
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
async def get_tasks():
    """Get all generation tasks"""
    db = next(get_db())
    tasks = db.query(GenerationTask).order_by(GenerationTask.created_at.desc()).all()
    return [{
        "id": task.id,
        "prompt": task.prompt,
        "status": task.status,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "file_path": task.file_path,
        "duration": task.duration
    } for task in tasks]


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "prompt": task.prompt,
        "status": task.status,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "file_path": task.file_path,
        "duration": task.duration
    }


@app.get("/api/tasks/{task_id}/audio")
async def get_task_audio(task_id: str):
    """Stream audio file for a task"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        task.file_path,
        media_type="audio/wav",
        filename=f"generation_{task_id}.wav"
    )


@app.post("/api/generate/audio")
async def generate_from_audio(
    prompt: str,
    duration: float = 30.0,
    audio_file: UploadFile = File(...),
    model_id: Optional[str] = None
):
    """Generate music from text prompt and audio conditioning"""
    try:
        # Save uploaded audio temporarily
        temp_path = Path(f"temp_{audio_file.filename}")
        with open(temp_path, "wb") as f:
            f.write(await audio_file.read())
        
        task = musicgen_service.queue_generation(
            prompt=prompt,
            duration=duration,
            model_id=model_id,
            audio_conditioning=temp_path
        )
        
        # Clean up temp file after processing
        if temp_path.exists():
            temp_path.unlink()
        
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_models():
    """Get all available model checkpoints"""
    db = next(get_db())
    models = db.query(ModelCheckpoint).order_by(ModelCheckpoint.created_at.desc()).all()
    return [{
        "id": model.id,
        "name": model.name,
        "description": model.description,
        "created_at": model.created_at.isoformat(),
        "file_path": model.file_path,
        "is_base": model.is_base
    } for model in models]


@app.post("/api/train/process-dataset")
async def process_dataset(background_tasks: BackgroundTasks):
    """Process dataset: slice audio and generate captions"""
    try:
        background_tasks.add_task(training_service.process_dataset)
        return {"status": "processing", "message": "Dataset processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/train/status")
async def get_training_status():
    """Get current training status"""
    return training_service.get_status()


@app.post("/api/train/start")
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Start fine-tuning training"""
    try:
        if training_service.training_in_progress():
            raise HTTPException(status_code=400, detail="Training already in progress")
        
        background_tasks.add_task(
            training_service.start_training,
            epochs=request.epochs,
            learning_rate=request.learning_rate,
            batch_size=request.batch_size
        )
        return {"status": "started", "message": "Training started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/train/stop")
async def stop_training():
    """Stop current training"""
    try:
        training_service.stop_training()
        return {"status": "stopped", "message": "Training stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a generation task and its audio file"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.file_path and os.path.exists(task.file_path):
        os.remove(task.file_path)
    
    db.delete(task)
    db.commit()
    return {"status": "deleted"}


# New Tools Endpoints

@app.post("/api/tasks/{task_id}/separate")
async def separate_stems(task_id: str, stems: Optional[List[str]] = None):
    """Separate audio into stems (drums, bass, vocals, etc.)"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Task or audio file not found")
    
    try:
        if stems is None:
            stems = ["drums", "bass", "vocals", "other"]
        
        stem_files = stem_separator.separate(Path(task.file_path), stems=stems)
        return {"status": "completed", "stems": stem_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/{task_id}/export")
async def export_audio(
    task_id: str,
    format: str = "mp3",
    bitrate: str = "320k"
):
    """Export audio in different format"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Task or audio file not found")
    
    try:
        output_path = audio_exporter.convert(
            Path(task.file_path),
            format=format,
            bitrate=bitrate
        )
        return {
            "status": "completed",
            "file_path": str(output_path),
            "format": format
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/generate")
async def batch_generate(request: dict):
    """Generate multiple tracks from prompts"""
    prompts = request.get("prompts", [])
    duration = request.get("duration", 30.0)
    model_id = request.get("model_id")
    
    if not prompts:
        raise HTTPException(status_code=400, detail="No prompts provided")
    
    try:
        task_ids = batch_generator.generate_batch(
            prompts=prompts,
            duration=duration,
            model_id=model_id
        )
        return {"status": "queued", "task_ids": task_ids, "count": len(task_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/variations")
async def generate_variations(request: dict):
    """Generate variations of a prompt"""
    prompt = request.get("prompt")
    num_variations = request.get("num_variations", 5)
    duration = request.get("duration", 30.0)
    model_id = request.get("model_id")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt provided")
    
    try:
        task_ids = batch_generator.generate_variations(
            base_prompt=prompt,
            num_variations=num_variations,
            duration=duration,
            model_id=model_id
        )
        return {"status": "queued", "task_ids": task_ids, "count": len(task_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prompts/templates")
async def get_templates(category: Optional[str] = None):
    """Get prompt templates"""
    if category:
        templates = prompt_templates.get_category(category)
        return {category: templates}
    else:
        return {
            cat: prompt_templates.get_category(cat)
            for cat in prompt_templates.list_categories()
        }


@app.get("/api/prompts/templates/{category}/{name}")
async def get_template(category: str, name: str):
    """Get a specific template"""
    template = prompt_templates.get_template(category, name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"category": category, "name": name, "prompt": template}


@app.post("/api/prompts/templates")
async def create_template(request: dict):
    """Create a new template"""
    category = request.get("category")
    name = request.get("name")
    prompt = request.get("prompt")
    
    if not all([category, name, prompt]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    prompt_templates.add_template(category, name, prompt)
    return {"status": "created", "category": category, "name": name}


@app.get("/api/prompts/search")
async def search_templates(query: str):
    """Search templates"""
    results = prompt_templates.search_templates(query)
    return results


@app.get("/api/tasks/{task_id}/analyze")
async def analyze_audio(task_id: str):
    """Analyze audio file"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Task or audio file not found")
    
    try:
        analysis = audio_analyzer.analyze(Path(task.file_path))
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}/waveform")
async def get_waveform(task_id: str):
    """Get waveform data for visualization"""
    db = next(get_db())
    task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Task or audio file not found")
    
    try:
        waveform_data = audio_analyzer.get_waveform_data(Path(task.file_path))
        return waveform_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    return config_manager.config.dict()


@app.post("/api/config")
async def update_config(updates: dict):
    """Update configuration"""
    try:
        config_manager.update(updates)
        return {"status": "updated", "config": config_manager.config.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


# 🎵 NodeComposer - Additional Tools & Features

This document outlines all the additional tools and functions added to NodeComposer.

## 🆕 New Backend Tools

### 1. Stem Separation (`stem_separator.py`)
- **Purpose**: Separate audio tracks into individual stems (drums, bass, vocals, other)
- **Methods**: Supports both Demucs and Spleeter
- **Features**:
  - Extract drums, bass, vocals, and other instruments
  - Convert stems to WAV format
  - Configurable stem selection
- **API Endpoint**: `POST /api/tasks/{task_id}/separate`

### 2. Audio Export (`audio_export.py`)
- **Purpose**: Convert and export audio files in multiple formats
- **Supported Formats**: MP3, FLAC, WAV, OGG, M4A, AAC
- **Features**:
  - Format conversion with quality control
  - Batch export to multiple formats
  - Audio trimming and editing
  - Metadata extraction
  - Duration calculation
- **API Endpoint**: `POST /api/tasks/{task_id}/export`

### 3. Batch Generation (`batch_generator.py`)
- **Purpose**: Generate multiple tracks efficiently
- **Features**:
  - Generate from multiple prompts
  - Generate variations of a single prompt
  - Generate themed playlists
  - Load prompts from text files
  - Configurable concurrent generation
- **API Endpoints**:
  - `POST /api/batch/generate` - Multiple prompts
  - `POST /api/batch/variations` - Prompt variations

### 4. Prompt Templates (`prompt_templates.py`)
- **Purpose**: Manage and organize prompt templates
- **Features**:
  - Pre-built templates for genres, moods, instruments, styles
  - Custom template creation
  - Template search functionality
  - Template categories
  - Template combination
- **API Endpoints**:
  - `GET /api/prompts/templates` - List all templates
  - `GET /api/prompts/templates/{category}/{name}` - Get specific template
  - `POST /api/prompts/templates` - Create new template
  - `GET /api/prompts/search` - Search templates

### 5. Audio Analysis (`audio_analyzer.py`)
- **Purpose**: Analyze generated audio files
- **Features**:
  - Tempo estimation (BPM)
  - Key detection
  - Energy calculation
  - Danceability score
  - Spectral analysis
  - Rhythm analysis
  - Harmonic/percussive separation
  - Waveform data for visualization
  - Spectrogram data
- **API Endpoints**:
  - `GET /api/tasks/{task_id}/analyze` - Full analysis
  - `GET /api/tasks/{task_id}/waveform` - Waveform data

### 6. Configuration Management (`config_manager.py`)
- **Purpose**: Manage application configuration
- **Features**:
  - Generation settings
  - Training parameters
  - Audio processing options
  - UI preferences
  - Path configuration
  - JSON-based storage
- **API Endpoints**:
  - `GET /api/config` - Get configuration
  - `POST /api/config` - Update configuration

## 🎨 New Frontend Components

### 1. PromptTemplates Component
- Browse and search prompt templates
- Create custom templates
- Select templates to use in generation
- Organized by categories (genres, moods, instruments, styles)

### 2. BatchGenerator Component
- Generate multiple tracks from multiple prompts
- Generate variations of a single prompt
- Adjustable duration and parameters
- Real-time progress tracking

### 3. AudioTools Component
- Export audio in different formats (MP3, FLAC, WAV, OGG)
- Stem separation interface
- Audio analysis visualization
- Quick access from task cards

## 📊 Feature Summary

| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Stem Separation | ✅ | ✅ | Complete |
| Audio Export | ✅ | ✅ | Complete |
| Batch Generation | ✅ | ✅ | Complete |
| Prompt Templates | ✅ | ✅ | Complete |
| Audio Analysis | ✅ | ✅ | Complete |
| Configuration Management | ✅ | ⚠️ | Backend only |
| Waveform Visualization | ✅ | ⚠️ | Backend ready |

## 🚀 Usage Examples

### Stem Separation
```python
from stem_separator import StemSeparator

separator = StemSeparator(method="demucs")
stems = separator.separate(audio_path, stems=["drums", "bass", "vocals"])
```

### Audio Export
```python
from audio_export import AudioExporter

exporter = AudioExporter()
mp3_path = exporter.convert(audio_path, format="mp3", bitrate="320k")
```

### Batch Generation
```python
from batch_generator import BatchGenerator

generator = BatchGenerator(musicgen_service)
task_ids = generator.generate_batch(
    prompts=["Prompt 1", "Prompt 2", "Prompt 3"],
    duration=30.0
)
```

### Prompt Templates
```python
from prompt_templates import PromptTemplates

templates = PromptTemplates()
prompt = templates.combine_templates(
    genre="synthwave",
    mood="energetic",
    instrument="synthesizer"
)
```

### Audio Analysis
```python
from audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer()
analysis = analyzer.analyze(audio_path)
print(f"Tempo: {analysis['tempo']} BPM")
print(f"Key: {analysis['key']}")
```

## 📦 Dependencies Added

- `demucs>=4.0.0` - For stem separation
- `spleeter>=2.3.0` - Alternative stem separation method
- Additional librosa features for advanced analysis

## 🔧 Configuration

All new tools are integrated into the main API and can be configured via:
- Environment variables
- Configuration file (`config.json`)
- API endpoints

## 🎯 Next Steps

Potential future enhancements:
- MIDI export functionality
- Real-time waveform visualization in frontend
- Advanced audio effects processing
- Cloud storage integration for exports
- Template marketplace/sharing


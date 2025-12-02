# 🎵 NodeComposer

> **A local, privacy-focused AI music generator capable of learning your unique sonic signature.**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Status](https://img.shields.io/badge/status-active-success.svg) ![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg) ![Node](https://img.shields.io/badge/Node-v18+-green.svg)

## 📖 Overview

**NodeComposer** is a self-hosted alternative to services like Suno or Udio. Unlike cloud based generators, NodeComposer runs entirely on your local machine. It allows you to generate high-fidelity music from text prompts and, most importantly, **fine-tune the model on your own music library** to create a generator that understands your specific style.

### ✨ Key Features

* **100% Local & Private:** No credits, no subscriptions, no data leaving your machine.
* **Custom Model Training:** Fine-tune the underlying MusicGen model on your own `.wav` files to mimic your genre or instrumentals.
* **Suno-like Interface:** A modern, dark-mode web UI built with Next.js for managing generation queues and playback.
* **Text-to-Music & Audio-to-Audio:** Generate from scratch or upload a melody whistle to guide the AI.
* **Stem Export:** (Experimental) Auto-separate generated tracks into drums, bass, and melody.

---

## 🏗️ The Tech Stack

NodeComposer uses a hybrid architecture to combine the best AI tools with the best web frameworks.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **AI Model** | **AudioCraft (MusicGen)** | The core transformer model by Meta Research. |
| **Fine-Tuning** | **LoRA / PEFT** | Efficient training technique to learn your music without retraining the whole model. |
| **Backend API** | **FastAPI (Python)** | Exposes the model inference and training status to the UI. |
| **Frontend** | **Next.js (Node.js)** | A reactive UI for prompting, playback, and library management. |
| **Styling** | **Tailwind CSS** | For that sleek, professional audio-app aesthetic. |
| **Database** | **SQLite** | Zero-config local database to store your prompts and generation history. |

---

## ⚡ Prerequisites

* **OS:** Linux (Ubuntu 22.04 recommended) or Windows 11 (WSL2).
* **GPU:** NVIDIA GPU with at least **12GB VRAM** (RTX 3060 or higher). *24GB recommended for training.*
* **Software:**
    * Python 3.10+
    * Node.js 18+
    * CUDA Toolkit 11.8+
    * FFmpeg

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/makalin/NodeComposer.git](https://github.com/makalin/NodeComposer.git)
cd NodeComposer
````

### 2\. Backend Setup (Python)

This handles the music generation and training logic.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install PyTorch with CUDA support (Adjust for your CUDA version)
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)

# Install dependencies including AudioCraft
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

### 3\. Frontend Setup (Node.js)

This handles the UI and player.

```bash
# In a new terminal window
cd frontend
npm install

# Start the UI
npm run dev
```

Visit `http://localhost:3000` to open NodeComposer.

-----

## 🎧 Usage Guide

### Generating Music

1.  Navigate to the **Compose** tab.
2.  Enter a prompt: *"A cyber-noir synthwave track with heavy bass and slow tempo."*
3.  Set duration (e.g., 30s) and click **Generate**.
4.  The task is queued locally; progress is shown in the sidebar.

### Training on Your Data (Fine-Tuning)

1.  Place your source audio files (WAV/MP3) in the `dataset/` folder.
2.  Navigate to the **Train** tab.
3.  Click **Process Dataset**. This will slice your audio and auto-caption it (using CLAP).
4.  Click **Start Training**.
      * *Note: Training takes 2-6 hours depending on your GPU and dataset size.*
5.  Once finished, select your new "Node" (Model Checkpoint) in the Compose tab to generate music in your style.

-----

## 🗺️ Roadmap

  - [ ] **In-Painting:** Re-generate specific bad sections of a track.
  - [ ] **Lyrics Integration:** Integration with TTS models for vocal generation.
  - [ ] **MIDI Export:** Convert generated audio to MIDI for use in DAWs (via Spotify Basic Pitch).

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

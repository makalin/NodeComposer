# NodeComposer Backend

FastAPI backend for NodeComposer music generation.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install PyTorch with CUDA (adjust URL for your CUDA version):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.


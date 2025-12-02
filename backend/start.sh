#!/bin/bash
# Backend startup script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p generations
mkdir -p models
mkdir -p dataset

# Start the API server
uvicorn main:app --reload --port 8000 --host 0.0.0.0


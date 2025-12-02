@echo off
REM Backend startup script for Windows

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Create necessary directories
if not exist generations mkdir generations
if not exist models mkdir models
if not exist dataset mkdir dataset

REM Start the API server
uvicorn main:app --reload --port 8000 --host 0.0.0.0


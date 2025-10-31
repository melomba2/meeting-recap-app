#!/usr/bin/env python3
"""
Local REST API server for Meeting Recap App.
Exposes workflow functions as HTTP endpoints.
"""

import sys
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add src-python to the path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT / "src-python"))

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from src_python.whisper_processor import WhisperProcessor
from src_python.transcript_analyzer import OllamaTranscriptAnalyzer
from src_python.recap_generator import DNDRecapGenerator

API_KEY = "your_api_key"  # Replace with a secure, generated API key
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

app = FastAPI(title="Meeting Recap API", dependencies=[Depends(get_api_key)])

# In-memory job storage
jobs: Dict[str, dict] = {}


# Request/Response Models
class TranscribeRequest(BaseModel):
    file_path: str
    model: str = "medium"
    output_dir: Optional[str] = None


class AnalyzeRequest(BaseModel):
    transcript_path: str
    model: str = "gemma3n:latest"
    ollama_url: str = "http://192.168.68.10:11434"
    output_dir: Optional[str] = None


class RecapRequest(BaseModel):
    analysis_path: str
    style: str = "epic"
    ollama_url: str = "http://192.168.68.10:11434"
    output_dir: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    stage: Optional[str] = None
    error: Optional[str] = None
    result: Optional[dict] = None


@app.get("/")
async def root():
    """Root endpoint to test if the server is running."""
    return {"message": "Meeting Recap API server is running!"}


# Background task processing functions
def process_transcribe_job(job_id: str, request: TranscribeRequest):
    """Background task for transcription."""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "transcription"
        jobs[job_id]["progress"] = 0

        # Initialize processor
        processor = WhisperProcessor(model_name=request.model)

        # Process the file
        input_path = Path(request.file_path)
        output_dir = Path(request.output_dir) if request.output_dir else input_path.parent

        jobs[job_id]["progress"] = 25
        result = processor.process_file(str(input_path), str(output_dir))

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "transcript_path": result.get("transcript_path"),
            "duration": result.get("duration"),
            "model": request.model
        }
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


def process_analyze_job(job_id: str, request: AnalyzeRequest):
    """Background task for transcript analysis."""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "analysis"
        jobs[job_id]["progress"] = 0

        # Initialize analyzer
        analyzer = OllamaTranscriptAnalyzer(
            model=request.model,
            base_url=request.ollama_url
        )

        # Read transcript
        transcript_path = Path(request.transcript_path)
        with open(transcript_path, 'r') as f:
            transcript_text = f.read()

        jobs[job_id]["progress"] = 25

        # Analyze
        output_dir = Path(request.output_dir) if request.output_dir else transcript_path.parent
        analysis = analyzer.analyze_transcript(transcript_text, str(output_dir))

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "analysis_path": analysis.get("output_path"),
            "model": request.model
        }
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


def process_recap_job(job_id: str, request: RecapRequest):
    """Background task for recap generation."""
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["stage"] = "recap_generation"
        jobs[job_id]["progress"] = 0

        # Initialize generator
        generator = DNDRecapGenerator(
            style=request.style,
            ollama_url=request.ollama_url
        )

        # Read analysis
        analysis_path = Path(request.analysis_path)
        with open(analysis_path, 'r') as f:
            analysis_text = f.read()

        jobs[job_id]["progress"] = 25

        # Generate recap
        output_dir = Path(request.output_dir) if request.output_dir else analysis_path.parent
        recap = generator.generate_recap(analysis_text, str(output_dir))

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "recap_path": recap.get("output_path"),
            "style": request.style
        }
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


# API Endpoints
@app.post("/api/transcribe", response_model=JobResponse)
async def transcribe(request: TranscribeRequest, background_tasks: BackgroundTasks):
    """Start a transcription job."""
    # Validate file exists
    if not Path(request.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "type": "transcribe"
    }

    # Start background task
    background_tasks.add_task(process_transcribe_job, job_id, request)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Transcription job queued"
    )


@app.post("/api/analyze", response_model=JobResponse)
async def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Start a transcript analysis job."""
    # Validate file exists
    if not Path(request.transcript_path).exists():
        raise HTTPException(status_code=404, detail="Transcript file not found")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "type": "analyze"
    }

    # Start background task
    background_tasks.add_task(process_analyze_job, job_id, request)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Analysis job queued"
    )


@app.post("/api/recap", response_model=JobResponse)
async def recap(request: RecapRequest, background_tasks: BackgroundTasks):
    """Start a recap generation job."""
    # Validate file exists
    if not Path(request.analysis_path).exists():
        raise HTTPException(status_code=404, detail="Analysis file not found")

    # Create job
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "type": "recap"
    }

    # Start background task
    background_tasks.add_task(process_recap_job, job_id, request)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Recap generation job queued"
    )


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job.get("status"),
        progress=job.get("progress"),
        stage=job.get("stage"),
        error=job.get("error"),
        result=job.get("result")
    )


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "type": job.get("type"),
                "created_at": job.get("created_at")
            }
            for job_id, job in jobs.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)


from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
from datetime import datetime
from pathlib import Path

from ..app import PeriodTracker
from ..config.settings import config
from ..utils.audio_recorder import record_audio_until_x

app = FastAPI(title="Period Tracker API", version="1.0.0")

# Initialize period tracker
period_tracker = PeriodTracker()

# Create directories if they don't exist
os.makedirs(config.audio_input_dir, exist_ok=True)
os.makedirs(config.audio_output_dir, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Period Tracker API is running"}

@app.post("/session/start")
async def start_session():
    """Start a new session"""
    try:
        response = period_tracker.start_new_session()
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/end/{session_id}")
async def end_session(session_id: str):
    """End an existing session"""
    try:
        response = period_tracker.end_current_session()
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/record-voice")
async def record_voice_note(session_id: Optional[str] = None):
    """Record a new voice note and process it"""
    try:
        # Generate a unique filename
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(config.audio_input_dir, audio_filename)
        
        # Record audio
        record_audio_until_x(audio_path)
        
        # Process the voice note
        response = period_tracker.process_voice_note(audio_path, session_id)
        
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-voice/{audio_path}")
async def process_voice_note(audio_path: str, session_id: Optional[str] = None):
    """Process an existing voice note"""
    try:
        # Validate the path
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
            
        # Process the voice note
        response = period_tracker.process_voice_note(audio_path, session_id)
        
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



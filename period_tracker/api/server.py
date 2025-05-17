from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, Dict, Any
import os
import uuid
from pathlib import Path
import uvicorn

from period_tracker.app import PeriodTracker
from period_tracker.config.settings import config
from period_tracker.utils.text_processor import extract_period_info
from period_tracker.elevenlabs_transcriber import ElevenLabsTranscriber

# Create router
router = APIRouter(prefix="/period-tracker")

# Initialize period tracker
period_tracker = PeriodTracker()
# Initialize transcriber
transcriber = ElevenLabsTranscriber()

# Create directories if they don't exist
os.makedirs(config.audio_input_dir, exist_ok=True)
os.makedirs(config.audio_output_dir, exist_ok=True)

session_id = None

def get_required_fields() -> Dict[str, list]:
    """Get the required fields for period tracking"""
    return {
        "period": ["status", "flow"],
        "timing": ["date"]
    }

def check_missing_fields(period_info: Dict[str, Any]) -> Dict[str, list]:
    """Check which required fields are missing from the period info"""
    required = get_required_fields()
    missing = {}
    
    for category, fields in required.items():
        missing_fields = []
        for field in fields:
            if category not in period_info or field not in period_info[category]:
                missing_fields.append(field)
        if missing_fields:
            missing[category] = missing_fields
    
    return missing

def generate_followup_question(missing_fields: Dict[str, list]) -> str:
    """Generate a follow-up question based on missing fields"""
    questions = []
    
    if "period" in missing_fields:
        if "status" in missing_fields["period"]:
            questions.append("Could you tell me if you're starting or ending your period?")
        if "flow" in missing_fields["period"]:
            questions.append("How would you describe your flow? (light, medium, or heavy)")
    
    if "timing" in missing_fields and "date" in missing_fields["timing"]:
        questions.append("When did this happen? (e.g., today, yesterday, 2 days ago)")
    
    if not questions:
        return "Is there anything else you'd like to share about your period?"
    
    return " ".join(questions)

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Period Tracker API is running"}

# @router.post("/process-audio")
def process_audio(
    file: str
):
    """Process an audio file containing voice input"""
    global session_id
    try:
        # Transcribe audio
        transcribed_text = transcriber.transcribe_audio(file)
        
        # Extract period information
        period_info = extract_period_info(transcribed_text)
        
        # Check for missing required fields
        missing_fields = check_missing_fields(period_info)
        
        if not missing_fields:
            # All required fields present, store the data
            if session_id:
                # Store in session if session exists
                period_tracker.data_store.add_log_to_session(session_id, period_info)
                
                # End the session
                session_data = period_tracker.end_current_session()
                
                # Generate response
                response_text = "Thank you for sharing your information. I've recorded your period details. Check back in soon!"
                response_audio = transcriber.text_to_speech(
                    response_text,
                    os.path.join(config.audio_output_dir, f"response_{uuid.uuid4()}.mp3")
                )
                session_id = None
                return {
                    "status": "complete",
                    "message": response_text,
                    "audio_url": f"/api/period-tracker/audio/{os.path.basename(response_audio)}",
                    "period_info": period_info,
                    "session_data": session_data
                }
            else:
                # No session, just return the period info
                return {
                    "status": "complete_no_session",
                    "period_info": period_info
                }
        else:
            # Missing fields, generate follow-up question
            followup_question = generate_followup_question(missing_fields)
            
            outpath = os.path.join(config.audio_output_dir, f"response_{uuid.uuid4()}.mp3")
            # Convert question to speech
            response_audio = transcriber.text_to_speech(
                followup_question,
                outpath
            )
            
            return {
                "status": "needs_more_info",
                "message": followup_question,
                "audio_url": outpath,
                "missing_fields": missing_fields,
                "session_id": session_id or "",
                "conversation_history": period_tracker.conversation_handler.conversation_history
            }
            
    except Exception as e:
        raise e

# if __name__ == "__main__":
#     uvicorn.run(router, host="0.0.0.0", port=8000)
    
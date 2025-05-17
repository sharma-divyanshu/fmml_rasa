from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
import os
from pathlib import Path

class PeriodFlow(str, Enum):
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"

class Mood(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    STRESSED = "stressed"
    TIRED = "tired"
    ENERGETIC = "energetic"
    CRAMPS = "cramps"
    BLOATED = "bloated"
    OTHER = "other"

class PeriodLog(BaseModel):
    user_id: str
    date: str
    flow: PeriodFlow = Field(..., description="Menstrual flow intensity")
    mood: List[Mood] = Field(default_factory=list, description="List of moods/feelings")
    spotting: bool = Field(False, description="Whether there's any spotting")
    notes: Optional[str] = Field(None, description="Additional notes or symptoms")
    symptoms: List[str] = Field(default_factory=list, description="List of symptoms")
    voice_note_path: Optional[str] = Field(None, description="Path to the voice recording")
    transcribed_text: Optional[str] = Field(None, description="Transcribed text from voice note")

class AppConfig(BaseModel):
    # Database configuration
    database_url: str = "sqlite:///period_tracker.db"
    
    # Voice settings
    voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)
    model_id: str = "eleven_monolingual_v1"
    audio_output_dir: str = "data/audio"
    
    # Text processing
    keywords: Dict[str, List[str]] = {
        "flow_light": ["light flow", "light period", "light bleeding"],
        "flow_medium": ["medium flow", "normal flow", "regular flow"],
        "flow_heavy": ["heavy flow", "heavy period", "heavy bleeding"],
        "spotting": ["spotting", "light spotting", "brown discharge"],
        "mood_happy": ["happy", "good", "great", "amazing", "wonderful"],
        "mood_sad": ["sad", "down", "depressed", "unhappy"],
        "mood_anxious": ["anxious", "nervous", "worried", "stressed"],
        "mood_cramps": ["cramps", "cramping", "pain", "ache"],
        "mood_bloated": ["bloated", "bloating", "swollen"],
    }
    
    class Config:
        env_file = ".env"
        env_prefix = "PERIOD_TRACKER_"

# Create data directories
os.makedirs(os.path.join(os.path.dirname(__file__), "../../data/audio"), exist_ok=True)

# Load configuration
config = AppConfig()

import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import tempfile
import subprocess

from dotenv import load_dotenv
from ..elevenlabs_transcriber import ElevenLabsTranscriber
from .text_processor import extract_period_info, format_period_summary
from .data_store import PeriodDataStore

load_dotenv()

class VoiceConversationHandler:
    def __init__(self, audio_output_dir: str = "audio_output"):
        """Initialize the voice conversation handler"""
        self.audio_output_dir = Path(audio_output_dir)
        self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        self.current_question = 0
        self.max_questions = 5
        self.conversation_history = []
        self.required_fields = {
            "period": ["status", "flow"],
            "timing": ["date"]
        }
        
        # Initialize data store
        self.data_store = PeriodDataStore()
        self.session_id = None
        
        # Create a new session
        self.session_id = self.data_store.create_session()

    def _convert_text_to_speech(self, text: str) -> str:
        """Convert text to speech and save as MP3"""
        audio_path = self.audio_output_dir / f"question_{self.current_question}.mp3"
        ElevenLabsTranscriber().text_to_speech(text, str(audio_path))
        return str(audio_path)

    def _play_audio(self, audio_path: str) -> None:
        """Play audio file using system player"""
        try:
            # Use appropriate command based on OS
            if os.name == 'nt':  # Windows
                subprocess.run(['start', '', audio_path], shell=True)
            elif os.name == 'posix':  # Unix/Linux
                subprocess.run(['xdg-open', audio_path])
            else:
                raise ValueError(f"Unsupported OS: {os.name}")
        except Exception as e:
            print(f"Error playing audio: {str(e)}")

    def _check_required_fields(self, data: Dict) -> List[str]:
        """Check if all required fields are present in the data"""
        missing_fields = []
        
        # Check period information
        period_data = data.get("period", {})
        if not any(period_data.get(field) for field in self.required_fields["period"]):
            missing_fields.append("period")
            
        # Check timing
        timing_data = data.get("timing", {})
        if not any(timing_data.get(field) for field in self.required_fields["timing"]):
            missing_fields.append("date")
            
        # Check for unusual symptoms
        if "symptoms" in data:
            unusual_symptoms = [
                "severe", "extreme", "unusual", "abnormal", 
                "heavy bleeding", "intense pain", "fainting", 
                "dizziness", "fever", "vomiting"
            ]
            
            for symptom in data["symptoms"]:
                if any(us in symptom.get("type", "").lower() for us in unusual_symptoms):
                    data["unusual_symptoms"] = True
                    break
            
        return missing_fields

    def _generate_followup_question(self, missing_fields: List[str], current_data: Dict) -> str:
        """Generate a follow-up question based on missing fields"""
        if not missing_fields:
            return ""
            
        if "period" in missing_fields:
            if "flow" in missing_fields:
                return "Could you tell me about the flow intensity of your period? (light, medium, heavy)"
            else:
                return "Could you confirm if you started or ended your period?"
        
        if "date" in missing_fields:
            return "Could you tell me the date or when this happened?"
            
        return "Is there anything else you'd like to add about your symptoms or mood?"

    def process_conversation(self, initial_text: str) -> Dict:
        """Process a conversation with follow-up questions until all required information is gathered"""
        # Start with initial text
        self.conversation_history.append({"role": "user", "content": initial_text})
        
        # Extract initial information
        result = extract_period_info(initial_text)
        
        # Check for unusual symptoms
        self._check_required_fields(result)  # This will set unusual_symptoms flag if needed
        
        # Check for missing fields
        missing_fields = self._check_required_fields(result)
        
        while missing_fields and self.current_question < self.max_questions:
            # Generate follow-up question
            question = self._generate_followup_question(missing_fields, result)
            
            # Convert question to speech
            audio_path = self._convert_text_to_speech(question)
            
            # Play the question
            self._play_audio(audio_path)
            
            # Add question to conversation history
            self.conversation_history.append({"role": "assistant", "content": question})
            
            # Get user response (this would be replaced with actual voice input in production)
            user_response = input("\nUser (type your response): ")
            
            # Process response
            self.conversation_history.append({"role": "user", "content": user_response})
            
            # Update result with new information
            new_info = extract_period_info(user_response)
            
            # Check for unusual symptoms in new info
            self._check_required_fields(new_info)  # This will set unusual_symptoms flag if needed
            
            result.update(new_info)
            
            # Check again for missing fields
            missing_fields = self._check_required_fields(result)
            self.current_question += 1
            
        # Store the conversation in data store
        if self.session_id:
            self.data_store.add_log_to_history(result)
            
        return result

    def end_conversation(self):
        """End the current conversation and store final data"""
        if self.session_id:
            self.data_store.end_session(self.session_id)
            self.session_id = None
            self.current_question = 0
            self.conversation_history = []

import os
import uuid
from datetime import datetime
from typing import Dict, Any

from period_tracker.elevenlabs_transcriber import ElevenLabsTranscriber
from period_tracker.config.settings import config
from period_tracker.utils.audio_recorder import record_audio_until_x
from period_tracker.utils.text_processor import extract_period_info, format_period_summary
from period_tracker.utils.voice_conversation_handler import VoiceConversationHandler
from period_tracker.utils.data_store import PeriodDataStore
from elevenlabs import play

class PeriodTracker:
    def __init__(self):
        """Initialize the period tracker with session management"""
        # Initialize data store
        self.data_store = PeriodDataStore()
        # Initialize conversation handler
        self.conversation_handler = VoiceConversationHandler()
        # Initialize current session
        self.current_session_id = None
        
    def start_new_session(self) -> Dict:
        """Start a new session for a new interaction"""
        self.current_session_id = self.data_store.create_session()
        return {
            "session_id": self.current_session_id,
            "status": "active",
            "start_time": self.data_store.get_session_data(self.current_session_id)["start_time"]
        }
        
    def end_current_session(self) -> Dict:
        """End the current session and return session data"""
        if not self.current_session_id:
            return {"error": "No active session"}
            
        # End the session
        self.data_store.end_session(self.current_session_id)
        
        # Get session data
        session_data = self.data_store.get_session_data(self.current_session_id)
        
        # Clear current session
        self.current_session_id = None
        
        return {
            "session_id": self.current_session_id,
            "status": "completed",
            "end_time": session_data["end_time"],
            "has_missing_data": session_data["has_missing_data"],
            "has_unusual_symptoms": session_data["has_unusual_symptoms"]
        }

    def generate_voice_response(self, text: str) -> Dict[str, Any]:
        """
        Generate a voice response using ElevenLabs API.
        
        Args:
            text: The text to convert to speech.
            
        Returns:
            Dict containing the generated audio file path and metadata.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response doesn't contain the expected data.
        """
        try:
            output_file_name = uuid.uuid4().hex + ".mp3"
            outpath = os.path.join(config.audio_output_dir, output_file_name)
            audio_gen = ElevenLabsTranscriber().text_to_speech(
                text=text,
                outpath=outpath
            )
            return {
                "audio_file_path": outpath,
                "text": text,
                "audio": audio_gen
            }
        except Exception as e:
            return {"error": f"Failed to generate voice response: {str(e)}"}
    
    def process_voice_note(self, audio_file_path: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a voice note using conversation flow to gather complete health information
        
        Args:
            audio_file_path: Path to the audio file
            session_id: Optional session ID to use for this interaction
            
        Returns:
            Dict containing the extracted information and metadata
        """
        # Check if we have an active session
        if not session_id and not self.current_session_id:
            return {"error": "No active session. Please start a new session first."}
            
        # Use provided session ID or current session
        if session_id:
            self.current_session_id = session_id
            
        # Transcribe the audio
        try:
            transcribed_text = ElevenLabsTranscriber().transcribe_audio(audio_file_path)
        except Exception as e:
            return {"error": f"Failed to transcribe audio: {str(e)}"}
        
        # Process conversation to gather complete information
        try:
            complete_info = self.conversation_handler.process_conversation(transcribed_text)
        except Exception as e:
            return {"error": f"Failed to process conversation: {str(e)}"}
        
        # Save to database
        log_id = str(uuid.uuid4())
        audio_filename = f"{log_id}.wav"
        audio_path = os.path.join(config.audio_output_dir, audio_filename)
        
        # Move the audio file to the designated directory
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        os.rename(audio_file_path, audio_path)
        
        # Add log to session history
        self.data_store.add_log_to_history(complete_info)
        
        # Get session data
        session_data = self.data_store.get_session_data(self.current_session_id)
        
        return {
            "log_id": log_id,
            "session_id": self.current_session_id,
            "transcribed_text": transcribed_text,
            "complete_info": complete_info,
            "summary": format_period_summary(complete_info),
            "conversation_history": self.conversation_handler.conversation_history,
            "session_status": session_data["status"],
            "has_missing_data": session_data["has_missing_data"],
            "has_unusual_symptoms": session_data["has_unusual_symptoms"]
        }
        
        return {
            "log_id": log_id,
            "transcribed_text": transcribed_text,
            "period_info": period_info,
            "summary": format_period_summary(period_info)
        }
    
    def get_recent_logs(self, limit: int = 5) -> list:
        """Get recent period logs for the user"""
        logs = self.db.query(PeriodLog)\
            .filter(PeriodLog.user_id == self.user_id)\
            .order_by(PeriodLog.date.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "date": log.date.isoformat(),
                "flow": log.flow,
                "spotting": log.spotting,
                "mood": log.mood,
                "symptoms": log.symptoms,
                "notes": log.notes,
                "summary": format_period_summary({
                    "flow": log.flow,
                    "spotting": log.spotting,
                    "mood": log.mood,
                    "symptoms": log.symptoms,
                    "notes": log.notes
                })
            }
            for log in logs
        ]
    

def record_voice_note() -> str:
    """
    Record a voice note using the system's default microphone.
    Returns the path to the recorded audio file.
    """
    print("Recording... (Press 'x' to stop early)")
    audio_file_path = record_audio_until_x(uuid.uuid4().hex + ".wav")
    return audio_file_path

def main():
    """Main entry point for the period tracker CLI"""
    print("Welcome to Period Tracker with Voice Notes!")
    print("----------------------------------------")
    
    tracker = PeriodTracker()
    
    try:
        while True:
            print("\nOptions:")
            print("1. Record a new voice note")
            print("2. View recent logs")
            print("3. Exit")
            print("4. Generate voice response")
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\nPreparing to record your voice note...")
                audio_file = record_voice_note()
                
                if not audio_file:
                    print("No audio was recorded. Please try again.")
                    continue
                
                print("\nProcessing your voice note...")
                result = tracker.process_voice_note(audio_file)
                
                if "error" in result:
                    print(f"Error: {result['error']}")
                else:
                    print("\nSuccessfully logged your entry!")
                    print("\nSummary:")
                    print(result["summary"])
            
            elif choice == "2":
                print("\nYour Recent Logs:")
                logs = tracker.get_recent_logs()
                
                if not logs:
                    print("No logs found.")
                    continue
                
                for i, log in enumerate(logs, 1):
                    print(f"\nLog #{i} - {log['date']}")
                    print("-" * 30)
                    print(log['summary'])
            
            elif choice == "3":
                print("Thank you for using Period Tracker!")
                break

            elif choice == "4":
                result = tracker.generate_voice_response("Hello, how are you?")
                if "error" in result:
                    print(f"Error: {result['error']}")
                else:
                    print("\nPlaying voice note...")
                    play(result['audio'])
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    
if __name__ == "__main__":
    main()

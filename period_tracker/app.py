import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from period_tracker.elevenlabs_transcriber import transcribe_audio_file, text_to_speech
from period_tracker.models.database import SessionLocal, User, PeriodLog, get_db
from period_tracker.config.settings import config
from period_tracker.utils.text_processor import extract_period_info, format_period_summary

class PeriodTracker:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.db = SessionLocal()
        self._ensure_user_exists()
    
    def _ensure_user_exists(self):
        """Ensure the user exists in the database"""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if not user:
            user = User(id=self.user_id)
            self.db.add(user)
            self.db.commit()
    
    def process_voice_note(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Process a voice note and extract period information
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dict containing the extracted information and metadata
        """
        # Transcribe the audio
        try:
            transcribed_text = transcribe_audio_file(audio_file_path)
        except Exception as e:
            return {"error": f"Failed to transcribe audio: {str(e)}"}
        
        # Extract period information
        period_info = extract_period_info(transcribed_text)
        
        # Save to database
        log_id = str(uuid.uuid4())
        audio_filename = f"{log_id}.wav"
        audio_path = os.path.join(config.audio_output_dir, audio_filename)
        
        # Move the audio file to the designated directory
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        os.rename(audio_file_path, audio_path)
        
        # Create log entry
        log_entry = PeriodLog(
            id=log_id,
            user_id=self.user_id,
            date=datetime.utcnow(),
            flow=period_info.get("flow"),
            spotting=period_info.get("spotting", False),
            mood=period_info.get("mood", []),
            symptoms=period_info.get("symptoms", []),
            notes=period_info.get("notes"),
            voice_note_path=audio_path,
            transcribed_text=transcribed_text
        )
        
        self.db.add(log_entry)
        self.db.commit()
        
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
    
    def close(self):
        """Close the database connection"""
        self.db.close()

def record_voice_note() -> str:
    """
    Record a voice note using the system's default microphone.
    Returns the path to the recorded audio file.
    """
    import sounddevice as sd
    from scipy.io.wavfile import write
    import tempfile
    
    # Audio recording parameters
    fs = 44100  # Sample rate
    seconds = 10  # Maximum recording duration
    
    print("Recording... (Press Ctrl+C to stop early)")
    try:
        # Record audio
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        write(temp_file.name, fs, recording)  # Save as WAV file
        
        print(f"Recording saved to {temp_file.name}")
        return temp_file.name
        
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
        temp_file.close()
        return ""
    except Exception as e:
        print(f"Error during recording: {e}")
        return ""

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
            
            choice = input("Enter your choice (1-3): ").strip()
            
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
            
            else:
                print("Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        tracker.close()

if __name__ == "__main__":
    main()

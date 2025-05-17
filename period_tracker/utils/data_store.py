from typing import Dict, List, Optional
from datetime import datetime
import uuid

class PeriodDataStore:
    def __init__(self):
        """Initialize the data store with empty collections"""
        self.sessions: Dict[str, Dict] = {}  # Session ID -> Session Data
        self.current_session_id: Optional[str] = None

    def create_session(self) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "logs": [],
            "status": "active"
        }
        self.current_session_id = session_id
        return session_id

    def add_log_to_session(self, session_id: str, log_data: Dict) -> None:
        """Add a log entry to the current session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        self.sessions[session_id]["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "data": log_data
        })

    def get_session_logs(self, session_id: str) -> List[Dict]:
        """Get all logs for a specific session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        return self.sessions[session_id]["logs"]

    def add_log_to_history(self, log_data: Dict) -> None:
        """Add a log entry to session history with additional metadata"""
        if self.current_session_id not in self.sessions:
            raise ValueError("No active session")
            
        # Add metadata about the log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": log_data,
            "has_missing_data": self._check_for_missing_data(log_data),
            "unusual_symptoms": log_data.get("unusual_symptoms", False)
        }
        
        # Add to session logs
        self.sessions[self.current_session_id]["logs"].append(log_entry)
        
    def _check_for_missing_data(self, log_data: Dict) -> bool:
        """Check if the log data has any missing required fields"""
        required_fields = {
            "period": ["status", "flow"],
            "timing": ["date"]
        }
        
        # Check period information
        period_data = log_data.get("period", {})
        if not any(period_data.get(field) for field in required_fields["period"]):
            return True
            
        # Check timing
        timing_data = log_data.get("timing", {})
        if not any(timing_data.get(field) for field in required_fields["timing"]):
            return True
            
        return False

    def get_session_data(self, session_id: str) -> Dict:
        """Get complete session data including logs"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session_data = self.sessions[session_id]
        return {
            "session_id": session_id,
            "start_time": session_data["start_time"],
            "end_time": session_data.get("end_time"),
            "status": session_data["status"],
            "logs": session_data["logs"],
            "has_missing_data": any(log["has_missing_data"] for log in session_data["logs"]),
            "has_unusual_symptoms": any(log["unusual_symptoms"] for log in session_data["logs"])
        }
        
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get all logs for a specific session"""
        session_data = self.get_session_data(session_id)
        return session_data["logs"]

    def get_current_session_id(self) -> Optional[str]:
        """Get the current active session ID"""
        return self.current_session_id

    def end_session(self, session_id: str) -> None:
        """End a session and mark it as completed"""
        if session_id in self.sessions:
            self.sessions[session_id]["end_time"] = datetime.now().isoformat()
            self.sessions[session_id]["status"] = "completed"
            self.current_session_id = None
            # Clear current session if this was the active one
            if self.current_session_id == session_id:
                self.current_session_id = None

    def get_stats(self) -> Dict:
        """Get statistics about the data store"""
        active_sessions = [s for s in self.sessions.values() if s["status"] == "active"]
        completed_sessions = [s for s in self.sessions.values() if s["status"] == "completed"]
        
        # Calculate statistics
        total_logs = sum(len(session["logs"]) for session in self.sessions.values())
        sessions_with_missing_data = sum(
            1 for session in self.sessions.values() 
            if any(log["has_missing_data"] for log in session["logs"])
        )
        sessions_with_unusual_symptoms = sum(
            1 for session in self.sessions.values() 
            if any(log["unusual_symptoms"] for log in session["logs"])
        )
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(active_sessions),
            "completed_sessions": len(completed_sessions),
            "total_logs": total_logs,
            "sessions_with_missing_data": sessions_with_missing_data,
            "sessions_with_unusual_symptoms": sessions_with_unusual_symptoms
        }

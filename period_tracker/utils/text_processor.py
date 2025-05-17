from typing import Dict, List, Optional, Tuple
import re
from ..config.settings import config

def extract_period_info(text: str) -> Dict[str, any]:
    """
    Extract period-related information from text.
    
    Args:
        text: The transcribed text from voice input
        
    Returns:
        Dict containing extracted period information
    """
    text = text.lower()
    result = {
        "flow": None,
        "spotting": False,
        "mood": [],
        "symptoms": [],
        "notes": text.strip()
    }
    
    # Check for flow indicators
    if any(keyword in text for keyword in config.keywords["flow_light"]):
        result["flow"] = "light"
    elif any(keyword in text for keyword in config.keywords["flow_medium"]):
        result["flow"] = "medium"
    elif any(keyword in text for keyword in config.keywords["flow_heavy"]):
        result["flow"] = "heavy"
    
    # Check for spotting
    result["spotting"] = any(keyword in text for keyword in config.keywords["spotting"])
    
    # Extract moods
    mood_mapping = {
        "happy": config.keywords["mood_happy"],
        "sad": config.keywords["mood_sad"],
        "anxious": config.keywords["mood_anxious"],
        "cramps": config.keywords["mood_cramps"],
        "bloated": config.keywords["mood_bloated"],
    }
    
    for mood, keywords in mood_mapping.items():
        if any(keyword in text for keyword in keywords):
            result["mood"].append(mood)
    
    # Extract symptoms (this is a simple implementation)
    # In a production app, you might want to use NLP here
    symptom_keywords = ["headache", "nausea", "fatigue", "tired", "pain", "cramp", "bloat"]
    for symptom in symptom_keywords:
        if symptom in text:
            result["symptoms"].append(symptom)
    
    # Remove duplicates
    result["mood"] = list(set(result["mood"]))
    result["symptoms"] = list(set(result["symptoms"]))
    
    return result

def format_period_summary(log_data: Dict[str, any]) -> str:
    """Format period log data into a human-readable summary"""
    summary_parts = []
    
    if log_data["flow"]:
        summary_parts.append(f"Flow: {log_data['flow'].title()}")
    
    if log_data["spotting"]:
        summary_parts.append("Spotting: Yes")
    
    if log_data["mood"]:
        summary_parts.append(f"Mood: {', '.join(log_data['mood']).title()}")
    
    if log_data["symptoms"]:
        summary_parts.append(f"Symptoms: {', '.join(log_data['symptoms']).title()}")
    
    if log_data["notes"] and len(summary_parts) == 0:
        summary_parts.append(f"Notes: {log_data['notes']}")
    
    return "\n".join(summary_parts) if summary_parts else "No specific details recorded."

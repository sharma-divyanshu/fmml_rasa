from typing import Dict, List, Optional, Tuple
import re
from ..config.settings import config
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_period_info(text: str) -> Dict[str, any]:
    """
    Extract comprehensive period-related information from text using advanced NLP.
    
    Args:
        text: The transcribed text from voice input
        
    Returns:
        Dict containing extracted period information with confidence scores
    """
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Define system prompt for comprehensive analysis
    system_prompt = """You are a health tracker assistant. Your task is to extract health metrics from natural language input about menstrual cycles and related symptoms. 
    
    Metrics to track:
    1. Period Status:
       - Start/End of period (must detect phrases like "started my period", "period began", "got my period", "period ended", "finished my period")
       - Flow intensity (light, medium, heavy, spotting)
       - Duration (number of days)
    
    2. Symptoms:
       - Pain levels (mild, moderate, severe)
       - Types of pain (cramps, headaches, back pain)
       - Other symptoms (bloating, fatigue, nausea, breast tenderness)
    
    3. Mood:
       - Emotional states (happy, sad, tired, energetic, irritable, anxious)
       - Intensity (mild, moderate, severe)
    
    4. Timing:
       - Specific dates ("yesterday", "today", "last week")
       - Relative timing ("since morning", "all day", "in the evening")
    
    5. Severity:
       - Pain levels (1-10 scale)
       - Symptom intensity (mild, moderate, severe)
    
    Return the extracted metrics in JSON format with the following structure:
    {
        "period": {
            "status": "start|end|none",
            "flow": "light|medium|heavy|spotting",
            "duration": "number_of_days"
        },
        "symptoms": [
            {"type": "cramps", "severity": "mild|moderate|severe", "confidence": 0.9}
        ],
        "mood": [
            {"state": "tired", "intensity": "moderate", "confidence": 0.85}
        ],
        "timing": {
            "date": "2023-05-17",
            "time_of_day": "morning|afternoon|evening|night"
        },
        "confidence": 0.85,
        "raw_text": "original text",
        "unusual_symptoms": false
    }

    Important notes:
    1. If the user mentions multiple symptoms, create separate entries for each
    2. If the user mentions severity, include that in the metric_value
    3. If the user mentions timing, include that in the date field
    4. Include a confidence score (0.0-1.0) for each extracted metric
    5. If a metric is not mentioned, do not include it in the output
    6. Handle variations in language (e.g., "cramps", "cramping", "pain")
    7. If the user mentions unusual symptoms (severe, extreme, unusual, abnormal, heavy bleeding, intense pain, fainting, dizziness, fever, vomiting), flag them as unusual
    8. Always include the unusual_symptoms flag in the output
    """
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Call OpenAI API for advanced analysis
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        
        result = eval(response.choices[0].message.content)
        
        # Initialize unusual symptoms flag
        result["unusual_symptoms"] = False
        
        # Check for unusual symptoms in symptoms
        if "symptoms" in result:
            unusual_symptoms = [
                "severe", "extreme", "unusual", "abnormal", 
                "heavy bleeding", "intense pain", "fainting", 
                "dizziness", "fever", "vomiting"
            ]
            
            # Check symptom types for unusual symptoms
            for symptom in result["symptoms"]:
                if any(us in symptom.get("type", "").lower() for us in unusual_symptoms):
                    result["unusual_symptoms"] = True
                    break
            
            # Also check symptom descriptions for unusual indicators
            for symptom in result["symptoms"]:
                if any(us in symptom.get("severity", "").lower() for us in unusual_symptoms):
                    result["unusual_symptoms"] = True
                    break
        
        return result
        
    except Exception as e:
        # Fallback to basic keyword matching if OpenAI fails
        result = {
            "period": {},
            "symptoms": [],
            "mood": [],
            "timing": {},
            "confidence": 0.5,
            "raw_text": text.strip(),
            "error": str(e),
            "unusual_symptoms": False
        }
        
        # Basic keyword matching as backup
        if any(keyword in text.lower() for keyword in config.keywords["flow_light"]):
            result["period"] = {"flow": "light"}
        elif any(keyword in text.lower() for keyword in config.keywords["flow_medium"]):
            result["period"] = {"flow": "medium"}
        elif any(keyword in text.lower() for keyword in config.keywords["flow_heavy"]):
            result["period"] = {"flow": "heavy"}
        
        return result

def format_period_summary(log_data: Dict[str, any]) -> str:
    """Format period log data into a human-readable summary"""
    summary_parts = []
    
    # Format period information
    if "period" in log_data:
        period = log_data["period"]
        if "status" in period:
            summary_parts.append(f"Period Status: {period['status'].title()}")
        if "flow" in period:
            summary_parts.append(f"Flow: {period['flow'].title()}")
        if "duration" in period:
            summary_parts.append(f"Duration: {period['duration']} days")
    
    # Format symptoms with severity
    if "symptoms" in log_data:
        symptom_parts = []
        for symptom in log_data["symptoms"]:
            symptom_str = symptom["type"].title()
            if "severity" in symptom:
                symptom_str += f" ({symptom['severity']})"
            symptom_parts.append(symptom_str)
        if symptom_parts:
            summary_parts.append(f"Symptoms: {', '.join(symptom_parts)}")
    
    # Format mood with intensity
    if "mood" in log_data:
        mood_parts = []
        for mood in log_data["mood"]:
            mood_str = mood["state"].title()
            if "intensity" in mood:
                mood_str += f" ({mood['intensity']})"
            mood_parts.append(mood_str)
        if mood_parts:
            summary_parts.append(f"Mood: {', '.join(mood_parts)}")
    
    # Add timing information
    if "timing" in log_data and log_data["timing"]:
        timing = log_data["timing"]
        timing_parts = []
        if "date" in timing:
            timing_parts.append(f"Date: {timing['date']}")
        if "time_of_day" in timing:
            timing_parts.append(f"Time: {timing['time_of_day'].title()}")
        if timing_parts:
            summary_parts.append(" | ".join(timing_parts))
    
    # Add unusual symptoms flag
    if log_data.get("unusual_symptoms", False):
        summary_parts.append("⚠️ Unusual symptoms detected")
    
    # Add confidence score
    if "confidence" in log_data:
        summary_parts.append(f"Confidence: {log_data['confidence']:.2f}")
    
    return "\n".join(summary_parts) if summary_parts else "No specific details recorded."

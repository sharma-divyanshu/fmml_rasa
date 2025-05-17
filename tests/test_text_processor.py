import os
from dotenv import load_dotenv
from period_tracker.utils.text_processor import extract_period_info, format_period_summary

# Load environment variables
load_dotenv()

def test_text_processor():
    """Test the text processor with various inputs"""
    test_cases = [
        {
            "input": "I started my period yesterday and it's been heavy all day with severe cramps",
            "expected": {
                "period": {"status": "start", "flow": "heavy"},
                "symptoms": [{"type": "cramps", "severity": "severe"}],
                "unusual_symptoms": False
            },
            "fallback": {
                "period": {"flow": "heavy"},
                "symptoms": [],
                "unusual_symptoms": False
            }
        },
        {
            "input": "Today I feel really tired and have been bloated since morning",
            "expected": {
                "mood": [{"state": "tired", "intensity": "moderate"}],
                "symptoms": [{"type": "bloating"}],
                "unusual_symptoms": False
            },
            "fallback": {
                "period": {},
                "symptoms": [],
                "unusual_symptoms": False
            }
        },
        {
            "input": "I noticed some spotting last night and had mild headaches",
            "expected": {
                "period": {"flow": "spotting"},
                "symptoms": [{"type": "headache", "severity": "mild"}],
                "unusual_symptoms": False
            },
            "fallback": {
                "period": {},
                "symptoms": [],
                "unusual_symptoms": False
            }
        },
        {
            "input": "I'm having really severe cramps and heavy bleeding - this is unusual for me",
            "expected": {
                "symptoms": [{"type": "cramps", "severity": "severe"},
                           {"type": "heavy bleeding", "severity": "severe"}],
                "unusual_symptoms": True
            },
            "fallback": {
                "period": {},
                "symptoms": [],
                "unusual_symptoms": False
            }
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test['input']}")
        
        # Process the text
        result = extract_period_info(test['input'])
        
        print("\nRaw Result:")
        print(result)
        
        print("\nFormatted Summary:")
        print(format_period_summary(result))
        
        # Check if expected keys are present
        expected_keys = test['expected'].keys()
        missing_keys = [k for k in expected_keys if k not in result]
        if missing_keys:
            print(f"\n⚠️ Warning: Missing expected keys: {missing_keys}")
        
        # Verify unusual symptoms flag
        expected_unusual = test['expected'].get('unusual_symptoms', False)
        if result.get('unusual_symptoms', False) != expected_unusual:
            print(f"\n⚠️ Warning: Unusual symptoms flag mismatch. Expected: {expected_unusual}, Got: {result.get('unusual_symptoms')}")
        
        # If we're in fallback mode (error present), check against fallback expectations
        if 'error' in result:
            fallback_keys = test['fallback'].keys()
            missing_fallback = [k for k in fallback_keys if k not in result]
            if missing_fallback:
                print(f"\n⚠️ Warning: Missing fallback keys: {missing_fallback}")
            
            for key in fallback_keys:
                if result.get(key) != test['fallback'][key]:
                    print(f"\n⚠️ Warning: Fallback value mismatch for {key}. Expected: {test['fallback'][key]}, Got: {result.get(key)}")

if __name__ == "__main__":
    test_text_processor()

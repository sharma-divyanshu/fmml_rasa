import streamlit as st
import os
from datetime import datetime as dt

from streamlit.runtime.state import session_state
from period_tracker.app import PeriodTracker
from period_tracker.utils.audio_recorder import record_audio_until_x
import tempfile
from period_tracker.api.server import process_audio

import uuid

# Initialize period tracker
period_tracker = PeriodTracker()

# --- Page Config ---
st.set_page_config(page_title="RASA: Wellness that Listens", page_icon="🩸", layout="centered")

# --- In-Memory Storage ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "step" not in st.session_state:
    st.session_state.step = 1

# --- Step 1: Welcome ---
if st.session_state.step == 1:
    st.title("🩸 RASA: Wellness that Listens")
    st.write("Track your cycle, symptoms, and feelings using your voice.")
    if st.button("Get Started"):
        st.session_state.step = 2

# --- Step 2: Name ---
elif st.session_state.step == 2:
    st.title("Step 1: What's your name?")
    name = st.text_input("Enter your name")
    if st.button("Next") and name.strip():
        st.session_state.user_profile["name"] = name
        st.session_state.step = 3

# --- Step 3: Age Range ---
elif st.session_state.step == 3:
    st.title("Step 2: Select your age range")
    age_range = st.radio("Choose one", ["18-24", "25-34", "35-44", "45-54", "55+", "Prefer not to say"])
    if st.button("Next"):
        st.session_state.user_profile["age_range"] = age_range
        st.session_state.step = 4

# --- Step 4: Gender ---
elif st.session_state.step == 4:
    st.title("Step 3: How do you identify?")
    gender = st.radio("Select one", ["Female", "Male", "Non-binary", "Prefer not to say", "Other"])
    if st.button("Next"):
        st.session_state.user_profile["gender"] = gender
        st.session_state.step = 5

# --- Step 5: Tracking Goals ---
elif st.session_state.step == 5:
    st.title("Step 4: What are you hoping to track?")
    goals = st.multiselect("Select all that apply:", [
        "Predicting my period",
        "Understanding symptoms (cramps, mood, etc.)",
        "Tracking irregularities",
        "Trying to conceive / Fertility tracking",
        "General health awareness",
        "Something else"
    ])
    if st.button("Next"):
        st.session_state.user_profile["tracking_goals"] = goals
        st.session_state.step = 6

# --- Step 6: Last Period Date ---
elif st.session_state.step == 6:
    st.title("Step 5: When did your last period start?")
    last_period = st.date_input("Select the date")
    if st.button("Next"):
        st.session_state.user_profile["last_period_start"] = str(last_period)
        st.session_state.step = 7

# --- Step 7: Typical Cycle Length ---
elif st.session_state.step == 7:
    st.title("Step 6: What's your typical cycle length?")
    cycle_length = st.number_input("Enter days", min_value=15, max_value=60, value=28)
    if st.button("Next"):
        st.session_state.user_profile["cycle_length"] = cycle_length
        st.session_state.step = 8

# --- Step 8: Typical Period Duration ---
elif st.session_state.step == 8:
    st.title("Step 7: How long does your period usually last?")
    period_duration = st.number_input("Enter days", min_value=1, max_value=10, value=5)
    if st.button("Next"):
        st.session_state.user_profile["period_duration"] = period_duration
        st.session_state.step = 9

# --- Step 9: Privacy & Data Usage ---
elif st.session_state.step == 9:
    st.title("Your Health Data is Private.")
    st.write("We are committed to protecting your personal health information.")
    share_data = st.checkbox("Help improve the app by sharing anonymous usage data", value=True)
    if st.button("Finish Setup"):
        st.session_state.user_profile["share_data"] = share_data
        st.session_state.step = 10

# --- Step 10: Voice-Based Tracker ---
elif st.session_state.step == 10:
    # Initialize session if not already done
    if "session_id" not in st.session_state:
        session_response = period_tracker.start_new_session()
        st.session_state.session_id = session_response["session_id"]
        st.session_state.session_status = "active"
        st.session_state.logs = []
        
    st.title("🎙️ Voice-Based Period Health Tracker")
    st.write("Speak and submit below. Your voice and logs will be saved for review.")
    
    # Show session status
    st.write(f"Session ID: {st.session_state.session_id}")
    if st.session_state.session_status == "active":
        st.write("Status: Active")
    else:
        st.write("Status: Completed")
    
    # Record audio
    if st.button("Start Recording"):
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_file.close()
        
        # Record audio
        record_audio_until_x(temp_file.name)
        
        # Process the voice note
        result = process_audio(temp_file.name)
        
        # Store the log
        st.session_state.logs.append(result)
        
        # Show summary
        st.success(result)
        
        # Show conversation history
        st.subheader("Conversation History")
        for msg in result["conversation_history"]:
            role = "User" if msg["role"] == "user" else "Assistant"
            st.write(f"**{role}:** {msg["content"]}")
            
        # Show warnings if any
        if result.get("missing_fields"):
            st.warning("Some required information is missing. Please provide more details.")
        if result.get("has_unusual_symptoms"):
            st.warning("Unusual symptoms detected. Please consider consulting a healthcare professional.")
                
    # End session button
    if st.button("End Session"):
        end_result = period_tracker.end_current_session()
        st.session_state.session_status = "completed"
        st.success("Session ended successfully")
        
    # Show session statistics
    st.subheader("Session Statistics")
    if st.session_state.logs:
        st.write(f"Total logs: {len(st.session_state.logs)}")
        missing_data = sum(1 for log in st.session_state.logs if log.get("missing_fields", []))
        unusual_symptoms = sum(1 for log in st.session_state.logs if log.get("has_unusual_symptoms", []))
        st.write(f"Logs with missing data: {missing_data}")
        st.write(f"Logs with unusual symptoms: {unusual_symptoms}")
        save_dir = "data/audio"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        file_path = st.session_state.logs[-1]["audio_url"]

        st.success(f"Saved your voice as {file_path}")
        with open(file_path, "rb") as f:
            audio_data = f.read()
        st.audio(audio_data, format="audio/wav")
        st.info("Simulated AI Response Played (replace this with your backend output)")

    st.write("You can record again any time without reloading the page.")

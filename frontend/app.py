import streamlit as st
import os
from datetime import datetime as dt

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
    st.title("🎙️ Voice-Based Period Health Tracker")
    st.write("Speak and submit below. Your voice and logs will be saved for review.")

    audio_bytes = st.audio_input("Record your voice")

    if audio_bytes:
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        save_dir = "recordings"
        os.makedirs(save_dir, exist_ok=True)
        file_path = f"{save_dir}/{st.session_state.user_profile.get('name', 'user')}_{timestamp}.wav"
        with open(file_path, "wb") as f:
            f.write(audio_bytes.getvalue())

        st.success(f"Saved your voice as {file_path}")
        st.audio(audio_bytes, format="audio/wav")
        st.info("Simulated AI Response Played (replace this with your backend output)")

    st.write("You can record again any time without reloading the page.")

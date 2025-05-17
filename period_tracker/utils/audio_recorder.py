import sounddevice as sd
import numpy as np
import wavio as wv
from pynput import keyboard
import threading
import sys

# --- Configuration for Recording ---
SAMPLERATE = 44100  # Samples per second (standard CD quality)
CHANNELS = 1        # Number of audio channels (2 for stereo, 1 for mono)
DTYPE = 'int16'     # Data type for audio samples (16-bit integers are common)
CHUNK_SIZE = 1024   # Number of frames read per buffer (affects latency and processing chunks)

# --- Global Variables and Events ---
# Event to signal when to stop recording. Set by the keyboard listener.
stop_recording_event = threading.Event()

# List to store the recorded audio frames (chunks of audio data).
audio_frames = []

# --- Keyboard Listener Callback ---
def on_press(key):
    """
    Callback function executed when a keyboard key is pressed.
    Checks if the pressed key is 'x' and signals the recording to stop.
    """
    try:
        # Check if the pressed key is the character 'x'
        if hasattr(key, 'char') and key.char == 'x':
            print("\n'x' key pressed. Stopping recording...")
            # Set the event to signal the recording loop to stop
            stop_recording_event.set()
            # Return False to stop the keyboard listener thread
            return False
    except AttributeError:
        # Ignore special keys (like Shift, Ctrl, etc.) that don't have a 'char' attribute
        pass

# --- Audio Recording Function ---
def record_audio_until_x(filename="recorded_audio.wav"):
    """
    Records audio from the microphone until the 'x' key is pressed,
    then saves the recording to a WAV file.

    Args:
        filename (str): The name of the file to save the audio to (e.g., "my_clip.wav").
                        Defaults to "recorded_audio.wav".
    """
    global audio_frames # Access the global list to store frames

    print("Starting audio recording...")
    print(f"Press the 'x' key on your keyboard to stop recording and save.")

    # Start the keyboard listener in a separate thread.
    # This allows the script to listen for key presses while recording audio.
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # --- Audio Recording Loop ---
    try:
        # Use sounddevice.InputStream to capture audio from the default input device.
        # The 'with' statement ensures the stream is properly closed even if errors occur.
        with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype=DTYPE, blocksize=CHUNK_SIZE) as stream:
            print("Recording active...")
            # Loop as long as the stop_recording_event has not been set
            while not stop_recording_event.is_set():
                # Read a block of audio data from the stream.
                # This call blocks until a chunk of audio is available.
                data, overflowed = stream.read(CHUNK_SIZE)
                # Append the recorded data chunk to our list of frames
                audio_frames.append(data)
                # Check for buffer overflow - indicates the system can't keep up
                if overflowed:
                    print("Warning: Audio input buffer overflowed!")

    except Exception as e:
        # Catch any exceptions that occur during recording (e.g., no input device)
        print(f"\nAn error occurred during recording: {e}")
        # Ensure the stop event is set so the script doesn't hang
        stop_recording_event.set()

    finally:
        # --- Stopping and Saving ---
        # Wait for the keyboard listener thread to finish (after 'x' was pressed and on_press returned False)
        listener.join()

        # Check if any audio data was actually recorded
        if not audio_frames:
            print("No audio data was recorded.")
            return # Exit the function if nothing was recorded

        print("Recording stopped.")
        print("Combining audio frames...")
        # Concatenate all the recorded NumPy arrays into a single array
        recorded_audio = np.concatenate(audio_frames, axis=0)

        print(f"Saving audio to {filename}...")
        try:
            # Use wavio to write the NumPy array to a WAV file.
            # wavio automatically handles the correct format based on the dtype of the array.
            wv.write(filename, recorded_audio, SAMPLERATE, sampwidth=np.dtype(DTYPE).itemsize)
            print("Audio saved successfully.")
            return filename
        except Exception as e:
            # Catch any errors during the file saving process
            print(f"An error occurred while saving the audio file: {e}")

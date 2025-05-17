import os
from typing import Optional, Union
import requests
from pathlib import Path
from elevenlabs.client import ElevenLabs
import io

# load api key from .env file
import dotenv
dotenv.load_dotenv()


class ElevenLabsTranscriber:
    """
    A class to handle audio transcription using ElevenLabs API.
    """    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the transcriber with an optional API key.
        If no API key is provided, it will be read from the ELEVEN_LABS_API_KEY environment variable.
        
        Args:
            api_key (str, optional): Your ElevenLabs API key. Defaults to None.
            
        Raises:
            ValueError: If no API key is provided and ELEVEN_LABS_API_KEY is not set.
        """
        self.api_key = api_key or os.getenv("ELEVEN_LABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Either pass it to the constructor or set the "
                "ELEVEN_LABS_API_KEY environment variable."
            )
        self.client = ElevenLabs(api_key=self.api_key)
    
    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default voice ID (Rachel)
        model_id: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> str:
        """
        Convert text to speech and save as an audio file using ElevenLabs API.
        
        Args:
            text (str): The text to convert to speech.
            output_path (str): Path where the output audio file will be saved.
            voice_id (str, optional): ID of the voice to use. Defaults to "21m00Tcm4TlvDq8ikWAM" (Rachel).
            model_id (str, optional): ID of the model to use. Defaults to "eleven_monolingual_v1".
            stability (float, optional): Stability parameter (0.0 to 1.0). Defaults to 0.5.
            similarity_boost (float, optional): Similarity boost parameter (0.0 to 1.0). Defaults to 0.75.
            
        Returns:
            str: Path to the generated audio file.
            
        Raises:
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response is not successful.
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        # Ensure output directory exists
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        audio = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            stability=stability,
            similarity_boost=similarity_boost
        )
        
        # Save the audio file
        with open(output_path, 'wb') as f:
            f.write(audio)
        
        return output_path

    def transcribe_audio(
        self,
        audio_file_path: str,
        model_id: str = "scribe_v1"
    ) -> str:
        """
        Transcribe an audio file using ElevenLabs API.
        
        Args:
            audio_file_path (str): Path to the audio file to transcribe.
            model_id (str, optional): ID of the model to use for transcription. 
                                   Defaults to "eleven_monolingual_v1".
        
        Returns:
            str: The transcribed text.
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist.
            requests.exceptions.RequestException: If the API request fails.
            ValueError: If the API response doesn't contain the expected data.
        """
        if not os.path.isfile(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        with open(audio_file_path, "rb") as audio_file:
            audio_data = io.BytesIO(audio_file.read())
            response = self.client.speech_to_text.convert(
                file=audio_data,
                model_id=model_id,
            )
            print(response)
            # return the transcribed text
            return response.text

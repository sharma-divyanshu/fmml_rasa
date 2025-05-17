import os
from typing import Optional, Union
import requests
from pathlib import Path

# load api key from .env file
import dotenv
dotenv.load_dotenv()


class ElevenLabsTranscriber:
    """
    A class to handle audio transcription using ElevenLabs API.
    """
    
    BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
    
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
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            stream=True
        )
        
        response.raise_for_status()
        
        # Save the audio file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        return output_path

    def transcribe_audio(
        self,
        audio_file_path: str,
        model_id: str = "eleven_monolingual_v1"
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
        
        url = f"{self.BASE_URL}/{model_id}"
        headers = {
            "xi-api-key": self.api_key,
            "accept": "application/json",
        }
        
        with open(audio_file_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_file_path), audio_file, "audio/mpeg")}
            response = requests.post(url, headers=headers, files=files)
        
        response.raise_for_status()
        result = response.json()
        
        if not isinstance(result, dict) or "text" not in result:
            raise ValueError("Unexpected API response format")
            
        return result["text"].strip()


def transcribe_audio_file(
    audio_file_path: str,
    api_key: Optional[str] = None,
    model_id: str = "eleven_monolingual_v1"
) -> str:
    """
    Convenience function to transcribe an audio file in one line.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe.
        api_key (str, optional): Your ElevenLabs API key. Defaults to None.
        model_id (str, optional): ID of the model to use for transcription. 
                               Defaults to "eleven_monolingual_v1".
                               
    Returns:
        str: The transcribed text.
    """
    transcriber = ElevenLabsTranscriber(api_key=api_key)
    return transcriber.transcribe_audio(audio_file_path, model_id=model_id)


def text_to_speech(
    text: str,
    output_path: str,
    api_key: Optional[str] = None,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    model_id: str = "eleven_monolingual_v1",
    stability: float = 0.5,
    similarity_boost: float = 0.75
) -> str:
    """
    Convenience function to convert text to speech and save as an audio file in one line.
    
    Args:
        text (str): The text to convert to speech.
        output_path (str): Path where the output audio file will be saved.
        api_key (str, optional): Your ElevenLabs API key. Defaults to None.
        voice_id (str, optional): ID of the voice to use. Defaults to "21m00Tcm4TlvDq8ikWAM" (Rachel).
        model_id (str, optional): ID of the model to use. Defaults to "eleven_monolingual_v1".
        stability (float, optional): Stability parameter (0.0 to 1.0). Defaults to 0.5.
        similarity_boost (float, optional): Similarity boost parameter (0.0 to 1.0). Defaults to 0.75.
        
    Returns:
        str: Path to the generated audio file.
    """
    transcriber = ElevenLabsTranscriber(api_key=api_key)
    return transcriber.text_to_speech(
        text=text,
        output_path=output_path,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost
    )

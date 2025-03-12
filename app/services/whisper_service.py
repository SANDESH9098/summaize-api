import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file_path: Path to the audio file

    Returns:
        Transcribed text

    Raises:
        Exception: If transcription fails
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        # Whisper returns a dict with a 'text' key
        if isinstance(transcript, dict) and 'text' in transcript:
            return transcript['text']
        else:
            return transcript

    except Exception as e:
        raise Exception(f"Whisper transcription failed: {str(e)}")
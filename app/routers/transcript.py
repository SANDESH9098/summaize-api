# transcript.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
import os
import tempfile
from app.services.transcript_service import get_youtube_transcript
from app.services.whisper_service import transcribe_audio
from app.utils.youtube_utils import download_youtube_audio, validate_youtube_id

router = APIRouter(prefix="/api")


class TranscriptResponse(BaseModel):
    video_id: str
    transcript: str
    source: str  # 'youtube' or 'whisper'
    language: str  # The language code of the transcript


@router.get("/transcript/{video_id}", response_model=TranscriptResponse)
async def get_transcript(video_id: str, lang: str = Query(None, description="Language code (e.g., 'en', 'te', 'ja')")):
    """
    Get transcript for a YouTube video.
    First tries to fetch captions using youtube-transcript-api.
    If captions don't exist, returns a 404 so frontend can call the transcribe endpoint.

    Optional query parameter 'lang' can be provided to specify the preferred language.
    """
    # Validate YouTube ID
    if not validate_youtube_id(video_id):
        raise HTTPException(status_code=400, detail="Invalid YouTube video ID")

    try:
        transcript, language = get_youtube_transcript(video_id, lang)
        return {
            "video_id": video_id,
            "transcript": transcript,
            "source": "youtube",
            "language": language
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Transcript not found: {str(e)}"
        )


@router.get("/transcribe/{video_id}", response_model=TranscriptResponse)
async def transcribe_video(video_id: str, background_tasks: BackgroundTasks,
                           lang: str = Query(None, description="Language code for Whisper (e.g., 'en', 'te', 'ja')")):
    """
    Transcribe a YouTube video using Whisper AI.
    This is used as a fallback when captions are not available.

    Optional query parameter 'lang' can be provided to specify the language for Whisper.
    """
    # Validate YouTube ID
    if not validate_youtube_id(video_id):
        raise HTTPException(status_code=400, detail="Invalid YouTube video ID")

    try:
        # Create a temporary directory for the audio file
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_file = os.path.join(temp_dir, f"{video_id}.mp3")

            # Download audio
            download_youtube_audio(video_id, audio_file)

            # Transcribe audio using Whisper (you'll need to update whisper_service to handle language)
            transcript = transcribe_audio(audio_file, lang)

            # Set the language that was used (you should have whisper_service return this)
            # For now we'll just use the requested language or default to 'auto'
            language = lang if lang else "auto"

            # Clean up will happen automatically when the temp_dir context exits
            background_tasks.add_task(lambda: None)  # No-op to keep temp files until response is sent

            return {
                "video_id": video_id,
                "transcript": transcript,
                "source": "whisper",
                "language": language
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe video: {str(e)}"
        )
from fastapi import APIRouter, HTTPException, status
from .services.transcript_service import get_youtube_transcript
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/transcript/{video_id}")
async def get_transcript(video_id: str):
    try:
        transcript = get_youtube_transcript(video_id)
        return {"transcript": transcript}
    except Exception as e:
        logger.error(f"Error getting transcript for {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transcript: {str(e)}"
        )

@router.get("/transcribe/{video_id}")
async def transcribe_video(video_id: str):
    try:
        transcript = get_youtube_transcript(video_id)
        return {"result": "processed transcript"}
    except Exception as e:
        logger.error(f"Error transcribing video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe video: {str(e)}"
        )
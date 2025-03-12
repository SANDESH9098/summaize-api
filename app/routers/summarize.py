from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.openai_service import summarize_transcript

router = APIRouter(prefix="/api")


class SummarizeRequest(BaseModel):
    transcript: str
    max_takeaways: int = 5


class KeyTakeaway(BaseModel):
    title: str
    description: str


class SummarizeResponse(BaseModel):
    takeaways: List[KeyTakeaway]
    original_length: int
    summary_length: int


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    Summarize a transcript using OpenAI GPT-4.
    Returns 3-5 key takeaways.
    """
    if not request.transcript or len(request.transcript.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Transcript is too short to summarize"
        )

    try:
        takeaways = summarize_transcript(
            request.transcript,
            max_takeaways=request.max_takeaways
        )

        return {
            "takeaways": takeaways,
            "original_length": len(request.transcript),
            "summary_length": sum(len(t["title"]) + len(t["description"]) for t in takeaways)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize transcript: {str(e)}"
        )
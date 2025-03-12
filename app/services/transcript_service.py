from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

def get_youtube_transcript(video_id: str) -> str:
    """
    Fetch transcript for a YouTube video using youtube-transcript-api.

    Args:
        video_id: YouTube video ID

    Returns:
        Combined transcript text

    Raises:
        Exception: If transcript is not available
    """
    try:
        # Try to get transcript in English first
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find English transcript first
        try:
            transcript = transcript_list.find_transcript(['en'])
        except NoTranscriptFound:
            # If no English transcript is found, just use the first available
            transcript = transcript_list.find_transcript([])

        # Get the transcript
        transcript_pieces = transcript.fetch()

        # Combine all pieces into a single text
        full_transcript = " ".join([piece.text for piece in transcript_pieces])

        # Clean up the transcript (remove timestamps, speaker identifications, etc.)
        full_transcript = clean_transcript(full_transcript)

        return full_transcript

    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise Exception(f"No transcripts found for video: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching transcript: {str(e)}")

def clean_transcript(transcript: str) -> str:
    """
    Clean up transcript text by removing common artifacts and normalizing spacing.

    Args:
        transcript: Raw transcript text

    Returns:
        Cleaned transcript text
    """
    # Remove timestamps like [00:00]
    cleaned = re.sub(r'\[\d+:\d+\]', '', transcript)

    # Remove speaker identifications like "Speaker 1:", "John:", etc.
    cleaned = re.sub(r'^\s*[A-Za-z\s]+:', '', cleaned, flags=re.MULTILINE)

    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Remove multiple newlines
    cleaned = re.sub(r'\n+', '\n', cleaned)

    # Trim whitespace
    cleaned = cleaned.strip()

    return cleaned
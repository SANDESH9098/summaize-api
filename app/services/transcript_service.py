# transcript_service.py
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re


def get_youtube_transcript(video_id: str, language_code: str = None) -> tuple[str, str]:
    """
    Fetch transcript for a YouTube video using youtube-transcript-api.

    Args:
        video_id: YouTube video ID
        language_code: Preferred language code (e.g., 'en', 'te', 'ja')

    Returns:
        Tuple of (combined transcript text, language code that was used)

    Raises:
        Exception: If transcript is not available
    """
    try:
        # Define a list of proxies to use (you'll need to get actual working proxies)
        proxies = [
            'http://brd-customer-hl_56c42ece-zone-summaize_proxy:46sm0t40kivs@brd.superproxy.io:33335',
            # Add more proxies
        ]
        
        # Get list of available transcripts with proxies
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)

        # Try to find transcript in the requested language
        if language_code:
            try:
                transcript = transcript_list.find_transcript([language_code])
                used_language = language_code
            except NoTranscriptFound:
                # If requested language not found, fall back to English
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    used_language = 'en'
                except NoTranscriptFound:
                    # If English not found, use first available
                    transcript = transcript_list.find_transcript([])
                    # Get the language of the transcript we found
                    used_language = transcript.language_code
        else:
            # No language specified, try English first
            try:
                transcript = transcript_list.find_transcript(['en'])
                used_language = 'en'
            except NoTranscriptFound:
                # If no English transcript, use first available
                transcript = transcript_list.find_transcript([])
                used_language = transcript.language_code

        # Get the transcript
        transcript_pieces = transcript.fetch()

        # Combine all pieces into a single text
        full_transcript = " ".join([piece.text for piece in transcript_pieces])

        # Clean up the transcript (remove timestamps, speaker identifications, etc.)
        full_transcript = clean_transcript(full_transcript)

        return full_transcript, used_language

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
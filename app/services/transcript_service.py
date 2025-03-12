from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.exceptions import TranscriptsDisabled, NoTranscriptFound
import requests
import yt_dlp
import logging
from .proxy_service import proxy_manager
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def get_youtube_transcript(video_id: str, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Get transcript for a YouTube video using proxies with retry logic
    """
    retries = 0
    errors = []
    
    while retries < max_retries:
        try:
            # Try to get a proxy
            proxy = proxy_manager.get_random_proxy()
            if proxy:
                logger.info(f"Using proxy for video {video_id}")
                
                # Configure yt-dlp options with proxy
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'proxy': proxy.get('http', ''),  # YouTube API typically uses HTTP
                }
                
                # For YouTube Transcript API, we need to use environment variables or system-wide proxy settings
                # so we'll manually request the transcript data
                try:
                    # First attempt with YouTube Transcript API but with proxy settings
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                        if info.get('subtitles') or info.get('automatic_captions'):
                            # Found captions with proxy, now use YouTubeTranscriptApi
                            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                            return transcript_list
                except Exception as e:
                    logger.warning(f"Error using yt-dlp with proxy: {e}, falling back to direct API call")
                    
                    # Fallback to direct YouTube Transcript API call
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        return transcript_list
                    except Exception as transcript_e:
                        errors.append(f"YouTube Transcript API error: {transcript_e}")
            else:
                # If no proxy available, try without proxy
                logger.warning("No proxy available, attempting without proxy")
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                return transcript_list
                
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            # These are terminal errors - retrying won't help
            logger.error(f"Transcript not available for video {video_id}: {e}")
            raise
        except Exception as e:
            logger.warning(f"Attempt {retries+1} failed: {e}")
            errors.append(str(e))
            retries += 1
            # Add a small delay before retrying
            time.sleep(1)
    
    # If all retries failed
    logger.error(f"Failed to get transcript after {max_retries} attempts. Errors: {errors}")
    raise Exception(f"Failed to get transcript after {max_retries} attempts: {'; '.join(errors)}")

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
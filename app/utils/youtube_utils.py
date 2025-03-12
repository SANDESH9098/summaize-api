import re
import yt_dlp
import os


def validate_youtube_id(video_id: str) -> bool:
    """
    Validate that a string is a valid YouTube video ID.

    Args:
        video_id: YouTube video ID to validate

    Returns:
        True if valid, False otherwise
    """
    # YouTube IDs are 11 characters, typically containing alphanumeric chars, dash, and underscore
    if re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
        return True
    return False


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from a URL.

    Args:
        url: YouTube URL

    Returns:
        YouTube video ID

    Raises:
        ValueError: If URL is not a valid YouTube URL
    """
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',  # Standard watch URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\?\s]+)',  # Embed URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^\?\s]+)',  # Old embed URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/[^\/]+\/([^\?\s]+)',  # User URL
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/[^\/]+\/([^\?\s]+)',  # Channel URL
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\?\s]+)'  # Shortened URL
    ]

    # Try each pattern
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Could not extract video ID from URL")


def download_youtube_audio(video_id: str, output_path: str) -> None:
    """
    Download audio from a YouTube video using yt-dlp.

    Args:
        video_id: YouTube video ID
        output_path: Path to save the audio file

    Raises:
        Exception: If download fails
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path.replace('.mp3', ''),  # yt-dlp adds the extension automatically
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise Exception(f"Failed to download audio: {str(e)}")
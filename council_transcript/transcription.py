"""Transcript extraction from YouTube captions and audio."""

import logging
import re
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp
import whisper
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

logger = logging.getLogger(__name__)


def _split_sentences(text: str) -> str:
    """Put each sentence on its own line.

    Splits on sentence-ending punctuation (. ! ?) while preserving
    the punctuation and spacing.

    Args:
        text: The text to split

    Returns:
        Text with each sentence on a new line
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return "\n".join(s.strip() for s in sentences if s.strip())


class TranscriptExtractor:
    """Extract transcripts from YouTube videos."""

    def __init__(self, config):
        """Initialize the extractor.

        Args:
            config: Settings object with configuration
        """
        self.config = config
        self.whisper_model = None  # Lazy load on first use

    def unload_model(self) -> None:
        """Release the Whisper model from memory."""
        if self.whisper_model is not None:
            del self.whisper_model
            self.whisper_model = None
            logger.info("Whisper model unloaded from memory")

    def extract_captions(self, video_id: str, language_codes: Optional[list] = None) -> Optional[str]:
        """Extract captions using youtube-transcript-api.

        Args:
            video_id: YouTube video ID
            language_codes: List of language codes to try (e.g., ['en', 'en-US'])
                           Defaults to ['en', 'en-US']

        Returns:
            Transcript text or None if captions unavailable
        """
        if language_codes is None:
            language_codes = ["en", "en-US"]

        try:
            transcript_obj = YouTubeTranscriptApi().fetch(
                video_id, languages=tuple(language_codes)
            )

            # Convert FetchedTranscript to list of dicts
            transcript_list = list(transcript_obj)

            # Combine transcript entries into continuous text
            transcript_text = " ".join([entry["text"] for entry in transcript_list])
            logger.info(f"Successfully extracted captions for video {video_id}")
            return transcript_text

        except (NoTranscriptFound, TranscriptsDisabled) as e:
            logger.warning(f"Captions not available for {video_id}: {e}")
            return None
        except VideoUnavailable as e:
            logger.error(f"Video unavailable: {video_id}")
            raise
        except Exception as e:
            logger.error(f"Error extracting captions: {e}")
            return None

    def extract_transcript(self, video_id: str) -> str:
        """Extract transcript from captions or audio.

        Strategy:
        1. Try captions from youtube-transcript-api
        2. Fall back to Whisper audio transcription

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript text with each sentence on its own line

        Raises:
            Exception: If both strategies fail
        """
        logger.info(f"Starting transcript extraction for {video_id}")

        # Try captions first
        captions = self.extract_captions(video_id)
        if captions:
            return _split_sentences(captions)

        logger.info("Captions not available, falling back to audio transcription with Whisper...")
        try:
            transcript = self._transcribe_with_whisper(video_id)
            return _split_sentences(transcript)
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise

    def _transcribe_with_whisper(self, video_id: str) -> str:
        """Transcribe audio using local Whisper model.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript text

        Raises:
            Exception: If transcription fails
        """
        logger.info(f"Downloading audio from video {video_id}...")
        audio_path = self._download_audio(video_id)

        try:
            logger.info("Loading Whisper model...")
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model(self.config.whisper_model_size)

            logger.info("Transcribing audio with Whisper...")
            result = self.whisper_model.transcribe(str(audio_path))
            transcript_text = result["text"]

            logger.info(f"Successfully transcribed audio for video {video_id}")
            return transcript_text
        finally:
            # Clean up audio file
            if audio_path.exists():
                audio_path.unlink()
                logger.debug(f"Cleaned up audio file {audio_path}")

    def _download_audio(self, video_id: str) -> Path:
        """Download audio from YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Path to downloaded audio file

        Raises:
            Exception: If download fails
        """
        temp_dir = Path(tempfile.gettempdir()) / "council_transcript"
        temp_dir.mkdir(exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": str(temp_dir / "%(id)s"),
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug(f"Downloading audio for {video_id}...")
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

            # Locate the actual output file (glob to handle version-dependent extensions)
            matches = list(temp_dir.glob(f"{video_id}.*"))
            if not matches:
                raise FileNotFoundError(
                    f"Audio download produced no output file for {video_id}. "
                    f"Files in {temp_dir}: {list(temp_dir.iterdir())}"
                )
            # Take the most recently modified file in case of duplicates
            audio_path = max(matches, key=lambda p: p.stat().st_mtime)
            logger.info(f"Audio downloaded to {audio_path}")
            return audio_path
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            raise

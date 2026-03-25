"""Transcript extraction from YouTube captions and audio."""

import logging
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


class TranscriptExtractor:
    """Extract transcripts from YouTube videos."""

    def __init__(self, config):
        """Initialize the extractor.

        Args:
            config: Settings object with configuration
        """
        self.config = config
        self.whisper_model = None  # Lazy load on first use

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
            Transcript text

        Raises:
            Exception: If both strategies fail
        """
        logger.info(f"Starting transcript extraction for {video_id}")

        # Try captions first
        captions = self.extract_captions(video_id)
        if captions:
            return captions

        logger.info("Captions not available, falling back to audio transcription with Whisper...")
        try:
            transcript = self._transcribe_with_whisper(video_id)
            return transcript
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
                self.whisper_model = whisper.load_model("base")

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

        audio_path = temp_dir / f"{video_id}.mp3"

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

            if audio_path.exists():
                logger.info(f"Audio downloaded to {audio_path}")
                return audio_path
            else:
                raise Exception(f"Audio download failed for {video_id}")
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            raise

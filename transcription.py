"""Transcript extraction with multiple fallback strategies."""

import logging
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptAvailable,
    TranscriptsDisabled,
    VideoUnavailable,
)

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Extract transcripts from YouTube videos with fallback strategies."""

    def __init__(self, config):
        """Initialize the extractor.

        Args:
            config: Settings object with API keys and configuration
        """
        self.config = config
        self.openai_api_key = config.openai_api_key
        self.anthropic_api_key = config.anthropic_api_key

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
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=language_codes
            )

            # Combine transcript entries into continuous text
            transcript_text = " ".join([entry["text"] for entry in transcript_list])
            logger.info(f"Successfully extracted captions for video {video_id}")
            return transcript_text

        except (NoTranscriptAvailable, TranscriptsDisabled) as e:
            logger.warning(f"Captions not available for {video_id}: {e}")
            return None
        except VideoUnavailable as e:
            logger.error(f"Video unavailable: {video_id}")
            raise
        except Exception as e:
            logger.error(f"Error extracting captions: {e}")
            return None

    def extract_transcript(self, video_id: str) -> str:
        """Extract transcript using fallback strategy.

        Strategy:
        1. Try captions from youtube-transcript-api
        2. Fall back to Whisper API (if enabled and OpenAI key provided)
        3. Fall back to Claude transcription (if enabled)

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript text

        Raises:
            Exception: If all strategies fail
        """
        logger.info(f"Starting transcript extraction for {video_id}")

        # Strategy 1: Try captions
        logger.debug("Attempting captions extraction...")
        captions = self.extract_captions(video_id)
        if captions:
            return captions

        logger.debug("Captions not available, trying fallback strategies...")

        # Strategy 2: Whisper API (if enabled)
        if self.config.enable_whisper_fallback and self.openai_api_key:
            logger.debug("Attempting Whisper API...")
            try:
                transcript = self._transcribe_with_whisper(video_id)
                if transcript:
                    return transcript
            except Exception as e:
                logger.warning(f"Whisper transcription failed: {e}")

        # Strategy 3: Claude transcription (if enabled)
        if self.config.enable_claude_transcription:
            logger.debug("Attempting Claude transcription...")
            try:
                transcript = self._transcribe_with_claude(video_id)
                if transcript:
                    return transcript
            except Exception as e:
                logger.warning(f"Claude transcription failed: {e}")

        raise Exception(f"All transcription strategies failed for {video_id}")

    def _transcribe_with_whisper(self, video_id: str) -> Optional[str]:
        """Transcribe using OpenAI Whisper API.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript or None if failed
        """
        # TODO: Implement Whisper transcription
        # 1. Download audio using yt-dlp
        # 2. Upload to Whisper API
        # 3. Return transcription
        raise NotImplementedError("Whisper transcription not yet implemented")

    def _transcribe_with_claude(self, video_id: str) -> Optional[str]:
        """Transcribe using Claude vision/audio capabilities.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript or None if failed
        """
        # TODO: Implement Claude transcription
        # 1. Download audio/video using yt-dlp
        # 2. Send to Claude API for transcription
        # 3. Return transcription
        raise NotImplementedError("Claude transcription not yet implemented")

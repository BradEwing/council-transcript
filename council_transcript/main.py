"""Main pipeline orchestrator."""

import logging
import re
from datetime import datetime
from pathlib import Path

from council_transcript.config import get_settings
from council_transcript.transcription import TranscriptExtractor
from council_transcript.youtube_extractor import get_video_info

logger = logging.getLogger(__name__)


class TranscriptPipeline:
    """Orchestrator for transcript extraction and local saving."""

    def __init__(self, config=None):
        """Initialize the pipeline.

        Args:
            config: Settings object (uses get_settings() if not provided)
        """
        self.config = config or get_settings()
        self._setup_logging()
        self.extractor = TranscriptExtractor(self.config)

    def _setup_logging(self):
        """Configure logging."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=self.config.log_level,
            format=log_format,
        )

    def _validate_transcript(self, transcript: str, video_id: str) -> None:
        """Raise ValueError if transcript content is empty or placeholder-only.

        Args:
            transcript: Transcript text to validate
            video_id: Used in error messages
        """
        stripped = transcript.strip()
        if not stripped:
            raise ValueError(f"Transcript for {video_id} is empty")
        # Reject transcripts that are only bracket-enclosed tokens like [Music] [Applause]
        non_bracket_content = re.sub(r'\[[^\]]*\]', '', stripped).strip()
        if not non_bracket_content:
            raise ValueError(
                f"Transcript for {video_id} contains only placeholder tokens "
                f"(e.g., [Music], [Applause]) and no real content"
            )

    def process_youtube_url(self, url: str) -> dict:
        """Process a YouTube URL and save transcript.

        Args:
            url: YouTube video/stream URL

        Returns:
            dict with keys:
            - video_id: str
            - title: str
            - transcript: str
            - transcript_file: str (path to saved transcript)
            - is_live: bool
            - is_upcoming: bool
        """
        logger.info(f"Processing YouTube URL: {url}")

        # Extract video ID and get info
        video_info = get_video_info(url)
        video_id = video_info["video_id"]
        logger.info(f"Video: {video_info['title']} (ID: {video_id})")

        # Check if live/upcoming
        if video_info["is_live"]:
            logger.warning("Video is currently live. Waiting for VOD or stream end...")
            raise NotImplementedError("Live stream handling not yet implemented")

        if video_info["is_upcoming"]:
            logger.warning("Video is upcoming. Cannot process yet.")
            raise ValueError("Cannot process upcoming streams")

        # Extract transcript
        logger.info("Extracting transcript...")
        transcript = self.extractor.extract_transcript(video_id)
        logger.info(f"Transcript extracted ({len(transcript)} characters)")

        # Validate transcript content
        self._validate_transcript(transcript, video_id)

        # Unload Whisper model to free memory
        self.extractor.unload_model()

        # Save transcript
        transcript_file = self._save_transcript(transcript, video_id)
        logger.info(f"Transcript saved to {transcript_file}")

        return {
            "video_id": video_id,
            "title": video_info["title"],
            "transcript": transcript,
            "transcript_file": str(transcript_file),
            "is_live": video_info["is_live"],
            "is_upcoming": video_info["is_upcoming"],
        }

    def _save_transcript(self, transcript: str, video_id: str) -> Path:
        """Save transcript with date and video ID in filename.

        Args:
            transcript: Transcript text to save
            video_id: YouTube video ID (ensures unique filenames)

        Returns:
            Path to saved file

        Raises:
            FileExistsError: If transcript already exists for this video today
        """
        date_str = datetime.now().strftime("%Y_%m_%d")
        filename = f"{date_str}_{video_id}.txt"
        filepath = self.config.transcripts_dir / filename

        if filepath.exists():
            raise FileExistsError(
                f"Transcript already exists for {video_id} on this date: {filepath}. "
                "Delete the file to reprocess."
            )

        filepath.write_text(transcript, encoding="utf-8")
        return filepath


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m council_transcript.main <YouTube_URL>")
        sys.exit(1)

    url = sys.argv[1]
    pipeline = TranscriptPipeline()

    try:
        result = pipeline.process_youtube_url(url)
        print("\n=== Results ===")
        print(f"Title: {result['title']}")
        print(f"Transcript saved to: {result['transcript_file']}")
        print(f"\n--- Transcript ({len(result['transcript'])} chars) ---")
        print(result["transcript"][:500] + "..." if len(result["transcript"]) > 500 else result["transcript"])
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()

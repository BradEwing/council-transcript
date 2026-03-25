"""Main pipeline orchestrator."""

import logging
from datetime import datetime
from pathlib import Path

from council_transcript.config import get_settings
from council_transcript.transcription import TranscriptExtractor
from council_transcript.youtube_extractor import extract_video_id, get_video_info

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
        video_id = extract_video_id(url)
        video_info = get_video_info(url)
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

        # Save transcript
        transcript_file = self._save_transcript(transcript)
        logger.info(f"Transcript saved to {transcript_file}")

        return {
            "video_id": video_id,
            "title": video_info["title"],
            "transcript": transcript,
            "transcript_file": str(transcript_file),
            "is_live": video_info["is_live"],
            "is_upcoming": video_info["is_upcoming"],
        }

    def _save_transcript(self, transcript: str) -> Path:
        """Save transcript with YYYY_MM_DD filename.

        Args:
            transcript: Transcript text to save

        Returns:
            Path to saved file
        """
        date_str = datetime.now().strftime("%Y_%m_%d")
        filename = f"{date_str}.txt"
        filepath = self.config.transcripts_dir / filename

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

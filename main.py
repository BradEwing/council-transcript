"""Main pipeline orchestrator."""

import logging
from typing import Optional

from council_transcript.config import get_settings
from council_transcript.llm_pipeline import LLMPipeline
from council_transcript.transcription import TranscriptExtractor
from council_transcript.youtube_extractor import extract_video_id, get_video_info

logger = logging.getLogger(__name__)


class TranscriptPipeline:
    """Main orchestrator for the transcript extraction and LLM pipeline."""

    def __init__(self, config=None):
        """Initialize the pipeline.

        Args:
            config: Settings object (uses get_settings() if not provided)
        """
        self.config = config or get_settings()
        self._setup_logging()

        self.extractor = TranscriptExtractor(self.config)
        self.llm = LLMPipeline(self.config)

    def _setup_logging(self):
        """Configure logging."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=self.config.log_level,
            format=log_format,
        )

    def process_youtube_url(
        self,
        url: str,
        operations: Optional[list] = None,
    ) -> dict:
        """Process a YouTube URL end-to-end.

        Args:
            url: YouTube video/stream URL
            operations: List of operations to perform. Options:
                       ['summarize', 'key_points', 'action_items']
                       Defaults to all operations.

        Returns:
            dict with keys:
            - video_id: str
            - title: str
            - transcript: str
            - results: dict with operation results
            - is_live: bool
            - is_upcoming: bool
        """
        if operations is None:
            operations = ["summarize", "key_points", "action_items"]

        logger.info(f"Processing YouTube URL: {url}")

        # Extract video ID and get info
        video_id = extract_video_id(url)
        video_info = get_video_info(url)
        logger.info(f"Video: {video_info['title']} (ID: {video_id})")

        # Check if live/upcoming
        if video_info["is_live"]:
            logger.warning("Video is currently live. Waiting for VOD or stream end...")
            # TODO: Implement live stream monitoring
            raise NotImplementedError("Live stream handling not yet implemented")

        if video_info["is_upcoming"]:
            logger.warning("Video is upcoming. Cannot process yet.")
            raise ValueError("Cannot process upcoming streams")

        # Extract transcript
        logger.info("Extracting transcript...")
        transcript = self.extractor.extract_transcript(video_id)
        logger.info(f"Transcript extracted ({len(transcript)} characters)")

        # Process with LLM
        results = {}
        for op in operations:
            logger.info(f"Performing operation: {op}")
            if op == "summarize":
                results["summary"] = self.llm.summarize(transcript)
            elif op == "key_points":
                results["key_points"] = self.llm.extract_key_points(transcript)
            elif op == "action_items":
                results["action_items"] = self.llm.extract_action_items(transcript)
            else:
                logger.warning(f"Unknown operation: {op}")

        logger.info("Processing complete")

        return {
            "video_id": video_id,
            "title": video_info["title"],
            "transcript": transcript,
            "results": results,
            "is_live": video_info["is_live"],
            "is_upcoming": video_info["is_upcoming"],
        }


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m council_transcript.main <YouTube_URL> [operations]")
        print("Operations: summarize, key_points, action_items")
        sys.exit(1)

    url = sys.argv[1]
    operations = sys.argv[2:] if len(sys.argv) > 2 else None

    pipeline = TranscriptPipeline()

    try:
        result = pipeline.process_youtube_url(url, operations)
        print("\n=== Results ===")
        print(f"Title: {result['title']}")
        print(f"\n--- Transcript ({len(result['transcript'])} chars) ---")
        print(result["transcript"][:500] + "..." if len(result["transcript"]) > 500 else result["transcript"])
        print(f"\n--- LLM Analysis ---")
        for op, content in result["results"].items():
            print(f"\n{op.upper()}:")
            print(content)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()

"""LLM pipeline for processing transcripts."""

import logging
from typing import Optional

from anthropic import Anthropic

logger = logging.getLogger(__name__)


class LLMPipeline:
    """Process transcripts with Claude LLM."""

    def __init__(self, config):
        """Initialize the LLM pipeline.

        Args:
            config: Settings object with API keys and model configuration
        """
        self.config = config
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.model = config.llm_model
        self.temperature = config.temperature

    def process_transcript(
        self,
        transcript: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Process a transcript with Claude.

        Args:
            transcript: The transcript text
            prompt: User prompt for processing
            system_prompt: Optional system prompt to set context
            max_tokens: Maximum tokens in response

        Returns:
            LLM response text
        """
        messages = [
            {
                "role": "user",
                "content": f"Transcript:\n\n{transcript}\n\n---\n\n{prompt}",
            }
        ]

        logger.info(f"Sending transcript to {self.model} for processing")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system_prompt or "You are a helpful assistant that analyzes transcripts.",
            messages=messages,
        )

        return response.content[0].text

    def summarize(self, transcript: str) -> str:
        """Summarize a transcript.

        Args:
            transcript: The transcript text

        Returns:
            Summary text
        """
        prompt = "Please provide a concise summary of this transcript in 3-5 sentences."
        return self.process_transcript(transcript, prompt)

    def extract_key_points(self, transcript: str) -> str:
        """Extract key points from a transcript.

        Args:
            transcript: The transcript text

        Returns:
            List of key points
        """
        prompt = """Extract the key points from this transcript.
        Format as a numbered list with brief explanations."""
        return self.process_transcript(transcript, prompt)

    def extract_action_items(self, transcript: str) -> str:
        """Extract action items from a transcript.

        Args:
            transcript: The transcript text

        Returns:
            List of action items
        """
        prompt = """Extract any action items, decisions, or next steps mentioned in this transcript.
        Format as a bulleted list."""
        return self.process_transcript(transcript, prompt)

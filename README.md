# Council Transcript

A Python pipeline for extracting transcripts from YouTube videos and live streams, with LLM-powered processing.

## Features

- **Multi-strategy transcript extraction**:
  1. YouTube captions (youtube-transcript-api)
  2. Whisper API fallback (optional)
  3. Claude transcription fallback
- **Live stream support** - detects and waits for VOD
- **LLM processing** - summarize, extract key points, and identify action items
- **Configurable** via environment variables

## Installation

1. Clone/create the project directory
2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   ```
   ```
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here  # optional, for Whisper
   ```

## Usage

### Command Line

```bash
# Basic: just get the transcript
python -m council_transcript.main "https://www.youtube.com/watch?v=VIDEO_ID"

# With specific operations
python -m council_transcript.main "https://www.youtube.com/watch?v=VIDEO_ID" summarize key_points
```

### Python API

```python
from council_transcript.main import TranscriptPipeline

pipeline = TranscriptPipeline()

result = pipeline.process_youtube_url(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    operations=["summarize", "key_points", "action_items"]
)

print(result["title"])
print(result["transcript"])
print(result["results"]["summary"])
```

## Project Structure

```
council-transcript/
├── council_transcript/
│   ├── __init__.py
│   ├── config.py              # Settings and configuration
│   ├── youtube_extractor.py   # YouTube video/stream utilities
│   ├── transcription.py       # Transcript extraction with fallbacks
│   ├── llm_pipeline.py        # LLM processing
│   └── main.py                # Main orchestrator
├── tests/                      # Test suite (to be added)
├── .env.example               # Environment template
├── .gitignore
├── pyproject.toml             # Project metadata and dependencies
└── README.md
```

## Configuration

Settings are loaded from environment variables (see `.env.example`):

- `ANTHROPIC_API_KEY` - Claude API key (required)
- `OPENAI_API_KEY` - OpenAI API key (optional, for Whisper)
- `LLM_MODEL` - Model to use (default: claude-opus-4-6)
- `TEMPERATURE` - Model temperature (default: 0.7)
- `ENABLE_WHISPER_FALLBACK` - Use Whisper if captions fail (default: false)
- `ENABLE_CLAUDE_TRANSCRIPTION` - Use Claude for transcription (default: true)
- `TEMP_DIR` - Temporary files directory (default: ./tmp)
- `LOG_LEVEL` - Logging level (default: INFO)

## Roadmap

- [ ] Whisper API integration for audio transcription
- [ ] Claude audio/video processing for transcription
- [ ] Live stream monitoring and VOD detection
- [ ] Batch processing for multiple videos
- [ ] Output formatting (Markdown, JSON, etc.)
- [ ] Caching of transcripts
- [ ] Test suite
- [ ] CLI improvements

## License

MIT

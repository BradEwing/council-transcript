# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Council Transcript** extracts and processes transcripts from YouTube videos of Santa Monica council meetings for analysis. It uses a two-strategy approach:
1. **YouTube captions** (via youtube-transcript-api) — fast and preferred
2. **Whisper audio transcription** (local, no API keys) — fallback when captions unavailable

Transcripts are automatically saved to `./transcripts/` with the format `YYYY_MM_DD_VIDEO_ID.txt`.

## Common Commands

### Setup & Installation
```bash
# Install dependencies (creates editable install)
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running
```bash
# Extract transcript from a YouTube URL
python -m council_transcript.main "https://www.youtube.com/watch?v=VIDEO_ID"

# Using Python API
python -c "
from council_transcript.main import TranscriptPipeline
result = TranscriptPipeline().process_youtube_url('https://www.youtube.com/watch?v=VIDEO_ID')
print(result['transcript'])
"
```

### Development & Code Quality
```bash
# Format code
black council_transcript/

# Lint with ruff
ruff check council_transcript/

# Type checking
mypy council_transcript/

# Run tests
pytest

# Run a specific test
pytest tests/test_file.py::test_function_name -v
```

### Configuration
Settings are loaded from environment variables (or `.env` file):
```bash
TEMP_DIR=./tmp                    # Temporary files (default: ./tmp)
TRANSCRIPTS_DIR=./transcripts     # Output directory (default: ./transcripts)
LOGS_DIR=./logs                   # Logs directory (default: ./logs)
LOG_LEVEL=INFO                    # Logging level (default: INFO)
WHISPER_MODEL_SIZE=base           # Whisper model: tiny, base, small, medium, large (default: base)
```

## Architecture & Data Flow

### Pipeline Orchestration (`main.py`)

**TranscriptPipeline** is the main orchestrator:
1. Takes a YouTube URL via CLI or programmatically
2. Calls `get_video_info()` to extract metadata and check if video is live/upcoming
3. Validates the video state (rejects live/upcoming)
4. Delegates to **TranscriptExtractor** to get the transcript
5. **Validates transcript content** — rejects empty transcripts or those with only bracket tokens like `[Music]` or `[Applause]`
6. Saves transcript to `./transcripts/YYYY_MM_DD_VIDEO_ID.txt`
7. Unloads the Whisper model from memory to free resources
8. Returns a result dict with: `video_id`, `title`, `transcript`, `transcript_file`, `is_live`, `is_upcoming`

### Transcript Extraction (`transcription.py`)

**TranscriptExtractor** implements the extraction strategy:
- **Primary strategy**: `extract_captions()` — uses YouTubeTranscriptApi to fetch captions, supports language fallback (defaults to 'en', 'en-US')
- **Fallback strategy**: `_transcribe_with_whisper()` — downloads audio via yt-dlp, transcribes with local Whisper model
  - Whisper model is **lazily loaded** on first use (not instantiated at init) to save memory
  - Always cleans up the audio file after transcription
- `extract_transcript()` — tries captions first, falls back to Whisper if captions unavailable

### URL & Metadata Extraction (`youtube_extractor.py`)

Utilities for working with YouTube URLs:
- **`extract_video_id()`** — parses various YouTube URL formats (full URL, short URL, or raw video ID)
- **`get_video_info()`** — uses yt-dlp to fetch video metadata (title, duration, live/upcoming status)
- **`is_live_stream()`, `is_upcoming_stream()`** — convenience functions for checking stream status

### Configuration (`config.py`)

**Settings** class (Pydantic) manages configuration:
- Reads from environment variables (or `.env` file)
- Auto-creates required directories (`temp_dir`, `transcripts_dir`, `logs_dir`) on init
- Singleton pattern via `get_settings()` to cache configuration

## Key Design Patterns

**Lazy Loading**: Whisper model is instantiated only when captions aren't available. After use, it's explicitly unloaded from memory via `extractor.unload_model()` to prevent memory bloat for multiple extractions.

**Validation**: Transcripts are validated for meaningful content. Empty transcripts or those containing only placeholder tokens (e.g., `[Music]`, `[Applause]`) are rejected with clear error messages.

**File Safety**: Transcript filenames include date and video ID to ensure uniqueness. The pipeline raises `FileExistsError` if a transcript already exists for the same video on the same day.

**Error Handling**: The extraction strategy gracefully falls back from captions to audio transcription. Live/upcoming streams are explicitly rejected with informative errors.

## Dependencies & External Tools

- **youtube-transcript-api** — Fetch YouTube captions
- **yt-dlp** — Download YouTube audio and extract metadata
- **openai-whisper** — Local audio transcription (no API key needed)
- **Pydantic** — Configuration validation
- **FFmpeg** — Required externally for audio processing (install via `brew install ffmpeg` on macOS)

Development dependencies: `pytest`, `black`, `ruff`, `mypy`, `pytest-asyncio`

## Notes for Future Development

The README lists upcoming features:
- Batch processing for multiple videos
- Additional output formats (JSON, SRT)
- Transcript caching
- Web UI

The pipeline is currently designed for single-video processing. Batch processing would require minimal changes (loop over URLs, handle file collision).

Live stream handling is explicitly not yet implemented (`NotImplementedError` is raised).

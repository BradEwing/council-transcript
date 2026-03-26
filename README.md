# Council Transcript

A Python pipeline for extracting and summarizing transcripts from Santa Monica council YouTube videos, with automatic audio transcription fallback.

## Features

- **Multi-strategy transcript extraction**:
  1. YouTube captions (youtube-transcript-api)
  2. **Local Whisper audio transcription** - runs locally, no API keys needed
- **Automatic saving** - transcripts saved to `./transcripts/YYYY_MM_DD.txt`

## Installation

1. Clone/create the project directory
2. Install FFmpeg (required for audio processing):
   ```bash
   # macOS
   brew install ffmpeg

   # Linux
   sudo apt-get install ffmpeg

   # Windows
   choco install ffmpeg
   ```

3. Install Python dependencies:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line

```bash
python -m council_transcript.main "https://www.youtube.com/watch?v=VIDEO_ID"
```

The transcript will be saved to `./transcripts/YYYY_MM_DD.txt` with today's date.

### Example

```bash
python -m council_transcript.main "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Output:
```
=== Results ===
Title: Rick Astley - Never Gonna Give You Up
Transcript saved to: ./transcripts/2026_03_25.txt

--- Transcript (5234 chars) ---
Never gonna give you up, never gonna let you down...
```


## Project Structure

```
council-transcript/
├── council_transcript/
│   ├── __init__.py
│   ├── config.py              # Settings and configuration
│   ├── youtube_extractor.py   # YouTube video/stream utilities
│   ├── transcription.py       # Transcript extraction (captions + Whisper)
│   └── main.py                # Main orchestrator and CLI
├── transcripts/               # Output directory (auto-created)
├── pyproject.toml             # Project metadata and dependencies
└── README.md
```

## Configuration

All configuration is done via environment variables in `.env`:

- `SMF_TEMP_DIR` - Temporary files directory (default: `./tmp`)
- `SMF_TRANSCRIPTS_DIR` - Output directory for transcripts (default: `./transcripts`)
- `SMF_LOGS_DIR` - Logs directory (default: `./logs`)
- `SMF_LOG_LEVEL` - Logging level (default: `INFO`)

## License

MIT

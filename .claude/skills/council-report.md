---
name: council-report
description: Generate comprehensive council meeting report with transcription and analysis
type: skill
---

# /council-report

Generate a comprehensive council meeting report with transcription and analysis.

## Usage

```
/council-report <YouTube_URL>
```

## What it does

1. **Extracts transcript** from the YouTube video using youtube-transcript-api or Whisper audio transcription
2. **Saves transcript** to `transcripts/YYYY_MM_DD_VIDEO_ID.txt`
3. **Runs SMF perspective analysis** using the smf-perspective agent
4. **Runs staff report analysis** using the staff-report-reviewer agent
5. **Compiles results** into a comprehensive report in `reports/DATE_REPORT.md`

## Example

```
/council-report https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Implementation Notes

This is implemented as a two-phase workflow:

### Phase 1: Transcript Extraction
Run the transcript extraction script:
```bash
python scripts/council_report.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This extracts the transcript and saves it to the transcripts directory.

### Phase 2: Agent Analysis
Once the transcript is extracted, the smf-perspective and staff-report-reviewer agents analyze it:

1. **SMF Perspective**: Analyzes through the lens of Santa Monica Forward priorities
   - Housing affordability
   - Tenant rights
   - Public safety
   - Economic vitality
   - Transit/mobility
   - Environmental sustainability
   - Community engagement

2. **Staff Report Review**: Compares council discussion with official staff reports
   - Identifies recommendations
   - Notes deviations
   - Documents conditions and amendments
   - Flags out-of-scope concerns

### Phase 3: Report Compilation
Results are compiled into `reports/YYYY_MM_DD_REPORT.md` with:
- Executive summary
- SMF perspective findings
- Staff report analysis
- Full transcript reference

## Configuration

Environment variables (optional, from `.env` or settings):
```bash
SMF_TRANSCRIPTS_DIR=./transcripts    # Where transcripts are saved
SMF_REPORTS_DIR=./reports             # Where reports are compiled
```

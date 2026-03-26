---
name: council-report
description: Generate comprehensive council meeting report with transcription and analysis
type: skill
---

# /council-report

Generate a comprehensive council meeting report with transcription and analysis.

## Usage

```bash
python3 scripts/council_report.py "<YouTube_URL>"
```

## What it does

1. **Extracts transcript** from the YouTube video (via captions or Whisper audio transcription)
2. **Saves transcript** to `transcripts/YYYY_MM_DD_VIDEO_ID.txt`
3. **Displays transcript** in console for copying to agents
4. **Guides agent analysis** — run `/smf-perspective` and `/staff-report-reviewer` agents in Claude Code
5. **Compiles results** into comprehensive report in `reports/YYYY_MM_DD_REPORT.md`

## Example

```bash
python3 scripts/council_report.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Important: Timeouts

Transcript extraction can take a very long time, especially when Whisper fallback is needed for multi-hour council meetings. **The transcript extraction command MUST be run in background mode** (`run_in_background: true`) since it can easily exceed 15 minutes when Whisper transcription is required. Do NOT use a foreground bash command for transcript extraction — it will time out.

## Implementation Notes

This is a three-phase workflow:

### Phase 1: Transcript Extraction & Display

Run the main script **in background mode** (it can take 15+ minutes for Whisper fallback):
```bash
python3 scripts/council_report.py "https://www.youtube.com/watch?v=VIDEO_ID"
```
Use `run_in_background: true` on the Bash tool. You will be notified when it completes. Then read the output file and the transcript file from `transcripts/`.

The script will:
- Extract transcript via YouTube captions (fast) or Whisper (fallback)
- Save to `transcripts/YYYY_MM_DD_VIDEO_ID.txt`
- Display the full transcript in console
- Show next steps and where to save analysis files

### Phase 2: Agent Analysis

In Claude Code, create new messages to run the analysis agents. The script provides instructions and the transcript text.

1. **SMF Perspective** — Run in Claude Code:
   ```
   /smf-perspective

   [paste transcript from console output]
   ```

   Analyzes through Santa Monica Forward's lens:
   - Housing affordability & tenant rights
   - Public safety & economic vitality
   - Transit/mobility & environmental sustainability
   - Community engagement

   Save output to the suggested file name.

2. **Staff Report Review** — Run in Claude Code:
   ```
   /staff-report-reviewer

   [paste transcript from console output]
   ```

   Compares council discussion with official staff reports:
   - Identifies staff recommendations
   - Notes where council deviated
   - Documents conditions & amendments
   - Flags out-of-scope concerns

   Save output to the suggested file name.

### Phase 3: Report Compilation

Once both analyses are saved, compile them:
```bash
python3 scripts/compile_report.py transcripts/YYYY_MM_DD_VIDEO_ID.txt \
  reports/YYYY_MM_DD_SMF_ANALYSIS.md \
  reports/YYYY_MM_DD_STAFF_ANALYSIS.md
```

This creates `reports/YYYY_MM_DD_REPORT.md` with:
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

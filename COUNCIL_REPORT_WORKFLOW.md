# Council Report Workflow

This document describes how to generate comprehensive council meeting reports using the `council-report` skill/workflow.

## Quick Start

```bash
# Step 1: Extract transcript
python scripts/council_report.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Step 2: Get the transcript filename from transcripts/ directory
ls -lt transcripts/ | head -1

# Step 3: Copy transcript text for agent analysis (Claude Code UI)
cat transcripts/YYYY_MM_DD_VIDEO_ID.txt

# Step 4: Run agent analyses (in Claude Code, in new messages)
# - Use /smf-perspective agent with transcript content
# - Use /staff-report-reviewer agent with transcript content
# - Save outputs to files (e.g., smf_analysis.md, staff_analysis.md)

# Step 5: Compile final report
python scripts/compile_report.py transcripts/YYYY_MM_DD_VIDEO_ID.txt [smf_analysis.md] [staff_report.md]
```

## Detailed Workflow

### Phase 1: Transcript Extraction

**Command:**
```bash
python scripts/council_report.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**What happens:**
1. Downloads the YouTube video
2. Attempts to fetch captions (fast, preferred)
3. Falls back to Whisper audio transcription if captions unavailable
4. Validates transcript content (rejects empty or placeholder-only transcripts)
5. Saves transcript to `transcripts/YYYY_MM_DD_VIDEO_ID.txt`

**Example:**
```bash
$ python scripts/council_report.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

📝 Extracting transcript from https://www.youtube.com/watch?v=dQw4w9WgXcQ...

✅ Transcript extraction complete!

📄 Next steps:
1. Use /smf-perspective agent to analyze from Santa Monica Forward priorities
2. Use /staff-report-reviewer agent to compare with official staff reports
3. Results will be compiled into: reports/2026_03_25_REPORT.md
```

### Phase 2: Agent Analysis

Once the transcript is extracted, run the analysis agents within Claude Code:

#### Option A: Use agents directly (recommended)

**In Claude Code, create a new message and invoke agents:**

1. **SMF Perspective Analysis**
   ```
   /smf-perspective

   [paste or reference the transcript content]
   ```

2. **Staff Report Analysis**
   ```
   /staff-report-reviewer

   [paste or reference the transcript content]
   ```

The agents will provide comprehensive analyses that you can copy/save.

#### Option B: Provide full transcript context

If you want deeper analysis, provide:
- Full transcript content
- Video title and date
- Link to the video
- Any specific questions or focus areas

### Phase 3: Report Compilation

Once you have analyses from the agents, compile them into a final report:

```bash
python scripts/compile_report.py \
  transcripts/2026_03_25_VIDEO_ID.txt \
  smf_analysis.txt \
  staff_analysis.txt
```

This creates `reports/2026_03_25_REPORT.md` with:
- Executive summary
- SMF perspective findings
- Staff report analysis comparison
- Full transcript for reference

## File Organization

```
council-transcript/
├── transcripts/              # Extracted transcripts
│   ├── 2026_03_25_dQw4w9WgXcQ.txt
│   └── ...
├── reports/                  # Compiled reports
│   ├── 2026_03_25_REPORT.md
│   └── ...
└── scripts/
    ├── council_report.py     # Transcript extraction
    └── compile_report.py     # Report compilation
```

## Configuration

The workflow uses environment variables from `.env` or settings:

```bash
SMF_TRANSCRIPTS_DIR=./transcripts    # Where transcripts are saved (default: ./transcripts)
SMF_REPORTS_DIR=./reports             # Where reports are compiled (default: ./reports)
SMF_WHISPER_MODEL_SIZE=base           # Whisper model size: tiny, base, small, medium, large
```

## Agent Details

### SMF Perspective Agent (`/smf-perspective`)

Analyzes the transcript through the lens of **Santa Monica Forward's** priorities:

- **Housing Affordability** - Housing costs, affordability programs, development policies
- **Tenant Rights** - Rent control, eviction protections, tenant protections
- **Public Safety** - Safety initiatives, community policing, public response
- **Economic Vitality** - Business development, economic growth, job creation
- **Transit/Mobility** - Transportation, parking, mobility solutions
- **Environmental Sustainability** - Climate action, green initiatives, sustainability
- **Community Engagement** - Public participation, community feedback, outreach

**Output includes:**
- Key discussions relevant to SMF priorities
- Proposals and decisions that affect these areas
- Notable gaps or missed opportunities
- Recommendations for SMF engagement

### Staff Report Reviewer Agent (`/staff-report-reviewer`)

Compares council discussion with official staff reports:

- Fetches matching staff reports from Santa Monica city clerk
- Compares staff recommendations with actual council discussion
- Documents conditions and amendments added during meeting
- Identifies deviations from staff recommendations
- Flags out-of-scope concerns that were raised

**Output includes:**
- Summary of staff recommendations
- Actual council decisions made
- Deviations and their implications
- Conditions, amendments, and side discussions
- Analysis of how council diverged from staff guidance

## Tips & Tricks

### Reusing Transcripts

If you've already extracted a transcript and want to analyze it again:

```bash
# Find the transcript file
ls -lt transcripts/ | head -5

# Copy its content and paste into agent
cat transcripts/2026_03_25_VIDEO_ID.txt
```

### Generating Multiple Reports

The workflow supports multiple reports per day. Each run increments a counter:
- First report: `2026_03_25_REPORT.md`
- Second report: `2026_03_25_REPORT_1.md`
- Third report: `2026_03_25_REPORT_2.md`

### Batch Processing

To process multiple videos:

```bash
for url in \
  "https://www.youtube.com/watch?v=VIDEO_1" \
  "https://www.youtube.com/watch?v=VIDEO_2"
do
  python scripts/council_report.py "$url"
done
```

### Customizing Reports

Edit `scripts/compile_report.py` to customize:
- Report formatting
- Section ordering
- Additional metadata
- Output location

## Troubleshooting

### Transcript extraction fails

**"Video is currently live"** - Wait for the live stream to end, then process

**"Cannot process upcoming streams"** - Video hasn't aired yet, try again after broadcast

**"Transcript is empty"** - No captions available and audio transcription failed
- Ensure FFmpeg is installed: `brew install ffmpeg`
- Try increasing `SMF_WHISPER_MODEL_SIZE` (but slower)

### Agent analysis not as expected

**Vague or generic results** - Provide more context to agents:
- Full transcript (not just excerpt)
- Video date and meeting context
- Specific questions or areas of interest

**Missing staff report analysis** - Staff reports may not yet be published
- Check Santa Monica city clerk website manually
- Agent will note if reports are unavailable

### Report compilation issues

**"Transcript file not found"** - Check spelling and path
```bash
ls transcripts/  # List all available transcripts
```

## Integration with Claude Code

This workflow is designed to work seamlessly within Claude Code:

1. **Extraction:** `python scripts/council_report.py <url>`
2. **Analysis:** Run `/smf-perspective` and `/staff-report-reviewer` agents
3. **Compilation:** `python scripts/compile_report.py <transcript> <analyses>`

All commands run in your project directory with proper environment setup.

## Next Steps

- [ ] Extract transcript from council video
- [ ] Run SMF perspective analysis
- [ ] Run staff report reviewer analysis
- [ ] Compile comprehensive report
- [ ] Review and share findings

## Support

For issues with:
- **Transcript extraction** - Check FFmpeg installation, video availability
- **Agent analysis** - Provide full context, specific questions
- **Report format** - Customize `compile_report.py`
- **Workflow integration** - See CLAUDE.md for project setup

---

**Last updated:** 2026-03-25

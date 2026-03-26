#!/usr/bin/env python3
"""Extract transcript and orchestrate council report analysis."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for council_transcript imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from council_transcript.config import get_settings
from council_transcript.youtube_extractor import extract_video_id


def extract_transcript(url: str) -> dict:
    """Extract transcript from YouTube URL.

    Returns:
        dict with keys: transcript_file, video_id, transcript_text
    """
    try:
        subprocess.run(
            ["python3", "-m", "council_transcript.main", url],
            capture_output=True,
            text=True,
            check=True
        )

        # Find the transcript file that was just created
        settings = get_settings()
        # List transcripts, find the most recently modified
        transcripts = sorted(
            settings.transcripts_dir.glob("*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not transcripts:
            raise RuntimeError("Transcript extraction succeeded but file not found")

        transcript_file = transcripts[0]
        transcript_text = transcript_file.read_text(encoding='utf-8')
        video_id = extract_video_id(url)

        return {
            "transcript_file": transcript_file,
            "video_id": video_id,
            "transcript_text": transcript_text,
        }

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Transcript extraction failed:")
        if e.stderr:
            print(f"\n{e.stderr}")
        raise RuntimeError("Failed to extract transcript") from e


def save_analysis_templates(transcript_file: Path) -> dict:
    """Create template files for agent analyses.

    Returns:
        dict with keys: smf_template, staff_template
    """
    settings = get_settings()
    report_date = datetime.now().strftime("%Y_%m_%d")

    # Create analysis templates
    smf_template = settings.reports_dir / f"{report_date}_SMF_ANALYSIS.md"
    staff_template = settings.reports_dir / f"{report_date}_STAFF_ANALYSIS.md"

    # SMF analysis template
    smf_content = """# SMF Perspective Analysis

**Date:** {date}
**Transcript File:** {transcript}

## Summary
[Analysis of council discussion through Santa Monica Forward's priorities lens]

## Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

## Housing Affordability
[Relevant discussions and decisions]

## Tenant Rights
[Relevant discussions and decisions]

## Public Safety
[Relevant discussions and decisions]

## Economic Vitality
[Relevant discussions and decisions]

## Transit/Mobility
[Relevant discussions and decisions]

## Environmental Sustainability
[Relevant discussions and decisions]

## Community Engagement
[Relevant discussions and decisions]

## Recommendations
[Action items for SMF]
""".format(date=datetime.now().strftime("%Y-%m-%d"), transcript=transcript_file.name)

    # Staff report analysis template
    staff_content = """# Staff Report Review

**Date:** {date}
**Transcript File:** {transcript}

## Executive Summary
[Comparison of staff recommendations vs. actual council decisions]

## Staff Recommendations
[Summary of official staff report recommendations]

## Council Decisions
[What actually happened in the meeting]

## Deviations
[Where council diverged from staff guidance]

## Conditions & Amendments
[Any modifications made during discussion]

## Out-of-Scope Concerns
[Issues raised that weren't in staff reports]

## Analysis
[Overall assessment of how council handled staff recommendations]
""".format(date=datetime.now().strftime("%Y-%m-%d"), transcript=transcript_file.name)

    return {
        "smf_template": smf_template,
        "staff_template": staff_template,
        "smf_content": smf_content,
        "staff_content": staff_content,
    }


def print_workflow_instructions(transcript_file: Path, templates: dict) -> None:
    """Print instructions for completing the workflow."""
    print(f"""
✅ Transcript extracted successfully!
📄 Saved to: {transcript_file}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS: Run agent analyses (in Claude Code, in new messages)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  SMF Perspective Analysis

   In Claude Code, create a new message and run:

   /smf-perspective

   [paste the transcript content below]

   Save the output to: {templates['smf_template'].name}

2️⃣  Staff Report Review

   In Claude Code, create a new message and run:

   /staff-report-reviewer

   [paste the transcript content below]

   Save the output to: {templates['staff_template'].name}

3️⃣  Compile Final Report

   Once both analyses are saved, run:

   python scripts/compile_report.py {transcript_file} \\
     {templates['smf_template'].name} \\
     {templates['staff_template'].name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRANSCRIPT CONTENT (copy for agent analysis):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


def main():
    """Orchestrate the full council report workflow."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/council_report.py <YouTube_URL>")
        print("\nExample:")
        print('  python scripts/council_report.py "https://www.youtube.com/watch?v=VIDEO_ID"')
        sys.exit(1)

    url = sys.argv[1]

    print(f"\n📝 Extracting transcript from {url}...\n")

    try:
        # Phase 1: Extract transcript
        extraction = extract_transcript(url)
        transcript_file = extraction["transcript_file"]
        transcript_text = extraction["transcript_text"]

        # Phase 2: Create analysis templates
        templates = save_analysis_templates(transcript_file)

        # Phase 3: Print workflow instructions
        print_workflow_instructions(transcript_file, templates)
        print(transcript_text)
        print(f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main()

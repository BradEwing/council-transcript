#!/usr/bin/env python3
"""Compile council report from transcript and analyses."""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for council_transcript imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from council_transcript.config import get_settings


def main():
    """Compile report from transcript file and optional analysis files."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/compile_report.py <TRANSCRIPT_FILE> [smf_analysis_file] [staff_report_file]")
        print("\nThis script compiles analyses into a formatted report.")
        print("\nExample:")
        print('  python scripts/compile_report.py transcripts/2026_03_25_dQw4w9WgXcQ.txt')
        sys.exit(1)

    settings = get_settings()

    transcript_file = Path(sys.argv[1])
    smf_analysis_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    staff_analysis_file = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if not transcript_file.exists():
        print(f"❌ Transcript file not found: {transcript_file}")
        sys.exit(1)

    # Read transcript
    transcript = transcript_file.read_text(encoding='utf-8')

    # Read analyses if provided
    smf_analysis = ""
    if smf_analysis_file and smf_analysis_file.exists():
        smf_analysis = smf_analysis_file.read_text(encoding='utf-8')

    staff_analysis = ""
    if staff_analysis_file and staff_analysis_file.exists():
        staff_analysis = staff_analysis_file.read_text(encoding='utf-8')

    # Generate report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_date = datetime.now().strftime("%Y_%m_%d")

    report = f"""# Council Meeting Report

**Generated:** {timestamp}
**Transcript File:** {transcript_file.name}

## Executive Summary

This report documents a Santa Monica council meeting with comprehensive analysis from multiple perspectives.

---

## SMF Perspective Analysis

{smf_analysis if smf_analysis else "[No SMF analysis provided. Run the smf-perspective agent and save output to include here.]"}

---

## Staff Report Review

{staff_analysis if staff_analysis else "[No staff analysis provided. Run the staff-report-reviewer agent and save output to include here.]"}

---

## Full Transcript

**Transcript Length:** {len(transcript):,} characters

### Transcript Text

{transcript}

---

*Report compiled {timestamp}*
"""

    # Save report
    report_file = settings.reports_dir / f"{report_date}_REPORT.md"

    # Add counter if file exists
    counter = 1
    while report_file.exists():
        report_file = reports_dir / f"{report_date}_REPORT_{counter}.md"
        counter += 1

    report_file.write_text(report, encoding='utf-8')

    print(f"\n✅ Report compiled successfully!")
    print(f"📄 Report saved to: {report_file}")


if __name__ == "__main__":
    main()

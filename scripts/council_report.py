#!/usr/bin/env python3
"""Extract transcript and prepare for council report analysis."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Extract transcript from YouTube URL."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/council_report.py <YouTube_URL>")
        print("\nExample: python scripts/council_report.py 'https://www.youtube.com/watch?v=VIDEO_ID'")
        sys.exit(1)

    url = sys.argv[1]

    print(f"\n📝 Extracting transcript from {url}...\n")

    try:
        result = subprocess.run(
            ["python3", "-m", "council_transcript.main", url],
            check=True
        )

        # Get today's date for report filename
        report_date = datetime.now().strftime("%Y_%m_%d")
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        report_file = reports_dir / f"{report_date}_REPORT.md"

        print(f"\n✅ Transcript extraction complete!")
        print(f"\n📄 Next steps:")
        print(f"1. Use /smf-perspective agent to analyze from Santa Monica Forward priorities")
        print(f"2. Use /staff-report-reviewer agent to compare with official staff reports")
        print(f"3. Results will be compiled into: {report_file}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Transcript extraction failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

import json
from datetime import datetime, timezone
from pathlib import Path


REPORTS_DIR = Path("reports")


def generate_json_report(issues):
    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "total_issues": len(issues),

        "issues": issues,
    }

    report_file = REPORTS_DIR / "issues_report.json"

    with report_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
        )

    return report_file
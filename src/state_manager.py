import json
from pathlib import Path


STATE_FILE = Path("data/processed_issues.json")


def load_processed_issues():
    if not STATE_FILE.exists():
        return set()

    with STATE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data)


def save_processed_issues(processed_issues):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(sorted(processed_issues), file, indent=2)


def is_issue_processed(issue_number, processed_issues):
    return issue_number in processed_issues
def process_issue(issue):
    return {
        "number": issue["number"],
        "title": issue.get("title", ""),
        "state": issue.get("state", ""),
        "author": issue.get("user", {}).get("login", "unknown"),
        "comments": issue.get("comments", 0),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "url": issue.get("html_url", ""),
        "body": issue.get("body") or "",
    }
def classify_issue(issue):
    text = f"{issue['title']} {issue['body']}".lower()

    bug_keywords = [
        "bug",
        "error",
        "crash",
        "broken",
        "not working",
    ]

    if any(keyword in text for keyword in bug_keywords):
        return "bug"

    return "general"
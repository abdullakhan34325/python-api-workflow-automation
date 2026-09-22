from src.ai.ai_client import generate_issue_comment


title = "Login crashes when password is empty"

body = """
When I submit the login form without entering a password,
the application returns a 500 error instead of showing
a validation message.
"""

issue_type = "bug"


comment = generate_issue_comment(
    title=title,
    body=body,
    issue_type=issue_type,
)


print("\nGenerated AI comment:\n")
print(comment)
import os

from dotenv import load_dotenv
from google import genai

from src.exceptions import (
    AIAPIError,
    AIConfigurationError,
)


load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise AIConfigurationError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        return genai.Client(
            api_key=api_key
        )

    except Exception as error:
        raise AIConfigurationError(
            "Could not initialize the Gemini client."
        ) from error


def generate_issue_comment(
    title,
    body,
    issue_type,
):
    client = get_gemini_client()

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.7-flash",
    )

    prompt = f"""
You are assisting with GitHub issue triage.

Analyze the GitHub issue below and write a concise,
professional response that can be posted as a GitHub comment.

Issue type:
{issue_type}

Issue title:
{title}

Issue body:
{body}

Rules:

1. Use ONLY the information provided in the issue.
2. Do not claim that you inspected source code, logs,
   databases, servers, or other systems.
3. Do not invent technical details.
4. If the cause is uncertain, describe it as a possibility.
5. Suggest practical investigation steps when appropriate.
6. Keep the response professional and useful.
7. Keep it reasonably concise.
8. Return ONLY the GitHub comment text.
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

    except Exception as error:
        raise AIAPIError(
            "Gemini API request failed."
        ) from error

    text = response.text

    if not text:
        raise AIAPIError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    if not text:
        raise AIAPIError(
            "Gemini returned an empty comment."
        )

    if len(text) > 4000:
        raise AIAPIError(
            "Gemini generated a comment that is too long."
        )

    return text
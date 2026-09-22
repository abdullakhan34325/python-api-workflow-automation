import time

import requests

from src.exceptions import (
    GitHubAPIError,
    GitHubConnectionError,
)


MAX_RETRIES = 3
RETRY_DELAY = 2


def _make_request(
    method,
    url,
    headers,
    *,
    params=None,
    json=None,
):
    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                timeout=10,
            )

            response.raise_for_status()

            return response


        except requests.exceptions.Timeout as error:

            if attempt == MAX_RETRIES:
                raise GitHubConnectionError(
                    "GitHub API request timed out "
                    f"after {MAX_RETRIES} attempts."
                ) from error

            time.sleep(RETRY_DELAY)


        except requests.exceptions.ConnectionError as error:

            if attempt == MAX_RETRIES:
                raise GitHubConnectionError(
                    "Could not connect to GitHub API "
                    f"after {MAX_RETRIES} attempts."
                ) from error

            time.sleep(RETRY_DELAY)


        except requests.exceptions.HTTPError as error:

            status_code = response.status_code

            # Retry only temporary server/rate-limit errors.
            if (
                status_code in {429, 500, 502, 503, 504}
                and attempt < MAX_RETRIES
            ):

                time.sleep(RETRY_DELAY)

                continue


            raise GitHubAPIError(
                f"GitHub API returned HTTP {status_code}."
            ) from error

    raise GitHubAPIError(
        "GitHub API request failed."
    )


def get_repository_issues(owner, repository, token):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/issues"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }

    params = {
        "state": "all",
        "per_page": 5,
    }

    response = _make_request(
        "GET",
        url,
        headers,
        params=params,
    )

    return response.json()


def add_issue_comment(
    owner,
    repository,
    issue_number,
    token,
    comment,
):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/issues/"
        f"{issue_number}/comments"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "body": comment,
    }

    response = _make_request(
        "POST",
        url,
        headers,
        json=payload,
    )

    return response.json()
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.ai.ai_client import generate_issue_comment
from src.api.github_client import (
    add_issue_comment,
    get_repository_issues,
)
from src.exceptions import (
    AIAPIError,
    AIConfigurationError,
    ConfigurationError,
    GitHubAPIError,
    GitHubConnectionError,
)
from src.logger import setup_logger
from src.processors.issue_processor import (
    classify_issue,
    process_issue,
)
from src.report_generator import generate_json_report
from src.state_manager import (
    is_issue_processed,
    load_processed_issues,
    save_processed_issues,
)


def get_current_time():
    return datetime.now(
        timezone.utc
    ).isoformat()


def main():

    logger = setup_logger()

    logger.info(
        "Automation run started."
    )

    load_dotenv()

    repository = os.getenv(
        "GITHUB_REPOSITORY"
    )

    github_token = os.getenv(
        "GITHUB_TOKEN"
    )

    if not repository:
        raise ConfigurationError(
            "GITHUB_REPOSITORY is not configured."
        )

    if not github_token:
        raise ConfigurationError(
            "GITHUB_TOKEN is not configured."
        )

    if "/" not in repository:
        raise ConfigurationError(
            "GITHUB_REPOSITORY must use the "
            "format owner/repository."
        )

    owner, repository_name = repository.split(
        "/",
        1,
    )

    logger.info(
        f"Processing repository: "
        f"{owner}/{repository_name}"
    )

    # -------------------------------------------------
    # 1. Fetch GitHub issues
    # -------------------------------------------------

    try:

        issues = get_repository_issues(
            owner,
            repository_name,
            github_token,
        )

    except GitHubConnectionError as error:

        logger.error(
            f"Connection error: {error}"
        )

        return

    except GitHubAPIError as error:

        logger.error(
            f"GitHub API error: {error}"
        )

        return

    logger.info(
        f"Fetched {len(issues)} issues."
    )

    # -------------------------------------------------
    # 2. Load automation state
    # -------------------------------------------------

    processed_issues = (
        load_processed_issues()
    )

    processed_issue_data = []

    # -------------------------------------------------
    # 3. Process each issue
    # -------------------------------------------------

    for issue in issues:

        issue_data = process_issue(
            issue
        )

        issue_number = issue_data[
            "number"
        ]

        # ---------------------------------------------
        # Already processed
        # ---------------------------------------------

        if is_issue_processed(
            issue_number,
            processed_issues,
        ):

            logger.info(
                f"Issue #{issue_number} "
                f"already processed. Skipping."
            )

            issue_data["automation"] = {
                "status": "already_processed",
                "action": "none",
            }

            processed_issue_data.append(
                issue_data
            )

            continue

        # ---------------------------------------------
        # New issue
        # ---------------------------------------------

        issue_data[
            "detected_at"
        ] = get_current_time()

        issue_type = classify_issue(
            issue_data
        )

        issue_data["type"] = issue_type

        logger.info(
            f"New issue detected: "
            f"#{issue_number} "
            f"({issue_type})"
        )

        # ---------------------------------------------
        # Non-bug issue
        # ---------------------------------------------

        if issue_type != "bug":

            logger.info(
                f"No automated action required "
                f"for issue #{issue_number}."
            )

            issue_data["automation"] = {
                "status": "success",
                "action": "none",
                "action_taken_at": None,
            }

            processed_issues.add(
                issue_number
            )

            processed_issue_data.append(
                issue_data
            )

            continue

        # ---------------------------------------------
        # AI comment generation
        # ---------------------------------------------

        try:

            logger.info(
                f"Generating AI comment for "
                f"issue #{issue_number}."
            )

            comment = generate_issue_comment(
                title=issue_data["title"],
                body=issue_data["body"],
                issue_type=issue_type,
            )

            logger.info(
                f"AI comment generated for "
                f"issue #{issue_number}."
            )

        except AIConfigurationError as error:

            logger.error(
                f"AI configuration error for "
                f"issue #{issue_number}: {error}"
            )

            issue_data["automation"] = {
                "status": "failed",
                "action": "ai_comment_generation",
                "action_taken_at": None,
                "error": str(error),
            }

            processed_issue_data.append(
                issue_data
            )

            continue

        except AIAPIError as error:

            logger.error(
                f"AI API error for "
                f"issue #{issue_number}: {error}"
            )

            issue_data["automation"] = {
                "status": "failed",
                "action": "ai_comment_generation",
                "action_taken_at": None,
                "error": str(error),
            }

            processed_issue_data.append(
                issue_data
            )

            continue

        # ---------------------------------------------
        # Post AI-generated comment to GitHub
        # ---------------------------------------------

        try:

            add_issue_comment(
                owner,
                repository_name,
                issue_number,
                github_token,
                comment,
            )

            action_time = (
                get_current_time()
            )

            logger.info(
                f"AI-generated comment added "
                f"to issue #{issue_number}."
            )

            issue_data["automation"] = {
                "status": "success",
                "action": "ai_comment_created",
                "action_taken_at": action_time,
            }

            processed_issues.add(
                issue_number
            )

        except GitHubConnectionError as error:

            logger.error(
                f"Connection error while "
                f"posting AI comment to "
                f"issue #{issue_number}: "
                f"{error}"
            )

            issue_data["automation"] = {
                "status": "failed",
                "action": "ai_comment_creation",
                "action_taken_at": None,
                "error": str(error),
            }

        except GitHubAPIError as error:

            logger.error(
                f"GitHub API error while "
                f"posting AI comment to "
                f"issue #{issue_number}: "
                f"{error}"
            )

            issue_data["automation"] = {
                "status": "failed",
                "action": "ai_comment_creation",
                "action_taken_at": None,
                "error": str(error),
            }

        processed_issue_data.append(
            issue_data
        )

    # -------------------------------------------------
    # 4. Save state
    # -------------------------------------------------

    save_processed_issues(
        processed_issues
    )

    logger.info(
        "Automation state saved."
    )

    # -------------------------------------------------
    # 5. Generate report
    # -------------------------------------------------

    report_file = (
        generate_json_report(
            processed_issue_data
        )
    )

    logger.info(
        f"Report generated: {report_file}"
    )

    logger.info(
        "Automation run completed."
    )


if __name__ == "__main__":

    try:

        main()

    except ConfigurationError as error:

        logger = setup_logger()

        logger.error(
            f"Configuration error: {error}"
        )
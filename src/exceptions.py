class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an error."""
    pass


class GitHubConnectionError(Exception):
    """Raised when the application cannot connect to GitHub."""
    pass


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class AIAPIError(Exception):
    """Raised when the AI API returns an error."""
    pass


class AIConfigurationError(Exception):
    """Raised when AI configuration is missing or invalid."""
    pass
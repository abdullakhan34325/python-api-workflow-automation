# Python API Workflow Automation & Notification System

A Python-based automation system that integrates the GitHub REST API with Gemini AI to automatically detect and classify GitHub issues, generate useful AI-assisted responses for bug reports, post comments back to GitHub, track processed issues, and generate structured reports and logs.

## Features

- GitHub REST API integration
- Secure API authentication using environment variables
- Automated GitHub issue retrieval
- Issue data processing and classification
- Bug detection using keyword-based classification
- Gemini AI integration for automated issue responses
- Automatic posting of AI-generated comments to GitHub
- Processed issue state tracking
- Retry handling for temporary API/network failures
- Timeout and connection error handling
- Structured JSON reporting
- Application logging
- Environment-based configuration
- Modular Python project structure

## Workflow

```text
GitHub Repository
        |
        v
Fetch GitHub Issues
        |
        v
Process Issue Data
        |
        v
Check Processing State
        |
        v
Classify Issue
        |
        +------ General Issue ------> No Automated Action
        |
        v
      Bug
        |
        v
Gemini AI Analysis
        |
        v
Generate Professional Comment
        |
        v
Post Comment to GitHub
        |
        v
Save Processing State
        |
        v
Generate JSON Report
        |
        v
Log Automation Activity

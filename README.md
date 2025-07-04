[![Python CI](https://github.com/mozaloom/codecraft-pr-agent/actions/workflows/main.yml/badge.svg)](https://github.com/mozaloom/codecraft-pr-agent/actions/workflows/main.yml)
# PR Agent

A Model Context Protocol (MCP) server that automates pull request analysis and team notifications through Slack integration.

## Overview

This project provides an intelligent PR agent that monitors GitHub workflow events, analyzes pull requests using AI, and sends structured notifications to Slack channels. It combines MCP tools and prompts to create complete team communication workflows.

## Features

- **Automated PR Analysis**: Uses Google Gemini AI to analyze pull request content and generate insights
- **GitHub Webhook Integration**: Monitors GitHub Actions events and workflow runs
- **Slack Notifications**: Sends formatted notifications to Slack channels via webhooks
- **PR Templates**: Supports multiple PR types with predefined templates (bug fixes, features, documentation, etc.)
- **Event Storage**: Stores GitHub events for processing and analysis
- **MCP Server**: Exposes tools and prompts through the Model Context Protocol

## Components

### Core Files

- `server.py` - Main MCP server with Slack notification integration
- `webhook_server.py` - GitHub webhook endpoint for receiving events
- `mcp_gemini_client.py` - Gemini AI client for PR analysis
- `templates/` - PR templates for different types of changes

### Templates

The project includes templates for common PR types:

- Bug fixes
- Feature implementations
- Documentation updates
- Code refactoring
- Tests
- Performance improvements
- Security fixes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mozaloom/codecraft-pr-agent.git
cd codecraft-pr-agent
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
GEMINI_API_KEY=your_google_gemini_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

Alternatively, run the setup script:
```bash
bash setup.sh
```

## Usage

### Start the MCP Server

```bash
python server.py
```

### Start the Webhook Server

```bash
python webhook_server.py
```

### Configure GitHub Webhooks

Set up a webhook in your GitHub repository pointing to your webhook server endpoint. The webhook should trigger on:
- Pull request events
- Workflow run events
- Check run events

## Configuration

The agent can be configured through environment variables and the templates directory. Modify the templates to customize PR analysis for your team's specific needs.

## Requirements

- Python 3.12+
- UV package manager (recommended) or pip
- Google Gemini API key
- Slack webhook URL
- GitHub repository with webhook access

## Development

Run tests:
```bash
pytest
```

Or with uv:
```bash
uv run pytest
```

## License

See LICENSE file for details.

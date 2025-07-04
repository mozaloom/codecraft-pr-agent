# MCP-Gemini PR Agent - Complete Guide

## Overview
A comprehensive MCP (Model Context Protocol) client that integrates Google Gemini AI with your development workflow. It provides intelligent PR analysis, CI/CD monitoring, and team communication through Slack.

## ✨ Key Features

### 🤖 AI-Powered Analysis
- **Smart PR Analysis**: Uses Gemini AI to analyze git changes and suggest appropriate PR templates
- **Intelligent Template Matching**: Automatically identifies change types (bug, feature, docs, etc.)
- **Context-Aware Descriptions**: Generates detailed, professional PR descriptions

### 🔧 MCP Integration
- **Multiple Tools**: Connects to 6+ MCP tools for different workflows
- **Prompt System**: Uses 6+ intelligent prompts for guided AI interactions
- **Real-time Communication**: Direct integration with your MCP server

### 📊 CI/CD Monitoring
- **GitHub Actions Integration**: Monitors workflow status and events
- **Failure Analysis**: AI-powered troubleshooting for failed builds
- **Status Reporting**: Comprehensive CI/CD health summaries

### 📢 Team Communication
- **Slack Integration**: Send formatted notifications to team channels
- **Multiple Output Formats**: Save to file, copy to clipboard, or send alerts
- **Rich Formatting**: Proper Slack markdown for professional messages

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
uv sync

# Or use the setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Keys
```bash
# Edit .env file
GEMINI_API_KEY=your_google_gemini_api_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 3. Usage Options

#### Command Line Interface
```bash
# Analyze PR changes
uv run python mcp_gemini_client.py analyze

# Check CI/CD status
uv run python mcp_gemini_client.py ci-status

# Send Slack alert
uv run python mcp_gemini_client.py slack-alert

# Interactive mode
uv run python mcp_gemini_client.py interactive
```

#### Interactive Mode
```bash
uv run python mcp_gemini_client.py
```
Then use commands:
- `1` or `analyze` - Analyze PR changes
- `2` or `ci-status` - Check CI/CD status  
- `3` or `slack-alert` - Send notifications
- `4` or `tools` - List available tools
- `5` or `prompts` - List available prompts

## 🛠️ Available Tools

### Core Analysis Tools
- **analyze_file_changes** - Git diff analysis with intelligent parsing
- **get_pr_templates** - Access to professional PR templates
- **suggest_template** - AI-powered template recommendations

### CI/CD Tools  
- **get_recent_actions_events** - GitHub Actions webhook events
- **get_workflow_status** - Current status of all workflows

### Communication Tools
- **send_slack_notification** - Formatted team notifications

## 💡 Available Prompts

### CI/CD Prompts
- **analyze_ci_results** - Comprehensive CI/CD analysis
- **troubleshoot_workflow_failure** - Guided failure debugging
- **create_deployment_summary** - Deployment status reports

### Communication Prompts
- **format_ci_failure_alert** - Slack-formatted failure alerts
- **format_ci_success_summary** - Success celebration messages
- **generate_pr_status_report** - Complete PR status overview

## 🔄 Workflow Examples

### 1. Complete PR Analysis
```bash
# Make some changes
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add new feature"

# Analyze with AI
uv run python mcp_gemini_client.py analyze
```

Result: Gets AI analysis, suggests template, generates complete PR description

### 2. CI/CD Monitoring
```bash
# Check status after pushing
uv run python mcp_gemini_client.py ci-status
```

Result: Shows workflow status, identifies failures, provides troubleshooting

### 3. Team Communication
```bash
# Send status to team
uv run python mcp_gemini_client.py slack-alert
```

Result: Formatted Slack message with current status and action items

## 🎯 Integration with Claude Code

This client provides the same functionality as Claude Code but uses Google Gemini:

**Claude Code Equivalent:**
- Claude: Uses Claude's built-in MCP support
- This Client: Direct MCP connection + Gemini AI

**Advantages:**
- **Flexibility**: Use any Gemini model (Flash, Pro, etc.)
- **Cost Control**: Direct API usage with transparent pricing
- **Customization**: Full control over prompts and analysis
- **Offline Capability**: Works without Claude subscription

## 🔧 Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gemini API    │    │  MCP Server     │    │   GitHub API    │
│                 │    │                 │    │                 │
│ • Analysis      │    │ • Tools         │    │ • Webhooks      │
│ • Generation    │    │ • Prompts       │    │ • Actions       │
│ • Reasoning     │    │ • Templates     │    │ • Status        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  MCP-Gemini     │
                    │   Client        │
                    │                 │
                    │ • Interactive   │
                    │ • CLI           │ 
                    │ • Automation    │
                    └─────────────────┘
```

## 📝 Example Output

### PR Analysis Result:
```
🔍 Analyzing PR Changes...
========================================
🤖 AI Analysis:
This PR adds comprehensive MCP-Gemini integration with interactive
mode, enhanced error handling, and multiple workflow options...

🎯 Identified change type: feature
📝 Recommended PR Template: Feature

✅ Generated PR Description:
## New Feature: MCP-Gemini PR Agent

### Description
Comprehensive MCP client with Google Gemini AI integration...

### Implementation  
- Interactive CLI with multiple command options
- Enhanced error handling and user feedback
- Integration with all MCP server capabilities
...
```

## 🚀 Next Steps

1. **Try the Demo**: `uv run python demo.py`
2. **Run Interactive Mode**: `uv run python mcp_gemini_client.py`
3. **Set up GitHub Webhooks**: For real-time CI/CD monitoring
4. **Configure Slack**: For team notifications
5. **Customize Prompts**: Modify analysis prompts for your workflow

## 🆚 Comparison with Claude Code

| Feature | Claude Code | MCP-Gemini Client |
|---------|-------------|-------------------|
| AI Model | Claude 3.5 | Gemini 1.5 Flash/Pro |
| MCP Support | Built-in | Direct connection |
| Cost | Subscription | Pay-per-use |
| Customization | Limited | Full control |
| Offline Use | No | Yes (with API) |
| Interactive Mode | Limited | Full CLI |
| Automation | Basic | Advanced |

The MCP-Gemini client provides equivalent functionality to Claude Code with greater flexibility and control!

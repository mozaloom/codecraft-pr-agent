# PR Agent - MCP Server

An intelligent MCP (Model Context Protocol) server that analyzes your git changes and suggests the best PR template for your pull requests using Google Gemini AI.

## What it does

- **Analyzes your code changes** - Looks at git diffs to understand what you've modified
- **Suggests PR templates** - Recommends the right template (bug fix, feature, docs, etc.)
- **Smart matching** - Uses AI to match your changes with appropriate PR templates
- **Gemini Integration** - Leverages Google Gemini AI for intelligent analysis and template generation

## Quick Start

### 1. Install dependencies
```bash
uv sync
```

### 2. Add to Claude
```bash
claude mcp add pr-agent -- uv --directory /path/to/this/project run server.py
```

### 3. Use with Claude
Make some changes in any git repo, then ask Claude:
> "Can you analyze my changes and suggest a PR template?"

## Quick Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up your Gemini API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Google Gemini API key
   ```

3. **Run the PR analysis**:
   ```bash
   uv run python mcp_gemini_client.py
   ```

## Available Templates

- **Bug Fix** - For fixing issues and bugs
- **Feature** - For new functionality
- **Documentation** - For docs updates
- **Refactor** - For code cleanup
- **Test** - For adding tests
- **Performance** - For optimizations
- **Security** - For security improvements

## Testing

```bash
# Run tests
uv run pytest test_server.py -v

# Validate setup
uv run python validate_solution.py
```

## How it works

1. You make changes to your code
2. The server analyzes your git diff
3. AI matches your changes to the best template type
4. You get a pre-filled PR template ready to use

That's it! Smart PR templates based on what you actually changed.
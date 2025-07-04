#!/bin/bash
# Setup script for MCP Gemini Client

echo "🚀 Setting up MCP-Gemini PR Agent..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo ""
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys"
    else
        echo "📝 Creating .env file..."
        cat > .env << EOF
# Google Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_google_gemini_api_key_here

# Slack Webhook URL (optional, for notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
EOF
        echo "⚠️  Please edit .env and add your API keys"
    fi
else
    echo "✅ .env file already exists"
fi

# Make the client executable
chmod +x mcp_gemini_client.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Run: python mcp_gemini_client.py --help"
echo "3. Try: python mcp_gemini_client.py interactive"

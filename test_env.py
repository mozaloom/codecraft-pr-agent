#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test environment loading
try:
    from dotenv import load_dotenv
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    
    print(f"📁 Script directory: {script_dir}")
    print(f"📄 .env file path: {env_file}")
    print(f"📄 .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            print(f"📄 .env content:\n{content}")
    
    load_dotenv(env_file)
    
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"🔑 SLACK_WEBHOOK_URL loaded: {bool(slack_url)}")
    print(f"🔑 GEMINI_API_KEY loaded: {bool(gemini_key)}")
    
    if slack_url:
        print(f"🔗 SLACK_WEBHOOK_URL: {slack_url[:50]}...")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

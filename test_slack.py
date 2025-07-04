#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"
    load_dotenv(env_file)
    
    print(f"🔑 Environment loaded from {env_file}")
    
except ImportError:
    print("⚠️ python-dotenv not available")

# Test Slack notification function directly
import requests

def test_slack_notification():
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    print(f"🔗 SLACK_WEBHOOK_URL: {bool(webhook_url)}")
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL environment variable not set")
        return False
    
    try:
        # Test message
        test_message = "🧪 Test notification from PR Agent"
        
        payload = {
            "text": test_message,
            "mrkdwn": True
        }
        
        print(f"📤 Sending test message: {test_message}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Slack notification sent successfully!")
            return True
        else:
            print(f"❌ Slack notification failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Slack notification: {e}")
        return False

if __name__ == "__main__":
    test_slack_notification()

#!/usr/bin/env python3
"""
Demo script for MCP-Gemini PR Agent
Shows all the capabilities in action
"""

import asyncio
import os
import sys
from mcp_gemini_client import MCPGeminiClient

async def demo():
    """Run a comprehensive demo of all features."""
    print("🎬 MCP-Gemini PR Agent Demo")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    # Initialize client
    client = MCPGeminiClient(api_key)
    
    # Find server
    server_path = "./server.py"
    if not os.path.exists(server_path):
        print("❌ server.py not found")
        return
    
    print("🔌 Connecting to MCP server...")
    
    try:
        # Demo connection and tool listing
        await demo_connection(client, server_path)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def demo_connection(client, server_path):
    """Demo connection and basic functionality."""
    from mcp.client.stdio import stdio_client
    from mcp import StdioServerParameters, ClientSession
    
    server_params = StdioServerParameters(command="python", args=[server_path])
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            client.session = session
            await session.initialize()
            
            # Get tools and prompts
            tools_response = await session.list_tools()
            client.available_tools = {tool.name: tool for tool in tools_response.tools}
            
            try:
                prompts_response = await session.list_prompts()
                client.available_prompts = {prompt.name: prompt for prompt in prompts_response.prompts}
            except:
                client.available_prompts = {}
            
            print(f"✅ Connected! Found {len(client.available_tools)} tools and {len(client.available_prompts)} prompts")
            
            # Demo 1: List all capabilities
            print("\n📋 Available Tools:")
            for name, tool in client.available_tools.items():
                print(f"  🔧 {name}")
            
            if client.available_prompts:
                print("\n💡 Available Prompts:")
                for name in client.available_prompts:
                    print(f"  💭 {name}")
            
            # Demo 2: Analyze changes (if any)
            print("\n🔍 Testing File Analysis...")
            try:
                changes = await client.call_mcp_tool("analyze_file_changes", {"base_branch": "main"})
                print("✅ File analysis works!")
                
                # Quick Gemini analysis
                if "total_diff_lines" in changes:
                    summary = client.analyze_with_gemini(
                        "Summarize these git changes in one sentence:", 
                        changes[:500]  # Truncate for demo
                    )
                    print(f"🤖 Gemini says: {summary}")
                
            except Exception as e:
                print(f"⚠️  File analysis: {e}")
            
            # Demo 3: Template suggestion
            print("\n📋 Testing Template Suggestion...")
            try:
                templates = await client.call_mcp_tool("get_pr_templates")
                print("✅ Template system works!")
                template_count = templates.count('"filename"')
                print(f"📝 Found {template_count} PR templates")
                
            except Exception as e:
                print(f"⚠️  Template system: {e}")
            
            # Demo 4: CI/CD status (if webhook data exists)
            print("\n⚙️  Testing CI/CD Integration...")
            try:
                events = await client.call_mcp_tool("get_recent_actions_events", {"limit": 5})
                workflows = await client.call_mcp_tool("get_workflow_status")
                print("✅ CI/CD integration works!")
                
                if "[]" not in events:
                    print("📊 Found GitHub Actions events")
                else:
                    print("📊 No GitHub Actions events yet (webhook not configured)")
                    
            except Exception as e:
                print(f"⚠️  CI/CD integration: {e}")
            
            # Demo 5: Slack integration
            print("\n📢 Testing Slack Integration...")
            try:
                if "send_slack_notification" in client.available_tools:
                    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
                    if webhook_url and "your_slack" not in webhook_url.lower():
                        # Test with a demo message
                        result = await client.call_mcp_tool(
                            "send_slack_notification", 
                            {"message": "🎬 MCP-Gemini Demo: Testing Slack integration!"}
                        )
                        print(f"✅ Slack test: {result}")
                    else:
                        print("⚠️  Slack webhook URL not configured")
                else:
                    print("⚠️  Slack tool not available in this server")
                    
            except Exception as e:
                print(f"⚠️  Slack integration: {e}")
            
            print(f"\n{'='*50}")
            print("🎉 Demo Complete!")
            print("\nTo use the full system:")
            print("1. python mcp_gemini_client.py analyze      # Analyze PR changes")
            print("2. python mcp_gemini_client.py ci-status    # Check CI/CD")
            print("3. python mcp_gemini_client.py interactive  # Interactive mode")

if __name__ == "__main__":
    asyncio.run(demo())

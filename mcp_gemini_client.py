#!/usr/bin/env python3
"""
MCP Client with Google Gemini API
A comprehensive client that connects to your MCP server and uses Gemini for intelligent analysis
"""

import json
import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, that's fine
    pass

class MCPGeminiClient:
    def __init__(self, gemini_api_key: str, model_name: str = "gemini-1.5-flash"):
        """Initialize the MCP-Gemini client.
        
        Args:
            gemini_api_key: Your Google Gemini API key
            model_name: Gemini model to use (default: gemini-1.5-flash)
        """
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # MCP session will be set when connecting
        self.session: Optional[ClientSession] = None
        self.available_tools: Dict[str, Any] = {}
        self.available_prompts: Dict[str, Any] = {}

    async def connect_to_mcp_server(self, server_script_path: str):
        """Connect to the MCP server and maintain the connection.
        
        Args:
            server_script_path: Path to your MCP server script
        """
        # Server parameters
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )
        
        # Connect to server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                
                # Initialize the session
                await session.initialize()
                
                # Get available tools
                tools_response = await session.list_tools()
                self.available_tools = {
                    tool.name: tool for tool in tools_response.tools
                }
                
                # Get available prompts
                try:
                    prompts_response = await session.list_prompts()
                    self.available_prompts = {
                        prompt.name: prompt for prompt in prompts_response.prompts
                    }
                except Exception:
                    # Prompts might not be available in older MCP versions
                    self.available_prompts = {}
                
                print(f"🔌 Connected to MCP server")
                print(f"📋 Available tools: {list(self.available_tools.keys())}")
                if self.available_prompts:
                    print(f"💡 Available prompts: {list(self.available_prompts.keys())}")
                
                # Run interactive mode or specific workflow based on arguments
                if len(sys.argv) > 1:
                    command = sys.argv[1]
                    await self.handle_command(command)
                else:
                    await self.interactive_mode()
                
                return session

    async def handle_command(self, command: str):
        """Handle specific commands from command line."""
        if command == "analyze":
            await self.generate_pr_description()
        elif command == "ci-status":
            await self.analyze_ci_status()
        elif command == "slack-alert":
            await self.send_ci_alert()
        elif command == "interactive":
            await self.interactive_mode()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: analyze, ci-status, slack-alert, interactive")

    async def interactive_mode(self):
        """Interactive mode for exploring MCP capabilities."""
        print("\n🤖 MCP-Gemini Interactive Mode")
        print("=" * 50)
        print("Commands:")
        print("  1. analyze     - Analyze PR changes")
        print("  2. ci-status   - Check CI/CD status")
        print("  3. slack-alert - Send Slack notification")
        print("  4. tools       - List available tools")
        print("  5. prompts     - List available prompts")
        print("  6. help        - Show this help")
        print("  7. quit        - Exit")
        print()
        
        while True:
            try:
                command = input("Enter command (or number): ").strip().lower()
                
                if command in ["quit", "exit", "q", "7"]:
                    break
                elif command in ["analyze", "1"]:
                    await self.generate_pr_description()
                elif command in ["ci-status", "2"]:
                    await self.analyze_ci_status()
                elif command in ["slack-alert", "3"]:
                    await self.send_ci_alert()
                elif command in ["tools", "4"]:
                    await self.list_tools()
                elif command in ["prompts", "5"]:
                    await self.list_prompts()
                elif command in ["help", "6"]:
                    print("Commands: analyze, ci-status, slack-alert, tools, prompts, help, quit")
                else:
                    print(f"❌ Unknown command: {command}")
                
                print()  # Add spacing between commands
                
            except (KeyboardInterrupt, EOFError):
                break
        
        print("👋 Goodbye!")

    async def list_tools(self):
        """List all available MCP tools."""
        print("📋 Available MCP Tools:")
        print("=" * 30)
        for name, tool in self.available_tools.items():
            print(f"🔧 {name}")
            if hasattr(tool, 'description') and tool.description:
                print(f"   {tool.description}")
            print()

    async def list_prompts(self):
        """List all available MCP prompts."""
        if not self.available_prompts:
            print("💡 No prompts available")
            return
            
        print("💡 Available MCP Prompts:")
        print("=" * 30)
        for name, prompt in self.available_prompts.items():
            print(f"💭 {name}")
            if hasattr(prompt, 'description') and prompt.description:
                print(f"   {prompt.description}")
            print()

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result as string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available. Available tools: {list(self.available_tools.keys())}")
        
        print(f"🔧 Calling tool: {tool_name}")
        
        # Call the tool
        result = await self.session.call_tool(tool_name, arguments or {})
        
        # Extract content from result
        if result.content:
            return result.content[0].text if result.content else ""
        return ""

    async def call_mcp_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a prompt on the MCP server.
        
        Args:
            prompt_name: Name of the prompt to call
            arguments: Arguments to pass to the prompt
            
        Returns:
            Prompt content as string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        if prompt_name not in self.available_prompts:
            raise ValueError(f"Prompt '{prompt_name}' not available. Available prompts: {list(self.available_prompts.keys())}")
        
        print(f"💭 Getting prompt: {prompt_name}")
        
        # Get the prompt
        result = await self.session.get_prompt(prompt_name, arguments or {})
        
        # Extract content from result
        if result.messages and len(result.messages) > 0:
            return result.messages[0].content.text if hasattr(result.messages[0].content, 'text') else str(result.messages[0].content)
        return ""

    def analyze_with_gemini(self, prompt: str, context: str = "") -> str:
        """Use Gemini to analyze the given prompt with context.
        
        Args:
            prompt: The main prompt/question
            context: Additional context (like file changes, PR data, etc.)
            
        Returns:
            Gemini's response
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        try:
            print("🧠 Analyzing with Gemini...")
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

    async def analyze_ci_status(self):
        """Analyze CI/CD status using MCP tools and Gemini."""
        print("🔍 Analyzing CI/CD Status...")
        print("=" * 40)
        
        try:
            # Get recent events
            events_data = await self.call_mcp_tool("get_recent_actions_events", {"limit": 10})
            
            # Get workflow status
            workflow_data = await self.call_mcp_tool("get_workflow_status")
            
            # Use Gemini to analyze
            analysis_prompt = """
            Analyze the CI/CD status and provide insights:
            
            Recent Events:
            {events}
            
            Workflow Status:
            {workflows}
            
            Please provide:
            1. Overall CI/CD health status
            2. Any failing workflows and possible causes
            3. Trends or patterns you notice
            4. Recommendations for improvement
            """
            
            analysis = self.analyze_with_gemini(
                analysis_prompt.format(events=events_data, workflows=workflow_data)
            )
            
            print("📊 CI/CD Analysis:")
            print("=" * 30)
            print(analysis)
            
        except Exception as e:
            print(f"❌ Error analyzing CI status: {e}")

    async def send_ci_alert(self):
        """Send a CI alert to Slack using MCP tools."""
        print("📢 Sending CI Alert...")
        print("=" * 25)
        
        try:
            # Check if Slack tool is available
            if "send_slack_notification" not in self.available_tools:
                print("❌ Slack notification tool not available")
                return
            
            # Get workflow status
            workflow_data = await self.call_mcp_tool("get_workflow_status")
            
            # Create alert message
            alert_prompt = """
            Create a Slack alert message based on this CI status:
            {workflow_data}
            
            Format it as a concise Slack message with:
            - Current status (✅ or ❌)
            - Key information
            - Any required actions
            
            Keep it under 200 characters for Slack.
            """
            
            message = self.analyze_with_gemini(
                alert_prompt.format(workflow_data=workflow_data)
            )
            
            # Send to Slack
            result = await self.call_mcp_tool("send_slack_notification", {"message": message})
            
            print("📤 Slack Message:")
            print(message)
            print(f"\n📋 Result: {result}")
            
        except Exception as e:
            print(f"❌ Error sending Slack alert: {e}")

    async def analyze_pr_changes(self, base_branch: str = "main", working_directory: str = None) -> Dict[str, Any]:
        """Analyze PR changes using MCP tools and Gemini.
        
        Args:
            base_branch: Base branch to compare against
            working_directory: Directory to analyze (optional)
            
        Returns:
            Analysis results
        """
        # Get file changes using MCP
        changes_args = {"base_branch": base_branch}
        if working_directory:
            changes_args["working_directory"] = working_directory
            
        changes_data = await self.call_mcp_tool("analyze_file_changes", changes_args)
        
        # Parse the changes data
        try:
            changes_json = json.loads(changes_data)
        except json.JSONDecodeError:
            changes_json = {"error": "Failed to parse changes data", "raw": changes_data}
        
        # Use Gemini to analyze the changes
        analysis_prompt = """
        Analyze the following git changes and provide:
        1. A summary of what this PR does
        2. The type of change (bug, feature, docs, refactor, test, performance, security)
        3. Key files affected
        4. Potential risks or considerations
        5. Suggested PR title and description
        
        Be concise but thorough in your analysis.
        """
        
        gemini_analysis = self.analyze_with_gemini(analysis_prompt, changes_data)
        
        return {
            "changes_data": changes_json,
            "ai_analysis": gemini_analysis
        }

    async def suggest_pr_template(self, analysis_summary: str, change_type: str) -> Dict[str, Any]:
        """Get PR template suggestion using MCP tools.
        
        Args:
            analysis_summary: Summary of the changes
            change_type: Type of change identified
            
        Returns:
            Template suggestion
        """
        # Get template suggestion from MCP
        template_data = await self.call_mcp_tool("suggest_template", {
            "changes_summary": analysis_summary,
            "change_type": change_type
        })
        
        try:
            template_json = json.loads(template_data)
        except json.JSONDecodeError:
            print(f"❌ Raw template response: {template_data}")
            template_json = {"error": "Failed to parse template data", "raw": template_data}
        
        return template_json

    async def generate_pr_description(self, working_directory: str = None, base_branch: str = "main"):
        """Complete PR analysis and description generation workflow.
        
        Args:
            working_directory: Directory to analyze
            base_branch: Base branch to compare against
        """
        print("🔍 Analyzing PR Changes...")
        print("=" * 40)
        
        # Step 1: Analyze changes
        analysis = await self.analyze_pr_changes(base_branch, working_directory)
        
        if "error" in analysis["changes_data"]:
            print(f"❌ Error analyzing changes: {analysis['changes_data']['error']}")
            return
        
        print("📊 Changes analyzed successfully!")
        print(f"\n{'='*60}")
        print("🤖 AI Analysis:")
        print(f"{'='*60}")
        print(analysis["ai_analysis"])
        
        # Step 2: Extract change type from AI analysis
        change_type_prompt = """
        Based on your previous analysis, what is the primary type of this change? 
        Respond with just one word: bug, feature, docs, refactor, test, performance, or security
        """
        
        change_type = self.analyze_with_gemini(
            change_type_prompt, 
            analysis["ai_analysis"]
        ).strip().lower()
        
        # Step 3: Get template suggestion
        print(f"\n🎯 Identified change type: {change_type}")
        print("📋 Getting template suggestion...")
        
        template_suggestion = await self.suggest_pr_template(
            analysis["ai_analysis"], 
            change_type
        )
        
        if "error" not in template_suggestion:
            print(f"\n{'='*60}")
            print("📝 Recommended PR Template:")
            print(f"{'='*60}")
            print(f"Template: {template_suggestion['recommended_template']['type']}")
            print(f"Reasoning: {template_suggestion['reasoning']}")
            print(f"\nTemplate Content:\n{template_suggestion['template_content']}")
            
            # Step 4: Generate filled template using enhanced Gemini prompt
            fill_template_prompt = f"""
            You are an expert software developer creating a professional PR description.
            
            CONTEXT:
            {analysis["ai_analysis"]}
            
            TASK:
            Fill out this PR template with specific, accurate content based on the git changes above:
            
            {template_suggestion['template_content']}
            
            REQUIREMENTS:
            - Use specific file names, function names, and technical details from the analysis
            - Write clear, concise descriptions
            - Include relevant technical context
            - Keep the same template structure and formatting
            - Replace all placeholder text with actual content
            
            Generate a complete, professional PR description:
            """
            
            filled_template = self.analyze_with_gemini(fill_template_prompt)
            
            print(f"\n{'='*60}")
            print("✅ Generated PR Description:")
            print(f"{'='*60}")
            print(filled_template)
            
            # Step 5: Offer to save or send
            await self.post_generation_options(filled_template, change_type)
            
        else:
            print(f"❌ Error getting template: {template_suggestion.get('error', 'Unknown error')}")

    async def post_generation_options(self, pr_description: str, change_type: str):
        """Offer options after generating PR description."""
        print(f"\n{'='*40}")
        print("📋 What would you like to do next?")
        print("1. Save to file")
        print("2. Send Slack notification")
        print("3. Copy to clipboard") 
        print("4. Continue")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                filename = f"pr_description_{change_type}.md"
                with open(filename, 'w') as f:
                    f.write(pr_description)
                print(f"💾 Saved to {filename}")
                
            elif choice == "2":
                if "send_slack_notification" in self.available_tools:
                    slack_message = f"📝 New PR Ready for Review ({change_type})\n\n{pr_description[:500]}..."
                    result = await self.call_mcp_tool("send_slack_notification", {"message": slack_message})
                    print(f"📤 Slack result: {result}")
                else:
                    print("❌ Slack tool not available")
                    
            elif choice == "3":
                try:
                    import pyperclip
                    pyperclip.copy(pr_description)
                    print("📋 Copied to clipboard")
                except ImportError:
                    print("❌ pyperclip not installed. Install with: pip install pyperclip")
                    
        except (KeyboardInterrupt, EOFError):
            pass

async def main():
    """Main function to run the MCP-Gemini client."""
    print("🚀 MCP-Gemini PR Agent")
    print("=" * 40)
    
    # Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("❌ Please set GEMINI_API_KEY environment variable")
        print("   You can:")
        print("   1. Set it directly: export GEMINI_API_KEY='your_key_here'")
        print("   2. Add it to a .env file: GEMINI_API_KEY=your_key_here")
        return
    
    # Determine which server to use
    server_options = [
        "./server.py",
        "./slack-notification/starter/server.py",
        "./github-actions-integration/starter/server.py"
    ]
    
    MCP_SERVER_PATH = None
    for path in server_options:
        if os.path.exists(path):
            MCP_SERVER_PATH = path
            break
    
    if not MCP_SERVER_PATH:
        print("❌ No MCP server found. Please ensure server.py exists.")
        return
    
    print(f"📡 Using MCP server: {MCP_SERVER_PATH}")
    
    # Initialize client with error handling
    try:
        client = MCPGeminiClient(GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        print("   Make sure you have the correct API key and internet connection")
        return
    
    # Connect and run
    try:
        await client.connect_to_mcp_server(MCP_SERVER_PATH)
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print("   Troubleshooting:")
        print("   1. Check that the server script exists and is executable")
        print("   2. Ensure all Python dependencies are installed")
        print("   3. Verify the server script runs independently")

def print_usage():
    """Print usage information."""
    print("Usage:")
    print("  python mcp_gemini_client.py                 # Interactive mode")
    print("  python mcp_gemini_client.py analyze         # Analyze PR changes")
    print("  python mcp_gemini_client.py ci-status       # Check CI/CD status")
    print("  python mcp_gemini_client.py slack-alert     # Send Slack alert")
    print("  python mcp_gemini_client.py interactive     # Force interactive mode")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print_usage()
    else:
        asyncio.run(main())
#!/usr/bin/env python3
"""
MCP Client with Google Gemini API
Connects to your MCP server and uses Gemini for AI analysis
"""

import json
import asyncio
import os
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

    async def connect_to_mcp_server(self, server_script_path: str):
        """Connect to the MCP server.
        
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
                
                print(f"Connected to MCP server. Available tools: {list(self.available_tools.keys())}")
                
                # Run the PR analysis workflow here since we need to stay in the context
                await self.generate_pr_description(
                    working_directory=None,
                    base_branch="main"
                )
                
                return session

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
        
        # Call the tool
        result = await self.session.call_tool(tool_name, arguments or {})
        
        # Extract content from result
        if result.content:
            return result.content[0].text if result.content else ""
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
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

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
            template_json = {"error": "Failed to parse template data", "raw": template_data}
        
        return template_json

    async def generate_pr_description(self, working_directory: str = None, base_branch: str = "main"):
        """Complete PR analysis and description generation workflow.
        
        Args:
            working_directory: Directory to analyze
            base_branch: Base branch to compare against
        """
        print("🔍 Analyzing PR changes...")
        
        # Step 1: Analyze changes
        analysis = await self.analyze_pr_changes(base_branch, working_directory)
        
        if "error" in analysis["changes_data"]:
            print(f"❌ Error analyzing changes: {analysis['changes_data']['error']}")
            return
        
        print("📊 Changes analyzed. Getting AI insights...")
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
            
            # Step 4: Generate filled template
            fill_template_prompt = f"""
            Fill out this PR template based on the analysis:
            
            Template:
            {template_suggestion['template_content']}
            
            Use the information from the git changes and analysis to provide specific, accurate content for each section.
            """
            
            filled_template = self.analyze_with_gemini(
                fill_template_prompt,
                analysis["ai_analysis"]
            )
            
            print(f"\n{'='*60}")
            print("✅ Generated PR Description:")
            print(f"{'='*60}")
            print(filled_template)
        else:
            print(f"❌ Error getting template: {template_suggestion['error']}")

async def main():
    """Main function to run the MCP-Gemini client."""
    # Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    # Path to your MCP server script
    MCP_SERVER_PATH = "./server.py"  # Updated to point to the actual server file
    
    # Working directory (optional - will use current directory if not specified)
    WORKING_DIRECTORY = None  # Let MCP server auto-detect from git repo
    
    # Initialize client
    client = MCPGeminiClient(GEMINI_API_KEY)
    
    try:
        # Connect to MCP server and run the workflow
        await client.connect_to_mcp_server(MCP_SERVER_PATH)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Example usage
    print("🚀 MCP-Gemini PR Agent")
    print("=" * 40)
    asyncio.run(main())
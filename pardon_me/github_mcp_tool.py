import os
from dotenv import load_dotenv 
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams  

# Load environment variables from .env file
load_dotenv()
GITHUB_TOKEN = os.environ.get("GITHUB_MCP_PAT")

# Github MCP toolset that allows access to the github repositories and issues.
github_mcp_tool = McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "X-MCP-Toolsets": "issues,repos",
                    "X-MCP-Readonly": "true"
                },
                timeout = 30,
            ),
        )
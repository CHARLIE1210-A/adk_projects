import json
import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.agents.llm_agent import Agent

# ---------------------------------------------------------------------
# Setup logging
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------
# System Instruction for the Notion Agent
# ---------------------------------------------------------------------
SYSTEM_INSTRUCTION = (
    "You are a Notion knowledge assistant. "
    "Your purpose is to access, read, write and summarize data from connected Notion pages, databases, or workspaces "
    "using the Notion MCP integration. "
    "If a user asks for any information not available in Notion, politely tell them that you can only assist "
    "with content and actions available through the Notion MCP integration. "
    "Use the available MCP tools only for Notion operations like reading, writing, searching, or summarizing pages."
)

# ---------------------------------------------------------------------
# Log Initialization
# ---------------------------------------------------------------------                                         
logger.info("--- 🔧 Loading Notion MCP Tools... ---")
logger.info("--- 🤖 Creating ADK Notion Agent... ---")



# ---------------------------------------------------------------------
# Notion Api Key
# ---------------------------------------------------------------------                                         

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
if NOTION_API_KEY is None:
    raise ValueError("Environment variable NOTION_API_KEY is not set.")

NOTION_MCP_HEADERS = json.dumps(
    {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }
)

# ---------------------------------------------------------------------
# Create the Notion MCP Agent
# ---------------------------------------------------------------------
root_agent = Agent(
    model="gemini-2.5-pro",
    name="notion_agent",
    description="An agent that interacts with Notion using MCP to read and summarize workspace content",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command = "npx",
                    args = ["-y", "@notionhq/notion-mcp-server"],
                    env = {"OPENAPI_MCP_HEADERS": NOTION_MCP_HEADERS },
                ),
                timeout = 20,
            ),
        )
    ],
)

# ---------------------------------------------------------------------
# Log success
# ---------------------------------------------------------------------
logger.info("Notion MCP Agent created successfully and ready to connect.")

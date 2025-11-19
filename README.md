# Notion MCP Agent

This folder contains a small example Python ADK agent that connects to Notion using the MCP (Model Context Protocol) via a Stdio (stdin/stdout) MCP server process.

This README explains how the Notion MCP integration is used to create the agent, why a stdio connection is used, how the MCP process is launched, environment setup, and troubleshooting notes.

## What this agent does

- Instantiates a Gemini LLM-backed agent (via the ADK `Agent` class).
- Uses a Notion MCP server process (the official `@notionhq/notion-mcp-server`) launched via `npx`.
- Communicates with the MCP server over stdin/stdout using a Stdio connection (no network socket required).
- Supplies Notion API headers (including the Notion integration secret) to the MCP server via environment variables.

The agent source is `agent.py` in this folder. It creates an `Agent` with an `MCPToolset` configured to start and talk to the Notion MCP server using `StdioServerParameters`.

## Key implementation points

- Environment variable: `NOTION_API_KEY` must be provided. The agent converts it into the JSON `OPENAPI_MCP_HEADERS` expected by the MCP server.
- The MCP server is started with `npx -y @notionhq/notion-mcp-server`. This is done by the `StdioServerParameters.command` + `args` in `agent.py`.
- The `MCPToolset` is created with `StdioConnectionParams` so the Python process and MCP server exchange messages over the subprocess' stdin/stdout streams.

Example snippets from `agent.py` (conceptually):

- Build Notion headers:

  - `NOTION_API_KEY = os.getenv("NOTION_API_KEY")`
  - `NOTION_MCP_HEADERS = json.dumps({"Authorization": f"Bearer {NOTION_API_KEY}", "Notion-Version": "2022-06-28"})`

- Start the MCP server via stdio:

  - `command = "npx"`
  - `args = ["-y", "@notionhq/notion-mcp-server"]`
  - `env = {"OPENAPI_MCP_HEADERS": NOTION_MCP_HEADERS}`

  These are passed into `StdioServerParameters` which is used by `StdioConnectionParams` inside the `MCPToolset`.

## Why use a Stdio MCP connection?

- Simplicity: launching the MCP server as a local subprocess and talking over stdin/stdout avoids the need to expose a network port or host a separate MCP server.
- Security: the Notion API key is only passed to the child process via an environment variable and not exposed to the network (as long as the machine is secure).
- Good for development and testing: it's easy to spin up and tear down the MCP server automatically from your Python code.

For production, you can also run the MCP server independently (for example on a remote host) and use an HTTP/streaming connection instead.

## Prerequisites

- Python 3.13+ and a virtual environment for the project.
- Node.js and npm (or at least `npx`) installed and available on your PATH. The agent uses `npx` to run `@notionhq/notion-mcp-server`.
- A Notion Integration API key (the integration must have the required permissions for the pages/databases you want to read).

## Setup

1. Clone repositories and install dependencies

- Clone this repository (replace the URL with your project repo):

```powershell
# clone the project
git clone https://github.com/CHARLIE1210-A/adk_projects.git
```
```powershell
cd adk_projects
```

1. Create and activate a Python virtual environment, then install Python dependencies

If you use `uv` as your Python package manager and venv helper, create and activate the virtual environment and install packages with:

```powershell
# create and activate a venv using uv 
uv venv .venv

# install the local package (reads pyproject.toml)
uv install -e .
```

If you prefer the standard venv + pip approach, use:

```powershell
# create a venv and activate (PowerShell)
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# upgrade pip and install the local package (uses pyproject.toml)
pip install --upgrade pip
pip install -e .
```

3. Ensure Node.js / npx is available

```powershell
npx --version
```

Install Node.js/npm from https://nodejs.org/ if not present.

4. Provide Notion credentials

Set the `NOTION_API_KEY` environment variable before running the agent or a2a server. Example (PowerShell):

```powershell
$env:NOTION_API_KEY = "secret_your_notion_integration_token"
```

You can also place environment variables in a `.env` file and load them in your shell or with a dotenv tool.

5. Run the agent

From the repository root you can start the interactive web agent:

```powershell
adk web
```

This will launch the agent which starts the Notion MCP server via `npx -y @notionhq/notion-mcp-server` (or use the locally-cloned MCP server if you prefer).

6. Run the a2a server (agent-to-agent)

From the `notion_mcp_agent` package folder you can run the bundled a2a server (the ASGI app in `__main__.py`) using the convenience `uv` command if available:

```powershell
cd notion_mcp_agent
uv run __main.py
```

If `uv` is not available, run with `uvicorn`:

```powershell
uvicorn __main__:app --reload
```

If you cloned the Notion MCP server locally and prefer to run it directly, use the MCP server repo's README for that server's startup instructions (usually `npm start` or `npx` commands).

## Run the agent

From the parent repository root (or the folder containing the package), run the agent module. Example using PowerShell:

```powershell
# from parent repository root
adk web
```

When run, the Python code will:

1. Read `NOTION_API_KEY` and emit `OPENAPI_MCP_HEADERS` for the MCP server.
2. Launch `npx -y @notionhq/notion-mcp-server` as a subprocess.
3. Communicate with the MCP server using stdin/stdout.
4. Register MCP tools on the agent so it can perform Notion read/search/summarize actions when asked.

Note: The provided `agent.py` primarily wires up the agent and MCP toolset. You will typically call the agent's run loop or integrate it with your higher-level orchestration to send tasks/queries to it.

## Troubleshooting

- If the MCP server fails to start:
  - Ensure Node.js and `npx` are installed and on PATH.
  - Try running `npx -y @notionhq/notion-mcp-server` manually to see stderr output.
- If the agent can't access Notion:
  - Verify `NOTION_API_KEY` is set and the integration has access to the target pages/databases.
  - Validate the `Notion-Version` header if you rely on specific API behavior; the example uses `2022-06-28`.
- If the connection hangs or times out, consider increasing the `timeout` configured in `StdioConnectionParams`.

## Security and best practices

- Keep `NOTION_API_KEY` secret. Do not commit `.env` or API keys to source control.
- Use least-privilege integration scopes for Notion.
- For production use, consider running the MCP server in a managed or isolated environment and use a secure connection pattern appropriate for your deployment.

## Next steps and enhancements

- Add concrete example scripts that send sample MCP requests and show the agent summarizing a Notion page.
- Add unit/integration tests that mock the MCP server and verify the agent's tool wiring.
- Add an option to use a TCP/HTTP MCP connection instead of stdio for deployment scenarios.

## Where to look in the code

- `notion_mcp_agent/agent.py` — the code that creates the `Agent`, prepares `NOTION_MCP_HEADERS`, and configures `MCPToolset` with `StdioConnectionParams` and `StdioServerParameters`.

If you need an example of how to call the agent or how to wire the agent into a runtime loop, I can add a small runner script or tests next.

---

Created to document the Notion MCP stdio-based agent wiring and how to run it locally.

## Useful links

- Notion MCP server (source, docs, and examples): [Notion MCP server — GitHub](https://github.com/makenotion/notion-mcp-server)

## Agent-to-Agent (a2a) protocol and running the a2a server

- **Overview:** This project includes support for an agent-to-agent (a2a) protocol used for multi-agent coordination. The a2a protocol exchanges structured JSON messages (for example: `message_id`, `from`, `to`, `type`, `payload`, `signature`) between agents. Messages can be transported via Notion artifacts (e.g., a dedicated database) or through a lightweight a2a server implemented in this package.

- **Where the server lives:** A simple a2a server implementation is present in `notion_mcp_agent/__main__.py`.

- **How to run the a2a server:** From the `notion_mcp_agent` package root run the CLI command shown below (PowerShell example). This project exposes a convenience command assumed to be available as `uv`:

```powershell
uv run __main__.py
```

If the `uv` command is not available you can run the ASGI app directly with `uvicorn` (if installed):

```powershell
uvicorn __main__:app --reload
```

- **Environment:** Ensure `NOTION_API_KEY` (and any other required env vars) are set before starting the a2a server so agents can access Notion via the MCP adapter.

- **Agent executor:** See `notion_mcp_agent/agent_executor.py` — this file implements the executor logic used to receive a2a messages, validate and process them, invoke the local Notion-backed agent (via the MCP adapter), and send back status or results over the a2a channel. Use `agent_executor.py` as the runtime bridge between incoming a2a messages and the Notion agent functionality.

- **Typical multi-agent flow:**
  - Agent A creates a task message and posts it (via Notion DB entry or a2a server).
  - The a2a server or a polling agent picks up the message.
  - The recipient uses `agent_executor.py` to validate and execute the task using the Notion MCP toolset.
  - The recipient posts back a reply/status message (signed) so the originator can mark the task completed.

- **Security:** a2a messages should be signed and verified to prevent impersonation. Store keys and secrets securely (environment variables or a secrets manager) and run the a2a server in a trusted environment.

- **Troubleshooting:** If `uv run` is not found, install `uv` or `uvicorn` (`pip install uvicorn`) and use the `uvicorn` command shown above. If the server fails to start, check `NOTION_API_KEY`, port conflicts, and any traceback printed to stderr.

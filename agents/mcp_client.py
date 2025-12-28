import os
import sys
import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from agents.logger import setup_logger

log = setup_logger("MCP-CLIENT")


class MCPClient:
    def __init__(self):
        log.info("Initializing MCPClient")
        self._session = None
        self._cm = None
        self._bg_task = None

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

    def connect(self):
        if self._session:
            log.info("MCP already connected")
            return

        repo_root = os.path.dirname(os.path.dirname(__file__))
        script_path = os.path.join(repo_root, "mcp_server", "system_tools.py")

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"MCP server script not found: {script_path}")

        python_exe = sys.executable or "python"

        log.info(f"Starting MCP server: {python_exe} {script_path}")

        server = StdioServerParameters(
            command=python_exe,
            args=[script_path]
        )

        async def _connect():
            self._cm = stdio_client(server)
            session, bg_task = await self._cm.__aenter__()
            self._session = session
            self._bg_task = bg_task
            log.info("MCP session established")

        self._loop.run_until_complete(_connect())

    def call_tool(self, tool_name: str, arguments: dict = None):
        if not self._session:
            raise RuntimeError("MCP client not connected")

        log.info(f"Calling MCP tool: {tool_name} | args={arguments}")

        async def _call():
            return await self._session.call_tool(tool_name, arguments or {})

        result = self._loop.run_until_complete(_call())
        log.info(f"Tool '{tool_name}' returned: {result.content}")
        return result

    def close(self):
        if not self._session:
            return

        log.info("Closing MCP session")

        async def _close():
            await self._cm.__aexit__(None, None, None)

        self._loop.run_until_complete(_close())
        self._session = None

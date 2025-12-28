from langchain_ollama import OllamaLLM
from agents.prompts import SYSTEM_PROMPT
from agents.mcp_client import MCPClient
from agents.logger import setup_logger

log = setup_logger("AGENT")


class DevOpsAgent:
    def __init__(self):
        log.info("Initializing DevOpsAgent")

        self.llm = OllamaLLM(
            model="qwen2.5:7b-instruct",
            temperature=0
        )

        self.mcp_client = MCPClient()
        self.mcp_client.connect()

        log.info("DevOpsAgent ready")

    def think(self, message: str) -> str:
        log.info("LLM thinking started")
        log.debug(f"User message: {message}")

        prompt = f"""
{SYSTEM_PROMPT}

User issue:
{message}

Think step by step.
Decide which tools you need and why.
"""

        response = self.llm.invoke(prompt)

        log.info("LLM thinking finished")
        return response

    def collect_system_data(self):
        log.info("Collecting system data via MCP")

        data = {}

        try:
            result = self.mcp_client.call_tool("cpu_usage")
            data["cpu_usage"] = result.content
        except Exception as e:
            log.error(f"cpu_usage failed: {e}")
            data["cpu_usage_error"] = str(e)

        try:
            result = self.mcp_client.call_tool("memory_usage")
            data["memory_usage"] = result.content
        except Exception as e:
            log.error(f"memory_usage failed: {e}")
            data["memory_usage_error"] = str(e)

        try:
            result = self.mcp_client.call_tool("disk_usage")
            data["disk_usage"] = result.content
        except Exception as e:
            log.error(f"disk_usage failed: {e}")
            data["disk_usage_error"] = str(e)

        try:
            result = self.mcp_client.call_tool("top_processes", {"limit": 5})
            data["top_processes"] = result.content
        except Exception as e:
            log.error(f"top_processes failed: {e}")
            data["top_processes_error"] = str(e)

        log.info("System data collection finished")
        return data

    def analyze(self, user_message: str):
        log.info("Analysis started")

        reasoning = self.think(user_message)
        system_data = self.collect_system_data()

        log.info("Invoking LLM for final analysis")

        final_prompt = f"""
You are a DevOps AI agent.

User issue:
{user_message}

Your reasoning:
{reasoning}

System data collected via tools:
{system_data}

Provide:
- Root cause analysis
- Clear explanation
- Suggested next steps
"""

        response = self.llm.invoke(final_prompt)

        log.info("Analysis finished")
        return response
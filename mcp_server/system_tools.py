from mcp.server.fastmcp import FastMCP
import psutil
import logging
import json
import traceback

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | MCP-SERVER | %(message)s",
    datefmt="%H:%M:%S"
)

log = logging.getLogger("mcp-server")

mcp = FastMCP("system-tools")


# -------------------------------
# Helper: structured logging
# -------------------------------
def log_tool_call(tool_name: str, args: dict | None):
    log.info(f"▶ TOOL CALL: {tool_name} | args={args}")


def log_tool_result(tool_name: str, result):
    try:
        result_str = json.dumps(result, default=str)
    except Exception:
        result_str = str(result)

    log.info(f"◀ TOOL RESULT: {tool_name} -> {result_str}")


def log_tool_error(tool_name: str, exc: Exception):
    log.error(f"✖ TOOL ERROR: {tool_name} | {exc}")
    log.debug(traceback.format_exc())


# -------------------------------
# MCP tools
# -------------------------------
@mcp.tool()
def cpu_usage():
    tool = "cpu_usage"
    log_tool_call(tool, None)

    try:
        result = psutil.cpu_percent(interval=1)
        log_tool_result(tool, result)
        return result
    except Exception as e:
        log_tool_error(tool, e)
        raise


@mcp.tool()
def memory_usage():
    tool = "memory_usage"
    log_tool_call(tool, None)

    try:
        mem = psutil.virtual_memory()
        result = {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent
        }
        log_tool_result(tool, result)
        return result
    except Exception as e:
        log_tool_error(tool, e)
        raise


@mcp.tool()
def disk_usage():
    tool = "disk_usage"
    log_tool_call(tool, None)

    try:
        disk = psutil.disk_usage("/")
        result = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": disk.percent
        }
        log_tool_result(tool, result)
        return result
    except Exception as e:
        log_tool_error(tool, e)
        raise


@mcp.tool()
def top_processes(limit: int = 5):
    tool = "top_processes"
    log_tool_call(tool, {"limit": limit})

    try:
        processes = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(p.info)
            except Exception:
                pass

        processes = sorted(
            processes,
            key=lambda x: x.get("cpu_percent", 0),
            reverse=True
        )[:limit]

        log_tool_result(tool, processes)
        return processes
    except Exception as e:
        log_tool_error(tool, e)
        raise


# -------------------------------
# Server startup
# -------------------------------
if __name__ == "__main__":
    log.info("Starting MCP system-tools server")
    mcp.run()
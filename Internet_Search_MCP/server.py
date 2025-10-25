# ============================================================
# MCP Name      : Internet_Search_MCP
# Author        : ParisNeo
# Creation Date : 2025-10-26
# Description   : Provides a simple and effective tool for LLMs
#                 to perform internet searches using DuckDuckGo.
#                 It automatically manages its dependencies
#                 at startup using pipmaster.
# ============================================================

import argparse
import sys
import subprocess
from pathlib import Path
import yaml

# Use pipmaster to ensure dependencies are installed
try:
    import pipmaster as pm
except ImportError:
    print("Pipmaster not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pipmaster"], check=True)
    import pipmaster as pm

from mcp.server.fastmcp import FastMCP
from ascii_colors import ASCIIColors

# --- MCP Tool Dependencies ---
# List of required packages for the MCP tools to function correctly.
REQUIRED_PACKAGES = [
    "pyyaml",
    "ascii_colors",
    "fastmcp",
    "duckduckgo-search"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")

class MCPConfig:
    """
    Handles configuration loading for the MCP.
    """
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.config = {}
        self._load_config()

    def _load_config(self):
        config_path_yaml = self.base_path / "config.yaml"
        if config_path_yaml.exists():
            with config_path_yaml.open("r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}

    def get(self, key, default=None):
        return self.config.get(key, default)

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Internet Search MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9625, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()
config = MCPConfig(base_path=Path(__file__).parent)

mcp = FastMCP(
    name="InternetSearchMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="InternetSearchMCPServer")


@mcp.tool()
def internet_search(query: str, num_results: int = 5, region: str = "wt-wt") -> dict:
    """
    Performs an internet search using DuckDuckGo.

    Args:
        query: The search query.
        num_results: The maximum number of results to return.
        region: The region to search in (e.g., 'us-en', 'uk-en', 'de-de'). 'wt-wt' is world-wide.

    Returns:
        A dictionary containing a list of search results or an error message.
    """
    from duckduckgo_search import DDGS

    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, region=region, max_results=num_results)]

        formatted_results = [
            {
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body"),
            }
            for result in results
        ]
        return {"results": formatted_results}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("Internet Search MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
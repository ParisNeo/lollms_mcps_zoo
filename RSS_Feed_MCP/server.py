# ============================================================
# MCP Name      : RSS_Feed_MCP
# Author        : Your Name
# Creation Date : 2025-10-26
# Description   : Provides a tool for LLMs to check and retrieve
#                 the latest entries from pre-configured RSS feeds.
#                 Feeds are managed in the config.yaml file.
# ============================================================

import argparse
import sys
import subprocess
from pathlib import Path
import yaml
from datetime import datetime
import time

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
REQUIRED_PACKAGES = [
    "pyyaml",
    "ascii_colors",
    "fastmcp",
    "feedparser"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")

class MCPConfig:
    """Handles loading the config.yaml file for the MCP."""
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
            ASCIIColors.red("Warning: config.yaml not found. The RSS feed checker will have no feeds to check.")
            self.config = {'feeds': []}

    def get(self, key, default=None):
        return self.config.get(key, default)

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="RSS Feed MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9627, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()
config = MCPConfig(base_path=Path(__file__).parent)

mcp = FastMCP(
    name="RSSFeedMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="RSSFeedMCPServer")

@mcp.tool()
def check_rss_feeds(feed_name: str = None, max_entries: int = 5) -> dict:
    """
    Checks pre-configured RSS feeds and returns the latest entries.
    If no feed_name is provided, it checks all feeds.

    Args:
        feed_name: The specific name of the feed to check (must be in config.yaml).
        max_entries: The maximum number of entries to return per feed.

    Returns:
        A dictionary with the latest feed entries or an error message.
    """
    import feedparser

    configured_feeds = config.get("feeds", [])
    if not configured_feeds:
        return {"status": "error", "error": "No RSS feeds are configured in config.yaml."}

    feeds_to_check = []
    if feed_name:
        # Find the specific feed
        found_feed = next((f for f in configured_feeds if f.get("name") == feed_name), None)
        if not found_feed:
            return {"status": "error", "error": f"Feed '{feed_name}' not found in configuration."}
        feeds_to_check.append(found_feed)
    else:
        # Check all configured feeds
        feeds_to_check = configured_feeds

    all_results = {}
    for feed_info in feeds_to_check:
        try:
            feed_data = feedparser.parse(feed_info["url"])
            if feed_data.bozo:
                ASCIIColors.yellow(f"Warning: Ill-formed feed from {feed_info['name']}. Reason: {feed_data.bozo_exception}")

            entries = []
            for entry in feed_data.entries[:max_entries]:
                # Format published date to a standard string
                published_time = entry.get("published_parsed", time.gmtime())
                published_iso = datetime.fromtimestamp(time.mktime(published_time)).isoformat()

                entries.append({
                    "title": entry.get("title", "N/A"),
                    "link": entry.get("link", "N/A"),
                    "summary": entry.get("summary", "N/A"),
                    "published": published_iso
                })
            all_results[feed_info["name"]] = entries
        except Exception as e:
            all_results[feed_info["name"]] = {"error": f"Failed to fetch or parse feed: {str(e)}"}

    return {"status": "success", "feeds": all_results}

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("RSS Feed MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
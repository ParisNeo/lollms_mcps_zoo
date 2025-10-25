# ============================================================
# MCP Name      : ArXiv_Search_MCP
# Author        : ParisNeo
# Creation Date : 2025-10-26
# Description   : Provides a tool for LLMs to search for and
#                 retrieve academic papers from the arXiv repository.
#                 Automatically manages its dependencies at startup.
# ============================================================

import argparse
import sys
import subprocess
from pathlib import Path
import yaml
from datetime import datetime

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
# List of required packages for this MCP to function.
REQUIRED_PACKAGES = [
    "pyyaml",
    "ascii_colors",
    "fastmcp",
    "arxiv"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="ArXiv Search MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9626, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()

mcp = FastMCP(
    name="ArXivSearchMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="ArXivSearchMCPServer")


@mcp.tool()
def search_arxiv(query: str, max_results: int = 5) -> dict:
    """
    Searches the arXiv repository for academic papers.

    Args:
        query: The search query (e.g., "quantum computing", "author:hinton", "cat:cs.AI").
        max_results: The maximum number of results to return.

    Returns:
        A dictionary containing a list of found papers or an error message.
    """
    import arxiv

    try:
        # Construct the search object
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = []
        for result in search.results():
            # Format authors to a simple list of names
            author_names = [author.name for author in result.authors]

            results.append({
                "title": result.title,
                "authors": author_names,
                "summary": result.summary,
                "published_date": result.published.isoformat(),
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category
            })

        if not results:
            return {"status": "success", "message": "No results found for your query."}

        return {"status": "success", "results": results}

    except Exception as e:
        return {"status": "error", "error": f"An error occurred while querying the arXiv API: {str(e)}"}

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("ArXiv Search MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
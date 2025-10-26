# ============================================================
# MCP Name      : Advanced_Calculator_MCP
# Author        : ParisNeo
# Creation Date : 2025-10-26
# Description   : Provides a secure tool for LLMs to evaluate
#                 complex mathematical expressions. It uses the
#                 'asteval' library to prevent arbitrary code execution.
# ============================================================

import argparse
import sys
import subprocess
from pathlib import Path

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
    "asteval"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES)
    ASCIIColors.green("All dependencies are met.")

# After dependency check, import the main library
from asteval import Interpreter as SafeEvaluator

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Advanced Calculator MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9629, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()

mcp = FastMCP(
    name="AdvancedCalculatorMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="AdvancedCalculatorMCPServer")

# Create a single, reusable instance of the safe evaluator
safe_eval = SafeEvaluator()

@mcp.tool()
def calculate_expression(expression: str) -> dict:
    """
    Safely evaluates a mathematical expression string.

    Supports standard arithmetic, functions (sin, cos, sqrt, log, etc.),
    constants (pi, e), and more.

    Args:
        expression: The mathematical expression to evaluate (e.g., "sqrt(16) * (pi / 2)").

    Returns:
        A dictionary containing the numerical result or an error message.
    """
    try:
        # Evaluate the expression in the sandboxed interpreter
        result = safe_eval.eval(expression)
        ASCIIColors.green(f"Evaluated '{expression}' to: {result}")
        return {"status": "success", "result": result}
    except Exception as e:
        ASCIIColors.red(f"Failed to evaluate '{expression}': {e}")
        return {"status": "error", "error": f"Invalid expression or syntax: {str(e)}"}

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("Advanced Calculator MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
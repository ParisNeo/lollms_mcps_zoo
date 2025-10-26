# ============================================================
# MCP Name      : Symbolic_Math_MCP
# Author        : ParisNeo
# Creation Date : 2025-10-26
# Description   : Provides a suite of tools for LLMs to perform
#                 symbolic mathematics (algebra, calculus) using
#                 the SymPy library.
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
    "sympy"
]

def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")

# After dependency check, import sympy
from sympy import sympify, solve, expand, factor, diff, integrate, simplify
from sympy.parsing.sympy_parser import parse_expr

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Symbolic Math MCP Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9630, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()

mcp = FastMCP(
    name="SymbolicMathMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="SymbolicMathMCPServer")

def _handle_computation(func, *args, **kwargs):
    """A generic wrapper to handle SymPy computations and errors."""
    try:
        result = func(*args, **kwargs)
        # Convert SymPy objects to strings for JSON serialization
        if isinstance(result, list):
            str_result = [str(item) for item in result]
        else:
            str_result = str(result)
        return {"status": "success", "result": str_result}
    except Exception as e:
        return {"status": "error", "error": f"An error occurred: {str(e)}"}

@mcp.tool()
def solve_equation(equation: str, variable: str) -> dict:
    """Solves an algebraic equation for a given variable."""
    return _handle_computation(lambda: solve(parse_expr(equation), parse_expr(variable)))

@mcp.tool()
def simplify_expression(expression: str) -> dict:
    """Simplifies a mathematical expression."""
    return _handle_computation(lambda: simplify(parse_expr(expression)))

@mcp.tool()
def expand_expression(expression: str) -> dict:
    """Expands a mathematical expression."""
    return _handle_computation(lambda: expand(parse_expr(expression)))

@mcp.tool()
def factor_expression(expression: str) -> dict:
    """Factors a polynomial expression."""
    return _handle_computation(lambda: factor(parse_expr(expression)))

@mcp.tool()
def differentiate(expression: str, variable: str) -> dict:
    """Computes the derivative of an expression with respect to a variable."""
    return _handle_computation(lambda: diff(parse_expr(expression), parse_expr(variable)))

@mcp.tool()
def integrate_expression(expression: str, variable: str, lower_bound: str = None, upper_bound: str = None) -> dict:
    """
    Computes the integral of an expression.
    Performs indefinite integration if bounds are not provided.
    Performs definite integration if both lower and upper bounds are provided.
    """
    if lower_bound and upper_bound:
        # Definite integral
        integral_tuple = (parse_expr(variable), parse_expr(lower_bound), parse_expr(upper_bound))
        return _handle_computation(lambda: integrate(parse_expr(expression), integral_tuple))
    else:
        # Indefinite integral
        return _handle_computation(lambda: integrate(parse_expr(expression), parse_expr(variable)))

if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("Symbolic Math MCP Server")
    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
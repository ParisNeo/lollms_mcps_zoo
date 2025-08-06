# ============================================================
# MCP Name      : Coding_MCPs
# Author        : ParisNeo
# Creation Date : 2025-08-04
# Description   : Provides code execution and analysis tools for LLMs.
#                 WARNING: Code execution is performed in a controlled environment,
#                 but may still be risky. Use with caution.
#
#                 Configuration options:
#                 - timeout (int): Maximum execution time in seconds for code execution (default: 10).
#                 - Additional configuration fields can be defined in schema.config.json.
#                 - Environment variable mapping is supported via schema metadata.
# ============================================================

from mcp.server.fastmcp import FastMCP
import argparse
from ascii_colors import ASCIIColors
import subprocess
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import yaml
import os
import tempfile

class MCPConfig:
    """
    Handles configuration loading and merging for the MCP.
    Loads schema from schema.config.json, user config from config.yaml,
    applies defaults, and supports environment variable overrides.
    """
    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.schema = {}
        self.config = {}
        self._load_schema()
        self._load_config()
        self._apply_env_vars()

    def _load_schema(self):
        schema_path = self.base_path / "schema.config.json"
        if schema_path.exists():
            with schema_path.open("r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            self.schema = {}

    def _load_config(self):
        config_path_yaml = self.base_path / "config.yaml"
        if config_path_yaml.exists():
            with config_path_yaml.open("r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = {}
        # Apply schema defaults
        for key, meta in self.schema.get("properties", {}).items():
            if key not in self.config and "default" in meta:
                self.config[key] = meta["default"]

    def _apply_env_vars(self):
        for key, meta in self.schema.get("properties", {}).items():
            env_var = meta.get("envVar")
            if env_var and env_var in os.environ:
                self.config[key] = os.environ[env_var]

    def get(self, key, default=None):
        """
        Retrieve a configuration value, falling back to the provided default if not set.
        """
        return self.config.get(key, default)
    

def parse_args():
    """
    Parse command-line arguments for the MCP server.
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Coding MCPs Server configuration")
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Hostname or IP address (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9624,
        help="Port number (1-65535)"
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "streamable-http"],
        default="streamable-http",
        help="Transport protocol: stdio, sse, or streamable-http"
    )
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()
config = MCPConfig(base_path=Path(__file__).parent)

if args.transport == "streamable-http":
    mcp = FastMCP(
        name="CodingMCPServer",
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )
    ASCIIColors.cyan(f"{mcp.settings}")
else:
    mcp = FastMCP(
        name="CodingMCPServer"
    )

def install_libraries(libraries: Optional[List[str]], venv_path: Path):
    """
    Install Python libraries into the given virtual environment.

    Args:
        libraries (Optional[List[str]]): List of library names to install.
        venv_path (Path): Path to the virtual environment.
    """
    if not libraries:
        return
    pip_exe = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"
    for lib in libraries:
        try:
            subprocess.run([str(pip_exe), "install", lib], check=True, capture_output=True)
        except Exception as e:
            ASCIIColors.red(f"Error installing {lib}: {e}")

@mcp.tool(
    name="run_python_code",
    description="Executes provided Python code in a controlled environment and returns the output or error. Optionally installs extra libraries before execution.",
)
async def run_python_code(code: str, extra_libraries: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Executes Python code in a temporary isolated virtual environment.

    Args:
        code (str): The Python code to execute.
        extra_libraries (Optional[List[str]]): List of additional libraries to install before execution.

    Returns:
        Dict[str, Any]: Dictionary containing stdout, stderr, and returncode, or error message.
    """
    timeout = int(config.get("timeout", 10))
    with tempfile.TemporaryDirectory() as tmpdirname:
        venv_path = Path(tmpdirname) / "venv"
        # Create an isolated virtual environment
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        install_libraries(extra_libraries, venv_path)
        python_exe = venv_path / "Scripts" / "python.exe" if os.name == "nt" else venv_path / "bin" / "python"
        try:
            completed = subprocess.run(
                [str(python_exe), "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Timeout ({timeout}s) exceeded during code execution."}
        except Exception as e:
            return {"error": str(e)}

@mcp.tool(
    name="format_python_code",
    description="Formats Python code using 'black' if available."
)
async def format_python_code(code: str) -> Dict[str, Any]:
    """
    Format Python code using the 'black' formatter.

    Args:
        code (str): The Python code to format.

    Returns:
        Dict[str, Any]: Dictionary containing the formatted code or an error message.
    """
    try:
        import black
        formatted = black.format_str(code, mode=black.Mode())
        return {"formatted_code": formatted}
    except ImportError:
        return {"error": "The 'black' module is not installed."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    name="check_python_syntax",
    description="Checks the syntax of Python code."
)
async def check_python_syntax(code: str) -> Dict[str, Any]:
    """
    Check the syntax of Python code.

    Args:
        code (str): The Python code to check.

    Returns:
        Dict[str, Any]: Dictionary indicating if the syntax is valid or containing the error.
    """
    import ast
    try:
        ast.parse(code)
        return {"syntax_ok": True}
    except SyntaxError as e:
        return {"syntax_ok": False, "error": str(e)}

@mcp.tool(
    name="check_python_syntax_compile",
    description="Checks the syntax of Python code using Python's built-in compile function."
)
async def check_python_syntax_compile(code: str) -> Dict[str, Any]:
    """
    Check the syntax of Python code using the built-in compile function.

    Args:
        code (str): The Python code to check.

    Returns:
        Dict[str, Any]: Dictionary indicating if the syntax is valid or containing the error.
    """
    try:
        compile(code, "<string>", "exec")
        return {"syntax_ok": True}
    except SyntaxError as e:
        return {"syntax_ok": False, "error": str(e)}

@mcp.tool(
    name="extract_imports",
    description="Extracts the list of imported modules from Python code."
)
async def extract_imports(code: str) -> Dict[str, Any]:
    """
    Extract the list of imported modules from Python code.

    Args:
        code (str): The Python code to analyze.

    Returns:
        Dict[str, Any]: Dictionary containing a list of imported modules.
    """
    import ast
    try:
        tree = ast.parse(code)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        return {"imports": sorted(list(imports))}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    name="lint_python_code",
    description="Lints Python code using flake8 if available."
)
async def lint_python_code(code: str) -> Dict[str, Any]:
    """
    Lint Python code using flake8.

    Args:
        code (str): The Python code to lint.

    Returns:
        Dict[str, Any]: Dictionary containing linting results or an error message.
    """
    import tempfile
    try:
        import flake8.api.legacy as flake8
    except ImportError:
        return {"error": "The 'flake8' module is not installed."}
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmpfile:
        tmpfile.write(code)
        tmpfile_path = tmpfile.name
    style_guide = flake8.get_style_guide(ignore=['E501'])
    report = style_guide.check_files([tmpfile_path])
    results = []
    for error in report.get_statistics(''):
        results.append(error)
    os.unlink(tmpfile_path)
    return {"lint_results": results, "total_errors": report.total_errors}

@mcp.tool(
    name="calculate_code_complexity",
    description="Calculates code complexity metrics using radon if available."
)
async def calculate_code_complexity(code: str) -> Dict[str, Any]:
    """
    Calculate code complexity metrics using radon.

    Args:
        code (str): The Python code to analyze.

    Returns:
        Dict[str, Any]: Dictionary containing complexity metrics or an error message.
    """
    try:
        from radon.complexity import cc_visit
    except ImportError:
        return {"error": "The 'radon' module is not installed."}
    try:
        results = cc_visit(code)
        complexity = [
            {
                "name": item.name,
                "type": item.type,
                "lineno": item.lineno,
                "col_offset": item.col_offset,
                "complexity": item.complexity
            }
            for item in results
        ]
        return {"complexity": complexity}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    ASCIIColors.cyan("MCP server will list tools upon connection.")
    ASCIIColors.cyan(f"Listening for MCP messages on {mcp.run(transport=args.transport)}...")
    mcp.run(transport=args.transport)

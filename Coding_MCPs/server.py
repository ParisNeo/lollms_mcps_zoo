# ============================================================
# MCP Name      : Self_Sufficient_Coding_MCPs
# Author        : ParisNeo (Reworked by an LLM with pipmaster)
# Creation Date : 2025-08-04
# Rework Date   : 2025-10-26
# Description   : Provides a secure, feature-rich, and self-sufficient
#                 suite of code execution and analysis tools for LLMs.
#                 It automatically verifies and installs its own dependencies
#                 at startup using pipmaster.
#
#                 WARNING: Code execution is performed in a more controlled
#                 environment, but executing untrusted code always carries
#                 inherent risks. Use with caution.
#
#                 Configuration options:
#                 - timeout (int): Maximum execution time in seconds for code execution (default: 30).
#                 - max_output_size (int): Maximum size of stdout/stderr in bytes (default: 10240).
# ============================================================

import argparse
import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use pipmaster to ensure dependencies are installed
try:
    import pipmaster as pm
except ImportError:
    print("Pipmaster not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pipmaster"], check=True)
    import pipmaster as pm


import yaml
from ascii_colors import ASCIIColors
from mcp.server.fastmcp import FastMCP

# --- Security Sandboxing (using seccomp on Linux) ---
try:
    import seccomp
except ImportError:
    seccomp = None

def setup_sandbox():
    """Configures a seccomp-based sandbox to restrict available syscalls."""
    if seccomp:
        f = seccomp.SyscallFilter(defaction=seccomp.KILL)
        # Whitelist necessary syscalls for basic Python execution
        syscalls_whitelist = [
            "read", "write", "open", "close", "stat", "fstat", "lseek",
            "mmap", "munmap", "brk", "access", "exit_group", "execve"
        ]
        for sc in syscalls_whitelist:
            f.add_rule(seccomp.ALLOW, sc)
        f.load()

class MCPConfig:
    """
    Handles configuration loading and merging for the MCP.
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

    def _load_config(self):
        config_path_yaml = self.base_path / "config.yaml"
        if config_path_yaml.exists():
            with config_path_yaml.open("r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
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
        return self.config.get(key, default)

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Self-Sufficient Coding MCPs Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9624, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

# --- MCP Tool Dependencies ---
# List of required packages for the MCP tools to function correctly.
REQUIRED_PACKAGES = [
    "pyyaml",
    "ascii_colors",
    "black",
    "flake8",
    "bandit",
    "safety",
    "packaging",
    "mypy",
    "radon"
]
if sys.platform == "linux":
    REQUIRED_PACKAGES.append("seccomp")


def check_and_install_dependencies():
    """Uses pipmaster to verify and install all required packages."""
    ASCIIColors.cyan("Checking for required dependencies...")
    pm.ensure_packages(REQUIRED_PACKAGES, upgrade=True)
    ASCIIColors.green("All dependencies are met.")


args = parse_args()
config = MCPConfig(base_path=Path(__file__).parent)

mcp = FastMCP(
    name="SelfSufficientCodingMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="SelfSufficientCodingMCPServer")


# --- MCP Tools ---

@mcp.tool()
async def run_python_code(code: str, extra_libraries: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Executes Python code in an isolated, sandboxed environment and returns the output.
    - code: The Python code to execute.
    - extra_libraries: A list of additional libraries to install before execution.
    Returns a JSON object with stdout, stderr, returncode, or an error message.
    """
    timeout = int(config.get("timeout", 30))
    max_output_size = int(config.get("max_output_size", 10240))

    with tempfile.TemporaryDirectory() as tmpdirname:
        venv_path = Path(tmpdirname) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True, capture_output=True)

        pip_exe = venv_path / "bin" / "pip" if os.name != 'nt' else venv_path / "Scripts" / "pip.exe"
        if extra_libraries:
            for lib in extra_libraries:
                subprocess.run([str(pip_exe), "install", lib], check=True, capture_output=True)

        python_exe = venv_path / "bin" / "python" if os.name != 'nt' else venv_path / "Scripts" / "python.exe"
        
        preexec_fn = setup_sandbox if seccomp and sys.platform != 'win32' else None

        try:
            completed = subprocess.run(
                [str(python_exe), "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=preexec_fn
            )
            stdout = completed.stdout[:max_output_size]
            stderr = completed.stderr[:max_output_size]
            return {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": completed.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Timeout ({timeout}s) exceeded during code execution."}
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def format_python_code(code: str) -> Dict[str, Any]:
    """Formats Python code using 'black' and returns the formatted code."""
    import black
    try:
        formatted_code = black.format_str(code, mode=black.Mode())
        return {"status": "success", "formatted_code": formatted_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def check_python_syntax(code: str) -> Dict[str, Any]:
    """Checks Python code for syntax errors and returns a validation status."""
    try:
        ast.parse(code)
        compile(code, "<string>", "exec")
        return {"status": "success", "syntax_ok": True}
    except SyntaxError as e:
        return {"status": "error", "syntax_ok": False, "error": str(e)}

@mcp.tool()
async def security_check(code: str) -> Dict[str, Any]:
    """Performs a static security analysis on Python code using 'bandit'."""
    from bandit.core import manager
    try:
        b_mgr = manager.BanditManager(None, "custom")
        b_mgr.discover_files([code], is_string=True)
        b_mgr.run_tests()
        results = [issue.as_dict() for issue in b_mgr.get_issue_list()]
        return {"status": "success", "issues": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def lint_python_code(code: str) -> Dict[str, Any]:
    """Lints Python code using 'flake8' and returns a list of issues found."""
    from flake8.api import legacy as flake8
    try:
        style_guide = flake8.get_style_guide()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        report = style_guide.check_files([tmp_path])
        os.unlink(tmp_path)
        
        results = []
        # The report.get_statistics('') returns a list of strings, not structured data.
        # We need to parse them. A better approach is to use a custom formatter,
        # but for simplicity, we process the raw report lines.
        for line in report.get_raw_errors():
             parts = line.split(':')
             if len(parts) >= 4:
                 results.append({
                     "file": parts[0],
                     "line": int(parts[1]),
                     "col": int(parts[2]),
                     "text": parts[3].strip()
                 })

        return {"status": "success", "lint_results": results, "total_errors": report.total_errors}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def analyze_dependencies(requirements_txt: str) -> Dict[str, Any]:
    """Analyzes a requirements.txt file for known security vulnerabilities using 'safety'."""
    import safety
    import packaging.requirements
    try:
        reqs = [str(r) for r in packaging.requirements.parse(requirements_txt)]
        vulnerabilities = safety.check(packages=reqs)
        return {
            "status": "success",
            "vulnerabilities": [v._asdict() for v in vulnerabilities],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def check_type_hints(code: str) -> Dict[str, Any]:
    """Performs static type checking on Python code using 'mypy'."""
    from mypy import api
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        stdout, stderr, exit_status = api.run([tmp_path])
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "stdout": stdout,
            "stderr": stderr,
            "exit_status": exit_status,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def calculate_code_complexity(code: str) -> Dict[str, Any]:
    """Calculates code complexity metrics using 'radon'."""
    from radon.complexity import cc_visit
    try:
        results = cc_visit(code)
        complexity = [
            {
                "name": item.name,
                "type": item.type,
                "lineno": item.lineno,
                "col_offset": item.col_offset,
                "complexity": item.complexity,
                "rank": item.rank
            }
            for item in results
        ]
        return {"status": "success", "complexity": complexity}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    check_and_install_dependencies()
    ASCIIColors.cyan("Self-Sufficient Coding MCP Server")
    if seccomp is None and os.name == 'posix':
        ASCIIColors.red("Warning: 'seccomp' library not found. Code execution sandboxing will be limited.")
        ASCIIColors.red("For better security on Linux, please run: pip install seccomp")

    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
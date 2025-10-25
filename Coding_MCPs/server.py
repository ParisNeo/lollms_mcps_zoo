# ============================================================
# MCP Name      : Enhanced_Coding_MCPs
# Author        : ParisNeo (Reworked by an LLM)
# Creation Date : 2025-08-04
# Rework Date   : 2025-10-26
# Description   : Provides a more secure and feature-rich suite of code
#                 execution and analysis tools for LLMs.
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
        # Default action is to kill the process
        f = seccomp.SyscallFilter(defaction=seccomp.KILL)

        # Whitelist necessary syscalls for basic Python execution
        f.add_rule(seccomp.ALLOW, "read")
        f.add_rule(seccomp.ALLOW, "write")
        f.add_rule(seccomp.ALLOW, "open")
        f.add_rule(seccomp.ALLOW, "close")
        f.add_rule(seccomp.ALLOW, "stat")
        f.add_rule(seccomp.ALLOW, "fstat")
        f.add_rule(seccomp.ALLOW, "lseek")
        f.add_rule(seccomp.ALLOW, "mmap")
        f.add_rule(seccomp.ALLOW, "munmap")
        f.add_rule(seccomp.ALLOW, "brk")
        f.add_rule(seccomp.ALLOW, "access")
        f.add_rule(seccomp.ALLOW, "exit_group")
        f.add_rule(seccomp.ALLOW, "execve")

        f.load()
        ASCIIColors.yellow("Seccomp sandbox enabled.")

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
        return self.config.get(key, default)

def parse_args():
    """Parse command-line arguments for the MCP server."""
    parser = argparse.ArgumentParser(description="Enhanced Coding MCPs Server")
    parser.add_argument("--host", type=str, default="localhost", help="Hostname or IP address")
    parser.add_argument("--port", type=int, default=9624, help="Port number")
    parser.add_argument("--log-level", dest="log_level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Logging level")
    parser.add_argument("--transport", type=str, choices=["stdio", "sse", "streamable-http"], default="streamable-http", help="Transport protocol")
    args = parser.parse_args()
    if not (1 <= args.port <= 65535):
        parser.error("Port must be between 1 and 65535")
    return args

args = parse_args()
config = MCPConfig(base_path=Path(__file__).parent)

mcp = FastMCP(
    name="EnhancedCodingMCPServer",
    host=args.host,
    port=args.port,
    log_level=args.log_level
) if args.transport == "streamable-http" else FastMCP(name="EnhancedCodingMCPServer")

def _run_tool_in_subprocess(tool_command: List[str], input_data: str, timeout: int) -> Dict[str, Any]:
    """Helper to run a tool in a separate process with a timeout."""
    try:
        process = subprocess.run(
            tool_command,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        if process.returncode == 0:
            return {"status": "success", "result": json.loads(process.stdout)}
        else:
            return {"status": "error", "error": process.stderr}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": f"Timeout ({timeout}s) exceeded."}
    except json.JSONDecodeError:
        return {"status": "error", "error": "Failed to decode JSON output from tool."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

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

        pip_exe = venv_path / "bin" / "pip"
        if extra_libraries:
            for lib in extra_libraries:
                subprocess.run([str(pip_exe), "install", lib], check=True, capture_output=True)

        python_exe = venv_path / "bin" / "python"
        
        # Using a pre-execution hook for sandboxing if seccomp is available
        preexec_fn = setup_sandbox if seccomp else None

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
    try:
        import black
        formatted_code = black.format_str(code, mode=black.Mode())
        return {"status": "success", "formatted_code": formatted_code}
    except ImportError:
        return {"status": "error", "error": "'black' is not installed. Please install it."}
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
    try:
        from bandit.core import manager
        b_mgr = manager.BanditManager(None, "custom")
        b_mgr.discover_files([code], is_string=True)
        b_mgr.run_tests()
        results = [issue.as_dict() for issue in b_mgr.get_issue_list()]
        return {"status": "success", "issues": results}
    except ImportError:
        return {"status": "error", "error": "'bandit' is not installed. Please install it."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
async def lint_python_code(code: str) -> Dict[str, Any]:
    """Lints Python code using 'flake8' and returns a list of issues found."""
    try:
        from flake8.api import legacy as flake8
        style_guide = flake8.get_style_guide()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        report = style_guide.check_files([tmp_path])
        os.unlink(tmp_path)
        results = [{"code": err[2], "line": err[0], "col": err[1], "text": err[3]} for err in report.get_statistics("")]
        return {"status": "success", "lint_results": results, "total_errors": report.total_errors}
    except ImportError:
        return {"status": "error", "error": "'flake8' is not installed. Please install it."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def analyze_dependencies(requirements_txt: str) -> Dict[str, Any]:
    """
    Analyzes a requirements.txt file for known security vulnerabilities.
    - requirements_txt: A string containing the contents of a requirements.txt file.
    Returns a JSON object with a list of vulnerable dependencies.
    """
    try:
        import safety
        import packaging.requirements
        
        reqs = [str(r) for r in packaging.requirements.parse(requirements_txt)]
        vulnerabilities = safety.check(packages=reqs)
        
        return {
            "status": "success",
            "vulnerabilities": [
                {
                    "package": v.pkg,
                    "spec": v.spec,
                    "version": v.ver,
                    "advisory": v.reason,
                    "id": v.vuln_id,
                }
                for v in vulnerabilities
            ],
        }
    except ImportError:
        return {"status": "error", "error": "'safety' or 'packaging' is not installed. Please install them."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def check_type_hints(code: str) -> Dict[str, Any]:
    """
    Performs static type checking on Python code using 'mypy'.
    - code: The Python code to type check.
    Returns a JSON object with the mypy output.
    """
    try:
        from mypy import api
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        result = api.run([tmp_path])
        os.unlink(tmp_path)
        
        stdout, stderr, exit_status = result
        
        return {
            "status": "success",
            "stdout": stdout,
            "stderr": stderr,
            "exit_status": exit_status,
        }
    except ImportError:
        return {"status": "error", "error": "'mypy' is not installed. Please install it."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    ASCIIColors.cyan("Enhanced Coding MCP Server")
    if seccomp is None and os.name == 'posix':
        ASCIIColors.red("Warning: 'seccomp' library not found. Code execution sandboxing will be limited.")
        ASCIIColors.red("For better security on Linux, please run: pip install seccomp")

    ASCIIColors.cyan(f"Starting server on {args.host}:{args.port} using {args.transport} transport.")
    mcp.run(transport=args.transport)
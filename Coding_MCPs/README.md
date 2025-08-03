# Coding_MCPs

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**Coding_MCPs** is a Management Component Plugin (MCP) for the [lollms](https://github.com/ParisNeo/lollms) ecosystem.  
It provides secure code execution, formatting, and syntax analysis tools for LLMs, enabling advanced coding workflows and automation.

---

## Features

- **Safe Python code execution** in a temporary, isolated virtual environment
- **Automatic installation of extra libraries** before code execution
- **Code formatting** using [black](https://github.com/psf/black)
- **Syntax checking** for Python code
- **Schema-driven configuration** with UI support in lollms
- **Environment variable mapping** for sensitive or dynamic configuration

---

## Configuration

This MCP uses a schema-driven configuration system:

- `schema.config.json` — Defines configuration fields, types, defaults, and environment variable mapping.
- `config.yaml` — Stores user configuration values.

### Example configuration options

- `timeout` (int): Maximum execution time in seconds for code execution (default: 10).  
  Can be set in `config.yaml` or via the `CODING_MCP_TIMEOUT` environment variable.

---

## Usage

1. **Configure the MCP**  
   Edit `config.yaml` to set your desired options, or set environment variables as needed.

2. **Start the MCP server**  
   ```bash
   python server.py
   ```

3. **Interact via lollms**  
   The MCP exposes tools for code execution, formatting, and syntax checking to LLMs through the lollms manager.

---

## Security

- All code execution happens in a temporary, isolated Python virtual environment.
- Extra libraries are installed only in the temporary environment.
- Execution is time-limited (see `timeout`).
- The environment is deleted after each run.
- **Warning:** While these measures improve safety, running arbitrary code is never fully risk-free. Use with caution.

---

## File Structure

- `server.py` — Main MCP server code
- `schema.config.json` — Configuration schema
- `config.yaml` — Default/user configuration
- `requirements.txt` — Python dependencies

---

## Extending

You can add new configuration fields by editing `schema.config.json` and updating `server.py` to use them.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).
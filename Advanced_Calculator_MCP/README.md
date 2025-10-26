# Advanced_Calculator_MCP

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**Advanced_Calculator_MCP** is a Model Context Protocol (MCP) server for the [lollms](https://github.com/ParisNeo/lollms) ecosystem. It provides a secure and powerful calculator for Large Language Models (LLMs), allowing them to evaluate complex mathematical expressions that go far beyond basic arithmetic.

## Features

-   **Complex Expressions:** Solves expressions with proper order of operations, parentheses, and nested functions (e.g., `(5 + 3) * sqrt(9)`).
-   **Rich Function Library:** Includes a wide range of mathematical functions like `sin`, `cos`, `tan`, `log`, `log10`, `sqrt`, `abs`, and more.
-   **Built-in Constants:** Understands common constants like `pi` and `e`.
-   **Secure by Design:** Uses the `asteval` library to create a secure sandbox for evaluation. This **prevents the execution of arbitrary Python code**, a critical security risk present in tools that use Python's built-in `eval()`.
-   **Self-Sufficient:** Automatically installs all dependencies on first run using `pipmaster`.

---

## Configuration

This MCP is ready to use out-of-the-box and does not require any configuration.

---

## Usage

1.  **Start the MCP server**  
    The script will handle dependency installation and then launch the server.
    ```bash
    python advanced_calculator_mcp.py
    ```

2.  **Interact via lollms**  
    The MCP exposes the `calculate_expression` tool. An LLM can now solve complex math problems by passing a string to this tool.

    **Example Calls:**
    -   Basic arithmetic with order of operations:  
        `{"tool": "calculate_expression", "expression": "100 / (5 * (2 + 2))"}`
    -   Using functions and constants:  
        `{"tool": "calculate_expression", "expression": "sin(pi / 2) + log(e)"}`
    -   Exponents (using Python's `**` operator):  
        `{"tool": "calculate_expression", "expression": "2**10 - 1"}`

---

## Security

The primary design consideration for this tool is security. Standard Python `eval()` is dangerous because it can execute any command the user passes, such as deleting files (`os.system('rm -rf /')`). This MCP avoids that risk entirely by using `asteval`, which only allows mathematical operations and has no access to the underlying operating system or filesystem.

---

## File Structure

-   `advanced_calculator_mcp.py` — The main MCP server script.
-   `description.yml` — Metadata for integration with the lollms manager.
-   `requirements.txt` — A list of Python dependencies (handled automatically).
-   `README.md` — This documentation file.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).
# ArXiv_Search_MCP

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**ArXiv_Search_MCP** is a Model Context Protocol (MCP) server for the [lollms](https://github.com/ParisNeo/lollms) ecosystem. It empowers Large Language Models (LLMs) with the ability to search for and retrieve information about academic papers from the [arXiv.org](https://arxiv.org/) repository, a premier open-access archive for scholarly articles.

---

## Features

-   **Direct ArXiv Access:** Queries the official arXiv API to find papers by keywords, authors, or categories.
-   **Structured Data:** Returns detailed, easy-to-parse JSON output, including title, authors, summary, publication date, and a direct PDF link.
-   **Self-Contained:** Uses `pipmaster` to automatically check and install all necessary dependencies on startup. No manual setup is required.
-   **No API Key Needed:** The arXiv API is public, allowing for immediate, hassle-free use.

---

## Configuration

This MCP is designed to run without any specific configuration. The default settings are sufficient for general use.

---

## Usage

1.  **Start the MCP server**  
    The script will first ensure all dependencies are installed before launching the server.
    ```bash
    python arxiv_search_mcp.py
    ```

2.  **Interact via lollms**  
    Once running, the MCP exposes the `search_arxiv` tool to the LLM. The LLM can then use this tool to find academic research to answer user prompts, summarize papers, or provide citations.

    Example queries an LLM might use:
    - `{"query": "large language models"}`
    - `{"query": "au:Yann LeCun", "max_results": 3}`
    - `{"query": "cat:cs.CV AND efficient transformers"}`

---

## Disclaimer

-   This tool is a client for the public arXiv API and is subject to their terms of service and rate limits.
-   The availability and performance of this tool are dependent on the status of the arXiv API servers.
-   All content retrieved is the property of the respective authors and is made available through arXiv's open-access initiative.

---

## File Structure

-   `arxiv_search_mcp.py` — The main MCP server script.
-   `description.yml` — Metadata for integration with the lollms manager.
-   `requirements.txt` — A list of Python dependencies (handled automatically by the server).
-   `README.md` — This documentation file.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).
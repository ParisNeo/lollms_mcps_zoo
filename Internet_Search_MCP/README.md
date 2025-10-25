# Internet_Search_MCP

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**Internet_Search_MCP** is a Model Context Protocol (MCP) server for the [lollms](https://github.com/ParisNeo/lollms) ecosystem. It provides Large Language Models (LLMs) with a powerful tool to perform real-time internet searches using the DuckDuckGo search engine. This enables LLMs to access current information, answer questions about recent events, and broaden their knowledge base beyond their training data.

---

## Features

- **Real-Time Web Search:** Connects to the internet via the `duckduckgo-search` library.
- **No API Key Required:** Offers hassle-free setup and usage without the need for credentials.
- **Customizable Searches:** Allows specifying the number of results and the search region for more targeted queries.
- **Self-Sufficient:** Automatically verifies and installs all required dependencies at startup using `pipmaster`.
- **Structured Output:** Returns clean JSON-formatted results, making it easy for LLMs to parse and use the information.

---

## Configuration

This MCP is designed to work out-of-the-box and does not require any API keys or complex setup. It uses a standard configuration file structure, but you do not need to edit `config.yaml` for the server to function.

- `config.yaml` — Stores user configuration values (optional).

---

## Usage

1.  **Start the MCP server**  
    The server will first check and install its dependencies, then launch.
    ```bash
    python internet_search_mcp.py
    ```

2.  **Interact via lollms**  
    Once running, the MCP exposes the `internet_search` tool to the LLM through the lollms manager, allowing it to perform searches as needed to answer prompts.

---

## Disclaimer

- This tool connects to the live internet to fetch information. The content from external websites is not filtered.
- The accuracy, reliability, and safety of the information returned by the search engine cannot be guaranteed.
- It is recommended to use this tool responsibly and to critically evaluate the search results provided to and by the LLM.

---

## File Structure

- `internet_search_mcp.py` — Main MCP server code
- `description.yml` — Metadata for the lollms manager
- `requirements.txt` — Python dependencies (managed automatically by the server)
- `README.md` — This documentation file

---

## Extending

You can extend this MCP by adding new tools to the `internet_search_mcp.py` script. For example, you could add tools for image or news searches by expanding the use of the `duckduckgo-search` library.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).
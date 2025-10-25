# RSS_Feed_MCP

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**RSS_Feed_MCP** is a Model Context Protocol (MCP) server for the [lollms](https://github.com/ParisNeo/lollms) ecosystem. It provides a powerful tool for Large Language Models (LLMs) to read and retrieve the latest entries from a pre-configured list of RSS feeds. This enables the LLM to stay up-to-date with news sites, blogs, project updates, or any other source that provides an RSS feed.

---

## Features

-   **User-Configurable Feeds:** Easily add, edit, or remove RSS feeds by modifying a simple `config.yaml` file.
-   **Check All or Specific Feeds:** The LLM can request updates from all configured feeds at once or query a specific feed by its friendly name.
-   **Structured JSON Output:** Returns clean, predictable JSON that is easy for an LLM to parse, including title, link, summary, and publication date for each entry.
-   **Self-Sufficient:** Automatically installs its own dependencies (`feedparser`, etc.) on first run using `pipmaster`.

---

## Configuration

This MCP's primary feature is its configuration. To add your own feeds, edit the `config.yaml` file. The file should contain a list of `feeds`. Each feed is a dictionary with two keys:

-   `name`: A user-friendly name that the LLM will use to identify the feed.
-   `url`: The full URL to the RSS feed XML file.

### Example `config.yaml`:

```yaml
feeds:
  - name: "BBC World News"
    url: "http://feeds.bbci.co.uk/news/world/rss.xml"

  - name: "Hacker News"
    url: "https://hnrss.org/frontpage"
```

---

## Usage

1.  **Configure Your Feeds**  
    Edit `config.yaml` to include the RSS feeds you are interested in.

2.  **Start the MCP server**  
    The script will install dependencies if needed, then start the server.
    ```bash
    python rss_feed_mcp.py
    ```

3.  **Interact via lollms**  
    The MCP exposes the `check_rss_feeds` tool. The LLM can now use this to fetch updates.

    -   To check all feeds: `{"tool": "check_rss_feeds"}`
    -   To check a specific feed: `{"tool": "check_rss_feeds", "feed_name": "Hacker News"}`
    -   To limit the number of entries: `{"tool": "check_rss_feeds", "feed_name": "BBC World News", "max_entries": 3}`

---

## Disclaimer

-   This tool's functionality depends entirely on the availability and proper formatting of the external RSS feeds listed in your configuration.
-   If a website changes its RSS feed URL or takes it down, the tool will fail for that specific feed.
-   The content and accuracy of the information retrieved are the sole responsibility of the feed provider.

---

## File Structure

-   `rss_feed_mcp.py` — The main MCP server script.
-   `config.yaml` — The user-configurable list of RSS feeds.
-   `description.yml` — Metadata for the lollms manager.
-   `requirements.txt` — A list of Python dependencies (handled automatically).
-   `README.md` — This documentation file.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).
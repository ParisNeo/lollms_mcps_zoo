# lollms_mcps_zoo

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/network)
[![Last Commit](https://img.shields.io/github/last-commit/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/commits/main)

A **zoo** for [lollms](https://github.com/ParisNeo/lollms) compatible Model Context Protocols (MCPs).

---

## Overview

**lollms_mcps_zoo** is a centralized repository for MCPs (Model Context Protocols) designed to extend the capabilities of LLMs (Large Language Models) within the lollms ecosystem. This repository aims to host hundreds of MCPs, each providing specialized tools, APIs, or environment access for LLMs.

- **Plug-and-play:** Easily add or update MCPs for your lollms instance.
- **Standardized:** All MCPs follow the lollms MCP interface and configuration schema.
- **Extensible:** Contribute your own MCPs to the zoo!

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ParisNeo/lollms_mcps_zoo.git
cd lollms_mcps_zoo
```

### 2. Explore available MCPs

Each MCP is located in its own subdirectory. For example:

- `Coding_MCPs/` — Provides code execution and analysis tools for LLMs.

Each MCP contains:
- `server.py` — The main MCP server code.
- `schema.config.json` — Configuration schema for the MCP.
- `config.yaml` — Default configuration.
- `requirements.txt` — Python dependencies.

### 3. Usage

Refer to each MCP's README or documentation for usage instructions.  
To use an MCP, follow the instructions in its directory and ensure it is properly configured.

---

## Contributing

Want to add your own MCP?  
Fork the repo, add your MCP in a new folder, and submit a pull request!

Please ensure your MCP:
- Follows the lollms MCP interface.
- Includes a `schema.config.json` and `config.yaml`.
- Has a clear description and documentation.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

---

## Links

- [lollms main repository](https://github.com/ParisNeo/lollms)
- [ParisNeo on GitHub](https://github.com/ParisNeo)
- [lollms_mcps_zoo on GitHub](https://github.com/ParisNeo/lollms_mcps_zoo)

---

## Roadmap

- [x] Add Coding_MCPs as a template
- [ ] Add more MCPs (data processing, web access, etc.)
- [ ] Community contributions
- [ ] Automated testing and CI

---

## Acknowledgements

Thanks to all contributors and the lollms community!

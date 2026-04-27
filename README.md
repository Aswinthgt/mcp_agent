# MCP Multi-Server Orchestrator

A robust Python client for the **Model Context Protocol (MCP)** that enables an LLM to interact with multiple MCP servers simultaneously. This project handles dynamic tool routing, namespacing, and lifecycle management for complex AI agent workflows.

## 🚀 Overview

This orchestrator solves the "multiple server" problem in MCP by creating a unified interface for an LLM to access tools across different backend processes. It automatically handles the connection to both Python and Node.js servers and provides a namespaced routing table to ensure the AI calls the correct tool on the correct server.

## ✨ Key Features

- **Multi-Server Connection**: Connects to multiple MCP servers (Python/Node.js) via a single configuration.
- **Dynamic Routing**: Uses a `server_name__tool_name` naming convention to prevent tool name collisions.
- **Async Architecture**: Built on `asyncio` and `mcp-sdk` for high-performance, non-blocking I/O.
- **Graceful Lifecycle**: Leverages `AsyncExitStack` to ensure all background subprocesses are properly terminated on exit.
- **Local LLM Integration**: Pre-configured to work with OpenAI-compatible local API endpoints (e.g., Minimax, Llama via Docker).
- **Interactive UI**: Includes a CLI interface with Markdown rendering and status spinners.

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Protocol**: Model Context Protocol (MCP)
- **Libraries**: `mcp`, `requests`, `rich`, `halo`, `asyncio`

## ⚙️ Configuration

The project uses a `config.json` file to manage server connections. Place this in your project root:

```json
{
  "terminal": {
    "command": "python",
    "args": ["path/to/terminal_server.py"]
  },
  "filesystem": {
    "command": "node",
    "args": ["path/to/filesystem_server.js"]
  },
  "fetch": {
    "command": "python",
    "args": ["path/to/fetch_server.py"]
  }
}
# MCP Multi-Server Orchestrator

A robust Python client for the **Model Context Protocol (MCP)** that enables an LLM to interact with multiple MCP servers simultaneously. This project handles dynamic tool routing, namespacing, and lifecycle management for complex AI agent workflows.

---

## 🚀 Overview

This orchestrator solves the "multiple server" problem in MCP by creating a unified interface for an LLM to access tools across different backend processes. It automatically handles the connection to both Python and Node.js servers and provides a namespaced routing table to ensure the AI calls the correct tool on the correct server.

## ✨ Key Features

- **Multi-Server Connection**: Connects to multiple MCP servers (Python/Node.js) via a single configuration.
- **Dynamic Routing**: Uses a `server_name__tool_name` naming convention to prevent tool name collisions.
- **Async Architecture**: Built on `asyncio` and `mcp-sdk` for high-performance, non-blocking I/O.
- **Graceful Lifecycle**: Leverages `AsyncExitStack` to ensure all background subprocesses are properly terminated on exit.
- **Local LLM Integration**: Pre-configured to work with OpenAI-compatible local API endpoints (e.g., Minimax, Llama via Docker).
- **Interactive UI**: Includes a CLI interface with Markdown rendering and status spinners using `rich` and `halo`.

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Protocol**: Model Context Protocol (MCP)
- **Libraries**: `mcp`, `requests`, `rich`, `halo`, `asyncio`

---

## ⚙️ Setup & Configuration

Before running the agent, you need to configure your tool servers and the LLM endpoint.

### 1. Update your MCP Tools (`config.json`)
List the servers you want the orchestrator to manage. You can mix Python and Node.js servers.

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
```

### 2. Configure the LLM Agent (`agent.py`)
Open your main script (e.g., `agent.py`) and customize your connection settings:

* **MODEL_URL**: Update this to your local server's IP address (e.g., your Docker container or Ollama endpoint).
* **Model Name**: Change the `"model"` value to the one you are running (e.g., `minimax-m2.5`).

```python
# In agent.py
MODEL_URL = "[http://localhost:12434/v1/chat/completions](http://localhost:12434/v1/chat/completions)"

# Inside the loop
response = requests.post(
    MODEL_URL,
    json={
        "model": "ai/gemma4:E2B", # Update your model name here
        "messages": messages,
        "tools": tool_descriptions,
    },
)
```

---

## 🏃 How to Run

1.  **Install Dependencies**:
    Ensure you have the required libraries installed:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Launch the Agent**:
    ```bash
    python agent/agent.py
    ```

## 🧠 How it Works (Routing Logic)

To prevent name collisions between different servers (e.g., two servers having a `search` tool), this client uses a **Double Underscore Namespace**:

1.  **Initialization**: Tools are registered with the AI as `server_name__original_tool_name`.
2.  **Mapping**: When the AI requests a tool call (e.g., `terminal__run_command`), the orchestrator:
    - Splits the name to identify the target server (`terminal`).
    - Retrieves the active session for that server.
    - Strips the prefix and executes `run_command` on the remote server.
3.  **Cleanup**: When you exit the program, the `AsyncExitStack` ensures every background process is killed cleanly.

## 🗓️ Roadmap (Coming Soon)

- [ ] **Unified Config**: Moving the `MODEL_URL` and `model` name into `config.json` for central management.
- [ ] **Environment Variable Support**: Pass API keys directly to MCP servers via the config file.
- [ ] **Dockerized Orchestrator**: A pre-built container to run the agent and its tools.

---

## 🤝 Contributing

Feel free to open an issue or submit a Pull Request if you have ideas to improve the orchestrator!

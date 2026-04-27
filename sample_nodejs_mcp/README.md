# 🛠️ Node Tools (Sample MCP)

A lightweight MCP server for local file operations.

### 1. Setup
```bash
npm install
```

### 2. Tools
* `node_read_file`: Read local files.
* `node_write_file`: Write/Overwrite local files.

### 3. Agent Integration
Add this to your `config.json`. **Replace the path** with your absolute local directory:

```json
{
  "node_tools": {
    "command": "npx",
    "args": [
      "-y",
      "tsx",
      "path/to/toolServer.ts"
    ]
  }
}
```

### 4. Test Server
Run the inspector to verify your tools are active:
```bash
npx @modelcontextprotocol/inspector npx tsx src/nodeToolsServer.ts
```
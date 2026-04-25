import { FastMCP } from "@modelcontextprotocol/sdk/server/fastmcp.js";
import fs from "fs/promises";

const mcp = new FastMCP({
  name: "node-tools",
  version: "1.0.0"
});

// 📖 READ FILE
mcp.tool({
  name: "node_read_file", // avoid conflict with Python
  description: "Read content of a file",
  inputSchema: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "Path to the file"
      }
    },
    required: ["path"]
  },
  async handler({ path }) {
    try {
      const data = await fs.readFile(path, "utf-8");
      return data;
    } catch (err) {
      return `Error: ${err.message}`;
    }
  }
});

// ✍️ WRITE FILE
mcp.tool({
  name: "node_write_file", // avoid conflict
  description: "Write content to a file",
  inputSchema: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "Path to the file"
      },
      content: {
        type: "string",
        description: "Content to write"
      }
    },
    required: ["path", "content"]
  },
  async handler({ path, content }) {
    try {
      await fs.writeFile(path, content, "utf-8");
      return "File written successfully";
    } catch (err) {
      return `Error: ${err.message}`;
    }
  }
});

// 🚀 START SERVER
mcp.run();
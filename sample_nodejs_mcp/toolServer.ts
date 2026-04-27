// Run with: pnpm tsx src/nodeToolsServer.ts

import { McpServer, StdioServerTransport } from '@modelcontextprotocol/server';
import { z } from 'zod'; // Standard zod import, use 'zod/v4' if your env requires it
import fs from 'fs/promises';

const mcpServer = new McpServer({
    name: 'node-tools',
    version: '1.0.0'
});

// 📖 READ FILE
mcpServer.registerTool(
    'node_read_file',
    {
        description: 'Read the content of a file from the local file system',
        inputSchema: z.object({
            path: z.string().describe('Absolute or relative path to the file')
        })
    },
    async ({ path }) => {
        try {
            const data = await fs.readFile(path, 'utf-8');
            return {
                content: [{ type: 'text', text: data }]
            };
        } catch (err: any) {
            return {
                content: [{ type: 'text', text: `Read Error: ${err.message}` }],
                isError: true
            };
        }
    }
);

// ✍️ WRITE FILE
mcpServer.registerTool(
    'node_write_file',
    {
        description: 'Write or overwrite content to a file on the local file system',
        inputSchema: z.object({
            path: z.string().describe('Path to the file'),
            content: z.string().describe('The content to write to the file')
        })
    },
    async ({ path, content }) => {
        try {
            await fs.writeFile(path, content, 'utf-8');
            return {
                content: [{ type: 'text', text: `Successfully wrote to ${path}` }]
            };
        } catch (err: any) {
            return {
                content: [{ type: 'text', text: `Write Error: ${err.message}` }],
                isError: true
            };
        }
    }
);

// 🚀 START SERVER
async function main() {
    const transport = new StdioServerTransport();
    await mcpServer.connect(transport);
    // Note: console.error is used for logging so it doesn't interfere with stdio protocol
    console.error('Node Tools MCP server is running...');
}

try {
    await main();
} catch (error) {
    console.error('Server error:', error);
    process.exit(1);
}
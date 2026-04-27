import asyncio
import json
from pathlib import Path
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

config_path = Path(__file__).resolve().parent.parent / "config.json"

async def initialize_tools():
    with open(config_path, 'r') as file:
        configs = json.load(file)

    exit_stack = AsyncExitStack()
    
    # Store everything we need to run tools later
    sessions = {}            # { "server_name": session_obj }
    tool_descriptions = []   # List for the AI model (OpenAI/Anthropic format)
    tool_mapping = {}        # { "unique_name": {"server": "name", "original_name": "name"} }

    try:
        for server_name, tool_config in configs.items():
            # 1. Connect and Initialize
            server_params = StdioServerParameters(
                command=tool_config["command"], 
                args=tool_config["args"]
            )
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            
            sessions[server_name] = session
            
            # 2. Fetch tools and format for AI
            response = await session.list_tools()
            
            for t in response.tools:
                # Create the unique key: "server__tool"
                unique_name = f"{server_name}__{t.name}"
                
                # Add to the list you send to the AI
                tool_descriptions.append({
                    "type": "function",
                    "function": {
                        "name": unique_name,
                        "description": t.description,
                        "parameters": t.inputSchema,
                    },
                })
                
                # Save the mapping so we know where to send the call later
                tool_mapping[unique_name] = {
                    "server": server_name,
                    "original_name": t.name
                }

        return sessions, tool_descriptions, tool_mapping, exit_stack

    except Exception as e:
        await exit_stack.aclose()
        raise e

async def main():
    sessions, descriptions, mapping, stack = await initialize_tools()
    
    try:
        # This 'descriptions' list is what you pass to the AI
        print("--- TOOL DESCRIPTIONS FOR AI ---")
        print(json.dumps(descriptions, indent=2))
        
        print("\n--- TOOL MAPPING ---")
        print(mapping)
        
        # EXAMPLE: If the AI calls 'weather_server__get_forecast'
        # You would look up mapping['weather_server__get_forecast'] 
        # to find which session to use.
        
    finally:
        await stack.aclose()

if __name__ == "__main__":
    asyncio.run(main())
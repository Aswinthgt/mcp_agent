import asyncio
import requests
import json
from pathlib import Path
from halo import Halo

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


# Docker model API
MODEL_URL = "http://localhost:12434/v1/chat/completions"

spinner = Halo(text='Thinking...', spinner='dots')

# locate tool server
tool_path = Path(__file__).resolve().parent.parent / "mcp_tools" / "tools_server.py"


# MCP server configuration
server = StdioServerParameters(
    command="python",
    args=[str(tool_path)]
)


async def main():

    async with stdio_client(server) as (read, write):

        async with ClientSession(read, write) as session:

            # REQUIRED MCP HANDSHAKE
            await session.initialize()

            # get MCP tools
            tools = await session.list_tools()

            tool_descriptions = []

            for t in tools.tools:
                tool_descriptions.append({
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    }
                })

            print("Loaded tools:", [t["function"]["name"] for t in tool_descriptions])

            messages = []

            user_input = input("Ask a question: ")

            messages.append({
                "role": "user",
                "content": user_input
            })

            while True:

                spinner.start()

                response = requests.post(
                    MODEL_URL,
                    json={
                        "model": "gemma3",
                        "messages": messages,
                        "tools": tool_descriptions
                    }
                ).json()

                # handle different API responses safely
                if "choices" in response:
                    message = response["choices"][0]["message"]
                elif "message" in response:
                    message = response["message"]
                else:
                    print("Unknown response:", response)
                    break

                # if model calls tool
                if "tool_calls" in message:

                    messages.append(message)

                    for call in message["tool_calls"]:

                        tool_name = call["function"]["name"]
                        args = call["function"]["arguments"]
                        tool_call_id = call["id"]

                        if isinstance(args, str):
                            args = json.loads(args)

                            # print("Calling tool:", tool_name)

                            result = await session.call_tool(tool_name, args)

                            if tool_name == "run_terminal":
                                print(result)

                            # print("Tool result:", result)

                            messages.append({
                                "role": "user",
                                "content": f"Tool result: {result}"
                            })  

                else:
                    spinner.stop()
                    # spinner.succeed("Done")
                    print(message["content"])
                    messages.append(message)
                    user_input = input("Ask a question: ")
                    messages.append({
                        "role": "user",
                        "content": user_input
                    })  


asyncio.run(main())
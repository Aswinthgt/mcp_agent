import asyncio
import requests
import json
import re
from pathlib import Path
from halo import Halo

from rich.console import Console
from rich.markdown import Markdown

# Import your updated initialization logic
from initialize_tool import initialize_tools

console = Console()

def extract_response(text):
    if not text:
        return ""
    # remove <think>...</think> including multiline
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

# Docker model API
MODEL_URL = "http://localhost:12434/v1/chat/completions"
spinner = Halo(text="Thinking...", spinner="dots")

async def main():
    # 1. Initialize all servers and get the mapping
    sessions, tool_descriptions, tool_mapping, exit_stack = await initialize_tools()

    try:
        print("✅ Loaded tools:", [t["function"]["name"] for t in tool_descriptions])

        messages = []
        user_input = input("\nAsk a question: ")
        messages.append({"role": "user", "content": user_input})

        while True:
            spinner.start()

            # 2. Call your local LLM
            response = requests.post(
                MODEL_URL,
                json={
                    "model": "ai/gemma4:E2B",
                    "messages": messages,
                    "tools": tool_descriptions,
                },
            )

            resp_json = response.json()

            # Handle different API response formats
            if "choices" in resp_json:
                message = resp_json["choices"][0]["message"]
            elif "message" in resp_json:
                message = resp_json["message"]
            else:
                spinner.stop()
                print("Unknown response format:", resp_json)
                break

            # 3. Check if the model wants to call a tool
            if "tool_calls" in message and message["tool_calls"]:
                spinner.text = "Executing tools..."
                messages.append(message) # Add assistant's tool call to history

                for call in message["tool_calls"]:
                    unique_tool_name = call["function"]["name"]
                    tool_args = call["function"]["arguments"]
                    tool_call_id = call.get("id")

                    if isinstance(tool_args, str):
                        tool_args = json.loads(tool_args)

                    # --- ROUTING LOGIC START ---
                    if unique_tool_name in tool_mapping:
                        mapping = tool_mapping[unique_tool_name]
                        server_name = mapping["server"]
                        original_name = mapping["original_name"]
                        
                        # Get the correct session for this specific server
                        target_session = sessions[server_name]
                        
                        # Execute the tool on the correct server
                        result = await target_session.call_tool(original_name, tool_args)
                        
                        # MCP returns a list of content blocks (text, image, etc.)
                        # We extract the text specifically for the LLM
                        readable_result = "\n".join([
                            content.text if hasattr(content, 'text') else str(content) 
                            for content in result.content
                        ])
                    else:
                        readable_result = f"Error: Tool {unique_tool_name} not found."
                    # --- ROUTING LOGIC END ---

                    # Append tool result to messages
                    # Note: Using 'role': 'tool' is standard for OpenAI-style APIs
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": unique_tool_name,
                        "content": readable_result,
                    })
                
                # The loop continues to send the tool results back to the LLM
                continue 

            else:
                # 4. Final Text Response
                spinner.stop()
                content = extract_response(message.get('content', ''))
                
                console.print("\n" + "-"*20)
                console.print(Markdown(f"# Answer\n\n{content}"))
                console.print("-"*20 + "\n")
                
                messages.append(message)
                
                user_input = input("Ask a question (or type 'exit'): ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                    
                messages.append({"role": "user", "content": user_input})

    finally:
        # 5. Crucial: Cleanly close all MCP server processes
        await exit_stack.aclose()
        print("\nDisconnected from all MCP servers.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
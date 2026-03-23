from mcp.server.fastmcp import FastMCP
import os
import subprocess
import platform

mcp = FastMCP("local-tools")
OS_NAME = platform.system()


@mcp.tool()
def list_files(path: str) -> list:
    """
    List files in a directory
    """
    return os.listdir(path)


@mcp.tool()
def read_file(path: str) -> str:
    """
    Read content of a file
    """
    with open(path, "r") as f:
        return f.read()


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Write content to file
    """
    with open(path, "w") as f:
        f.write(content)

    return "File written successfully"


@mcp.tool()
def run_terminal(command: str) -> str:
    f"""
    Execute terminal commands on the host machine.

    Current Operating System: {OS_NAME}

    If OS is Windows:
    - Use: dir, del, copy, move

    If OS is Linux or macOS:
    - Use: ls, rm, cp, mv
    """

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        return result.stdout + result.stderr

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    mcp.run()
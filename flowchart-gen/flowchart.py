# main.py
#
# An MCP server that uses the graphviz library to generate flowcharts.
#
# Installation:
# 1. Python 3.9+
# 2. Run: pip install "mcp[cli]" graphviz
# 3. Install the Graphviz software: https://graphviz.org/download/
#    (Ensure the `dot` executable is in your system's PATH)
#
# To Run:
# python main.py

import base64
import os
import shutil
from mcp.server.fastmcp import FastMCP
from graphviz import Source
from typing import Any, Dict

mcp = FastMCP("graphviz_flowchart_server", "0.0.1")

def generate_graph_image(dot_string: str) -> bytes:
    """
    Synchronous helper function to generate the graph image.
    This isolates the non-async graphviz library call.
    """
    s = Source(dot_string, filename="flowchart", format="png", engine="dot")
    output_filename = s.render(cleanup=True)
    with open(output_filename, "rb") as image_file:
        return image_file.read()

@mcp.tool()
async def create_flowchart(dot_string: str) -> Dict[str, str]:
    """
    Creates a flowchart from a DOT language string and returns it as an
    MCP image content block.

    Args:
        dot_string: A string containing the flowchart definition in the
                    DOT language. For example:
                    'digraph { a -> b; b -> c; a -> c; }'
    """
    try:
        # Generate the image bytes using the synchronous helper.
        image_bytes = generate_graph_image(dot_string)
        # Encode the image bytes as a base64 string.
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        # Return the image as an MCP image content block.
        return {
            "type": "image",
            "data": base64_image,
            "mimeType": "image/png"
        }
    except Exception as e:
        # If there's an error during graph generation, return a
        # user-friendly error message.
        print(f"An error occurred: {e}")
        return {
            "type": "text",
            "text": "Error: Could not generate the flowchart. Please check if Graphviz is installed and that the DOT string is valid."
        }


@mcp.resource("info://server")
def server_info() -> str:
    """
    Provides comprehensive information about this MCP server.

    This resource tells clients about the server's capabilities,
    dependency status, and how to use it.
    """
    graphviz_status = "✅ Found" if shutil.which('dot') else "❌ Not Found"
    return f"""
# Graphviz Flowchart MCP Server

This server provides tools to generate flowcharts and diagrams using the Graphviz library.

## Dependency Status

- **Graphviz Executable**: {graphviz_status}
  - If not found, please install from [graphviz.org/download/](https://graphviz.org/download/) and ensure it's in your system's PATH.

## How to Use

Use the `create_flowchart` tool with a DOT language string to generate an image.

**Example:**
`create_flowchart(dot_string='digraph G {{ a -> b; }}')`

## Official Documentation

For more advanced diagrams, refer to the dedicated documentation resource:
[Graphviz Documentation](info://documentation/graphviz)
"""

@mcp.resource("info://documentation/graphviz")
def graphviz_documentation() -> str:
    """
    Provides a link to the official Graphviz documentation.
    """
    return "[Graphviz Documentation](https://graphviz.org/documentation/)"


if __name__ == "__main__":
    mcp.run()
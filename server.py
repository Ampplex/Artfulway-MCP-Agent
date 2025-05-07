from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from typing import Dict, Any
from serpapi import Client

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

# Ensure API key is present
if not API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in environment variables. Please set it in the .env file.")

# Initialize the MCP server
mcp = FastMCP("SerpApi MCP Server")

# Tool to perform searches via SerpApi
@mcp.tool()
async def search(params: Dict[str, Any] = {}) -> str:
    """Perform a search on the specified engine using SerpApi.

    Args:
        params: Dictionary of engine-specific parameters (e.g., {"q": "Coffee", "engine": "google", "location": "Austin, TX"}).

    Returns:
        A formatted string of search results or an error message.
    """

    params = {
        "engine": "google",  # Default engine
        **params  # Include any additional parameters
    }

    try:
        client = Client(api_key=API_KEY)
        data = client.search(**params)

        # Process organic search results if available
        if "organic_results" in data:
            formatted_results = []
            for result in data.get("organic_results", []):
                title = result.get("title", "No title")
                link = result.get("link", "No link")
                snippet = result.get("snippet", "No snippet")
                formatted_results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
            return "\n".join(formatted_results) if formatted_results else "No organic results found"
        else:
            return "No organic results found"

    # Handle other exceptions (e.g., network issues)
    except Exception as e:
        return f"Error: {str(e)}"

# Run the server
if __name__ == "__main__":
    mcp.run()
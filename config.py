"""
Configuration settings for the Artist Project Assistant application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_TITLE = "Artist Project Assistant API"
API_DESCRIPTION = "API for providing project planning assistance to artists"
API_VERSION = "1.0.0"

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_MODEL = "gpt-4o"
GEMINI_MODEL = "gemini-2.0-flash"

# Default LLM settings
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 600
DEFAULT_TIMEOUT = 20
DEFAULT_MAX_RETRIES = 5

# MCP configuration
MCP_CONFIG_FILE = "browser_mcp.json"
MCP_MAX_STEPS = 5
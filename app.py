"""
Main entry point for the Artist Project Assistant API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import threading
from mcp_server import mcp

from config import API_TITLE, API_DESCRIPTION, API_VERSION
from api.routes import router as api_router

# Initialize FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    # Start the MCP server in a separate thread
    mcp_thread = threading.Thread(target=mcp.run)
    mcp_thread.start()
    # Start the FastAPI server
    uvicorn.run("app:app", host="localhost", port=port, reload=True)

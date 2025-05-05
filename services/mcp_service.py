"""
MCP service for the Artist Project Assistant.
"""
from mcp_use import MCPAgent, MCPClient
from langchain_core.language_models import BaseChatModel

from config import MCP_CONFIG_FILE, MCP_MAX_STEPS

class MCPService:
    """Service for interacting with the MCP client and agent."""
    
    @staticmethod
    def create_client() -> MCPClient:
        """
        Create an MCP client.
        
        Returns:
            An MCP client instance.
        """
        return MCPClient.from_config_file(MCP_CONFIG_FILE)
    
    @staticmethod
    def create_agent(llm: BaseChatModel) -> MCPAgent:
        """
        Create an MCP agent with the given LLM.
        
        Args:
            llm: The LLM to use with the agent.
            
        Returns:
            An MCP agent instance.
        """
        client = MCPService.create_client()
        return MCPAgent(llm=llm, client=client, max_steps=MCP_MAX_STEPS)
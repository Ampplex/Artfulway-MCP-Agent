"""
Core Artist Project Assistant implementation.
"""
import json
from typing import List, Dict, Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models import BaseChatModel

from core.prompts import ARTIST_ASSISTANT_PROMPT, RESEARCH_SUMMARY_TEMPLATE, get_search_queries
from services.mcp_service import MCPService
from utils.session import get_session, add_message_to_session
import asyncio

class ArtistProjectAssistant:
    """Core Assistant class for helping artists with projects."""
    
    def __init__(self, llm: BaseChatModel, session_id: str):
        """
        Initialize the Artist Project Assistant.
        
        Args:
            llm: The language model to use.
            session_id: The session ID for maintaining conversation history.
        """
        self.llm = llm
        self.session_id = session_id
        self.chat_history = get_session(session_id) or [SystemMessage(content=ARTIST_ASSISTANT_PROMPT)]
        
        # Create MCP agent
        self.agent = MCPService.create_agent(self.llm)
        
        # Create the chain for follow-up questions
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ARTIST_ASSISTANT_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        self.chain = (
            {"input": RunnablePassthrough(), "chat_history": lambda _: self.chat_history[1:]}
            | self.prompt
            | self.llm
        )
    
    async def research_project(self, project_description: str) -> str:
        """
        Research tools and resources for the given project using MCP agent.
        
        Args:
            project_description: The project description to research.
            
        Returns:
            A comprehensive project guide based on the research.
        """
        # Get search queries based on the project description
        search_queries = get_search_queries(project_description)
        
        # Search results collection
        search_results = []
        
        # Execute searches
        for query in search_queries:
            # Use the run method with a search prompt
            search_prompt = f"Search for information about: {query}\nProvide a comprehensive summary of the top 3 results."
            result = await self.agent.run(search_prompt)
            search_results.append({"query": query, "results": result})
            await asyncio.sleep(2) 
        
        # Generate research summary prompt
        research_prompt = RESEARCH_SUMMARY_TEMPLATE.format(
            project_description=project_description,
            search_results=json.dumps(search_results, indent=2)
        )
        
        # Use the LLM to analyze and synthesize the research
        result = await self.llm.ainvoke([SystemMessage(content=ARTIST_ASSISTANT_PROMPT), HumanMessage(content=research_prompt)])
        return result.content
        
    async def process_project(self, project_description: str) -> str:
        """
        Process a new project description with research and recommendations.
        
        Args:
            project_description: The project description to process.
            
        Returns:
            A comprehensive project guide.
        """
        # Add to chat history
        self.chat_history.append(HumanMessage(content=project_description))
        add_message_to_session(self.session_id, HumanMessage(content=project_description))
        
        # Perform comprehensive research
        project_guide = await self.research_project(project_description)
        
        # Add the response to chat history
        response_message = AIMessage(content=project_guide)
        self.chat_history.append(response_message)
        add_message_to_session(self.session_id, response_message)
    
        return project_guide
    
    async def process_followup(self, user_input: str) -> str:
        """
        Process a follow-up question or request within the current project context.
        
        Args:
            user_input: The follow-up question or request.
            
        Returns:
            The assistant's response to the follow-up.
        """
        # Add to chat history
        self.chat_history.append(HumanMessage(content=user_input))
        add_message_to_session(self.session_id, HumanMessage(content=user_input))
        
        # Use the chain for follow-up questions
        result = await self.chain.ainvoke(user_input)
        
        # Add to chat history
        response_message = AIMessage(content=result.content)
        self.chat_history.append(response_message)
        add_message_to_session(self.session_id, response_message)
        
        return result.content
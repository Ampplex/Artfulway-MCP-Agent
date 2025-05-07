"""
Core Artist Project Assistant implementation with improved error handling and true streaming.
"""
import json
import time
import random
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.language_models import BaseChatModel

from core.prompts import ARTIST_ASSISTANT_PROMPT, RESEARCH_SUMMARY_TEMPLATE, get_search_queries
from services.mcp_service import MCPService
from utils.session import get_session, add_message_to_session


class ArtistProjectAssistant:
    """Core Assistant class for helping artists with projects with true streaming and improved error handling."""
    
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

        self.search_cache = {}
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    async def _execute_search_with_retry(self, query: str) -> AsyncGenerator[str, None]:
        """
        Execute a search query with retry logic for handling rate limits.
        Now returns an AsyncGenerator to enable true streaming.
        
        Args:
            query: The search query to execute.
            
        Yields:
            Chunks of search results as they become available or fallback messages.
        """
        for attempt in range(self.max_retries):
            try:
                search_prompt = f"Search for information about: {query}\nProvide a comprehensive summary of the top 3 results."
                
                # Yield initial status
                yield f"Starting search for: {query}...\n"
                
                # Use agent's streaming capabilities if available
                if hasattr(self.agent, "stream"):
                    async for chunk in self.agent.stream(search_prompt):
                        # Check for rate limit indicators in chunks
                        if "rate-limited" in chunk.lower() or "unable to complete" in chunk.lower():
                            yield f"\nSearch encountered rate limits. Retrying in {self.retry_delay * (2 ** attempt)} seconds...\n"
                            await asyncio.sleep(self.retry_delay * (2 ** attempt) + random.uniform(0, 1))
                            break
                        yield chunk
                    else:
                        # If we completed the loop without breaking, search was successful
                        yield "\nSearch completed successfully.\n"
                        return
                else:
                    # Fallback for non-streaming agents
                    yield "Searching...\n"
                    result = await self.agent.run(search_prompt)
                    
                    # Check if the result indicates a rate limit error
                    if "rate-limited" in result.lower() or "unable to complete" in result.lower():
                        yield f"\nSearch encountered rate limits. Retrying in {self.retry_delay * (2 ** attempt)} seconds...\n"
                        await asyncio.sleep(self.retry_delay * (2 ** attempt) + random.uniform(0, 1))
                        continue
                    
                    yield result
                    return
                    
            except Exception as e:
                yield f"\nSearch attempt {attempt+1} failed: {str(e)[:50]}...\n"
                wait_time = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                yield f"Waiting {wait_time:.1f} seconds before retrying...\n"
                await asyncio.sleep(wait_time)
        
        # If all retries failed, yield a fallback response
        fallback = self._generate_fallback_response(query)
        yield f"\nAll search attempts failed. Using internal knowledge instead.\n"
        yield fallback
    
    def _generate_fallback_response(self, query: str) -> str:
        """
        Generate a fallback response when search fails.
        
        Args:
            query: The original search query.
            
        Returns:
            A fallback response.
        """
        return f"I couldn't retrieve external information about '{query}' due to service limitations. " \
               f"I'll use my internal knowledge to assist with this topic instead."
    
    async def _collect_search_results(self, project_description: str) -> AsyncGenerator[tuple[str, List[Dict[str, str]]], None]:
        """
        Collect search results for the given project description with true streaming.
        
        Args:
            project_description: The project description to research.
            
        Yields:
            Tuples of (status_message, current_search_results) where status_message is a string
            update and current_search_results is the list of search results collected so far.
        """
        search_queries = get_search_queries(project_description)
        search_results = []
        
        for idx, query in enumerate(search_queries, 1):
            yield f"\n[Researching... {query}\n", search_results
            
            # Check cache first
            if query in self.search_cache:
                yield f"Using cached search results for: {query}\n", search_results
                search_results.append({"query": query, "results": self.search_cache[query]})
                continue
                
            # Collect all chunks from the search
            full_result = ""
            async for chunk in self._execute_search_with_retry(query):
                full_result += chunk
                yield chunk, search_results
                
            # Store in cache and add to results
            self.search_cache[query] = full_result
            search_results.append({"query": query, "results": full_result.replace("*", "")})
            
            # Add a small delay between searches for rate limiting
            yield "Pausing briefly before next search...\n", search_results
            await asyncio.sleep(1)
            
        # Final yield with complete results
        yield f"\nAll research completed. Found information for {len(search_results)} queries.\n", search_results
    
    async def stream_project(self, project_description: str) -> AsyncGenerator[str, None]:
        """
        Stream the LLM response for a new project description with true streaming.
        
        Args:
            project_description: The project description to process.
            
        Yields:
            Chunks of the response as they become available.
        """
        # Add user message to chat history
        self.chat_history.append(HumanMessage(content=project_description))
        add_message_to_session(self.session_id, HumanMessage(content=project_description))

        # Stream search results while collecting them
        search_results = []
        final_results = []
        async for status_or_chunk, current_results in self._collect_search_results(project_description):
            yield status_or_chunk
            final_results = current_results

        # Once searches are complete, prepare for LLM synthesis
        yield "\n\n[LLM Synthesis] Generating comprehensive project guide...\n\n"

        # Prepare the research prompt
        research_prompt = RESEARCH_SUMMARY_TEMPLATE.format(
            project_description=project_description,
            search_results=json.dumps(final_results, indent=2)
        )

        # Stream the LLM synthesis
        response_content = ""
        async for chunk in self.llm.astream([
            SystemMessage(content=ARTIST_ASSISTANT_PROMPT),
            HumanMessage(content=research_prompt)
        ]):
            if hasattr(chunk, "content") and chunk.content:
                response_content += chunk.content
                yield chunk.content

        # Add the final response to chat history
        self.chat_history.append(AIMessage(content=response_content))
        add_message_to_session(self.session_id, AIMessage(content=response_content))

    async def stream_followup(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        Stream the LLM response for a follow-up question with true streaming.
        
        Args:
            user_input: The follow-up question or request.
            
        Yields:
            Chunks of the response as they become available.
        """
        # Add user message to chat history
        self.chat_history.append(HumanMessage(content=user_input))
        add_message_to_session(self.session_id, HumanMessage(content=user_input))

        # Stream the LLM response
        response_content = ""
        async for chunk in self.llm.astream([
            SystemMessage(content=ARTIST_ASSISTANT_PROMPT),
            *self.chat_history[1:],  # Include all history except the system message
        ]):
            if hasattr(chunk, "content") and chunk.content:
                response_content += chunk.content
                yield chunk.content
                
        # Add the final response to chat history
        self.chat_history.append(AIMessage(content=response_content))
        add_message_to_session(self.session_id, AIMessage(content=response_content))
        
    # The following methods remain for backward compatibility but now use streaming internally
    
    async def research_project(self, project_description: str) -> str:
        """
        Research tools and resources for the given project using MCP agent.
        Now uses the streaming implementation internally.
        
        Args:
            project_description: The project description to research.
            
        Returns:
            A comprehensive project guide based on the research.
        """
        full_response = ""
        async for chunk in self.stream_project(project_description):
            full_response += chunk
            
        # Extract just the LLM synthesis part
        synthesis_marker = "[LLM Synthesis] Generating comprehensive project guide..."
        if synthesis_marker in full_response:
            return full_response.split(synthesis_marker)[1].strip()
        return full_response
    
    async def process_project(self, project_description: str) -> str:
        """
        Process a new project description with research and recommendations.
        Now uses the streaming implementation internally.
        
        Args:
            project_description: The project description to process.
            
        Returns:
            A comprehensive project guide.
        """
        return await self.research_project(project_description)
    
    async def process_followup(self, user_input: str) -> str:
        """
        Process a follow-up question or request within the current project context.
        Now uses the streaming implementation internally.
        
        Args:
            user_input: The follow-up question or request.
            
        Returns:
            The assistant's response to the follow-up.
        """
        full_response = ""
        async for chunk in self.stream_followup(user_input):
            full_response += chunk
            
        return full_response
        
    async def _generate_fallback_project_guide(self, project_description: str) -> str:
        """
        Generate a project guide using only the LLM's internal knowledge when searches fail.
        
        Args:
            project_description: The project description.
            
        Returns:
            A project guide based on internal knowledge.
        """
        fallback_prompt = f"""
        Due to external search limitations, I'll help you with your project using my internal knowledge.
        
        Project Description: {project_description}
        
        Please provide:
        1. A comprehensive overview of this type of project
        2. Suggested materials, tools, and techniques
        3. Step-by-step guidance for the project
        4. Common challenges and how to overcome them
        5. Tips for achieving professional results
        
        Focus only on reliable information you're confident about, and be clear about any limitations in your advice.
        """
        
        result = await self.llm.ainvoke([SystemMessage(content=ARTIST_ASSISTANT_PROMPT), HumanMessage(content=fallback_prompt)])
        return result.content
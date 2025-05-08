"""
Session management for the Artist Project Assistant.
"""
import uuid
from typing import Dict, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage

# Global session storage
sessions: Dict[str, List[BaseMessage]] = {}
conversation_history = []

def create_session(system_prompt: str) -> str:
    """
    Create a new session with a system prompt.
    
    Args:
        system_prompt: The system prompt to initialize the session with.
        
    Returns:
        The session ID.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = [SystemMessage(content=system_prompt)]
    return session_id

def get_session(session_id: str) -> List[BaseMessage]:
    """
    Get a session by ID. Returns None if the session doesn't exist.
    
    Args:
        session_id: The session ID.
        
    Returns:
        The chat history for the session.
    """
    return sessions.get(session_id)

def update_session(session_id: str, messages: List[BaseMessage]) -> None:
    """
    Update a session with new messages.
    
    Args:
        session_id: The session ID.
        messages: The new chat history.
    """
    sessions[session_id] = messages

def add_message_to_session(session_id: str, message: BaseMessage) -> None:
    """
    Add a message to a session.
    
    Args:
        session_id: The session ID.
        message: The message to add.
    """
    if session_id in sessions:
        sessions[session_id].append(message)
    
def generate_session_id() -> str:
    """
    Generate a new session ID.
    
    Returns:
        A new UUID as a string.
    """
    return str(uuid.uuid4())
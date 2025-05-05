"""
Pydantic models for the Artist Project Assistant API.
"""
from typing import Optional
from pydantic import BaseModel

class ProjectRequest(BaseModel):
    """Request model for project assistance."""
    project_description: str
    model_type: str = "gemini"  # Default to gemini
    follow_up_question: Optional[str] = None  # For follow-up questions
    session_id: Optional[str] = None  # For maintaining conversations

class ProjectResponse(BaseModel):
    """Response model for project assistance."""
    response: str
    session_id: str
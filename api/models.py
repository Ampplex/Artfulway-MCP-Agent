"""
Request and response models for the Artist Project Assistant API.
"""
from typing import Optional
from pydantic import BaseModel, Field

class ProjectRequest(BaseModel):
    """
    Request model for processing a project or follow-up question.
    """
    project_description: Optional[str] = Field(
        None, 
        description="Description of the art project to get assistance with"
    )
    follow_up_question: Optional[str] = Field(
        None, 
        description="Follow-up question related to a previously described project"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Session ID for maintaining conversation context"
    )
    model_type: Optional[str] = Field(
        "gemini", 
        description="LLM type to use (gemini, claude, gpt4)"
    )

    class Config:
        schema_extra = {
            "example": {
                "project_description": "I want to create a mixed media portrait combining acrylic painting with collage elements",
                "follow_up_question": None,
                "session_id": None,
                "model_type": "gemini"
            }
        }

class ProjectResponse(BaseModel):
    """
    Response model containing the assistant's response and session ID.
    """
    response: str = Field(..., description="The assistant's response")
    session_id: str = Field(..., description="Session ID for follow-up questions")

    class Config:
        schema_extra = {
            "example": {
                "response": "I'll help you with your mixed media portrait project...",
                "session_id": "abc123def456"
            }
        }


class StreamResponse(BaseModel):
    """
    Model for streaming responses that still need to include session ID.
    """
    content: str = Field(..., description="Content chunk")
    session_id: str = Field(..., description="Session ID for follow-ups")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "I'll help you with your mixed media portrait project...",
                "session_id": "abc123def456"
            }
        }
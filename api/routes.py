"""
API routes for the Artist Project Assistant.
"""
from fastapi import APIRouter, BackgroundTasks, Depends

from api.models import ProjectRequest, ProjectResponse
from core.assistant import ArtistProjectAssistant
from core.prompts import ARTIST_ASSISTANT_PROMPT
from services.llm_service import LLMServiceFactory
from utils.session import create_session, get_session

router = APIRouter()

async def get_assistant(
    model_type: str = "gemini",
    session_id: str = None
) -> ArtistProjectAssistant:
    """
    Dependency for getting an Artist Project Assistant instance.
    
    Args:
        model_type: The type of model to use.
        session_id: The session ID for conversation history.
        
    Returns:
        An ArtistProjectAssistant instance.
    """
    # Create session if not provided
    if not session_id or not get_session(session_id):
        session_id = create_session(ARTIST_ASSISTANT_PROMPT)
    
    # Get LLM
    llm = LLMServiceFactory.create_llm(model_type)
    
    # Return assistant
    return ArtistProjectAssistant(llm=llm, session_id=session_id)

async def process_request_background(
    assistant: ArtistProjectAssistant,
    project_request: ProjectRequest
) -> str:
    """
    Process the request in the background and return the result.
    
    Args:
        assistant: The ArtistProjectAssistant instance.
        project_request: The project request.
        
    Returns:
        The assistant's response.
    """
    if project_request.follow_up_question:
        return await assistant.process_followup(project_request.follow_up_question)
    else:
        return await assistant.process_project(project_request.project_description)

@router.post("/process", response_model=ProjectResponse)
async def process_project(
    project_request: ProjectRequest,
    background_tasks: BackgroundTasks,
    assistant: ArtistProjectAssistant = Depends(get_assistant)
):
    """
    Process a project request and return the assistant's response.
    
    - For new projects, provide the project_description
    - For follow-up questions, provide follow_up_question and session_id
    """
    # Process the request
    response = await process_request_background(assistant, project_request)
    
    return ProjectResponse(
        response=response,
        session_id=assistant.session_id
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
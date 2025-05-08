"""
API routes for the Artist Project Assistant.
"""
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from api.models import ProjectRequest, ProjectResponse
from core.assistant import ArtistProjectAssistant
from core.prompts import ARTIST_ASSISTANT_PROMPT
from services.llm_service import LLMServiceFactory

router = APIRouter()

async def get_assistant(
    model_type: str = "gemini"
) -> ArtistProjectAssistant:
    """
    Dependency for getting an Artist Project Assistant instance.
    
    Args:
        model_type: The type of model to use.
        
    Returns:
        An ArtistProjectAssistant instance.
    """
    # Get LLM instance
    llm = LLMServiceFactory.create_llm(model_type)
    
    # Return assistant (no session tracking)
    return ArtistProjectAssistant(llm=llm)

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
    
    - For new projects: provide project_description
    - For follow-ups: provide follow_up_question
    """
    response = await process_request_background(assistant, project_request)
    
    return ProjectResponse(
        response=response,
        session_id=None  # Maintain response model but return None for session
    )

@router.post("/process/stream")
async def process_project_stream(
    project_request: ProjectRequest,
    assistant: ArtistProjectAssistant = Depends(get_assistant)
):
    """
    Stream the assistant's response for a project request.
    
    Returns:
        StreamingResponse with conversation chunks.
    """
    async def generate_stream():
        if project_request.follow_up_question:
            async for chunk in assistant.stream_followup(project_request.follow_up_question):
                yield chunk
        else:
            async for chunk in assistant.stream_project(project_request.project_description):
                yield chunk
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
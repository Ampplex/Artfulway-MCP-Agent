"""
LLM service factory for the Artist Project Assistant.
"""
from fastapi import HTTPException
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from config import (
    OPENAI_API_KEY, 
    GOOGLE_API_KEY, 
    OPENAI_MODEL, 
    GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES
)

class LLMServiceFactory:
    """Factory for creating LLM instances."""
    
    @staticmethod
    def create_llm(model_type: str = "gemini") -> BaseChatModel:
        """
        Create an LLM instance based on the model type.
        
        Args:
            model_type: The type of model to create ("openai" or "gemini").
            
        Returns:
            An LLM instance.
            
        Raises:
            HTTPException: If the required API key is not found or model type is invalid.
        """
        if model_type.lower() == "openai":
            if not OPENAI_API_KEY:
                raise HTTPException(
                    status_code=500, 
                    detail="OPENAI_API_KEY not found in environment variables"
                )
            
            return ChatOpenAI(
                model=OPENAI_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
                max_retries=DEFAULT_MAX_RETRIES
            )
        elif model_type.lower() == "gemini":
            if not GOOGLE_API_KEY:
                raise HTTPException(
                    status_code=500, 
                    detail="GOOGLE_API_KEY not found in environment variables"
                )
                
            return ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
                timeout=DEFAULT_TIMEOUT,
                max_retries=DEFAULT_MAX_RETRIES,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model type: {model_type}. Must be 'openai' or 'gemini'"
            )
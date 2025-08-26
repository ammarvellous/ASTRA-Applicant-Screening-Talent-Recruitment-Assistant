"""
LLM Loader module for ASTRA
This module centralizes loading of different language models for use across the application.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_ibm import ChatWatsonx
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from gemini_llm import GeminiLLM

# Load environment variables from .env file
load_dotenv()

# Dictionary to store initialized LLMs to avoid recreating them
_llm_cache = {}

def get_gemini_llm(
    model_name: str = "gemini-1.5-flash", 
    temperature: float = 0.0,
    force_reload: bool = False
) -> GeminiLLM:
    """
    Get a Gemini LLM instance with specified parameters.
    
    Args:
        model_name: The model to use (default: gemini-1.5-flash)
        temperature: Controls randomness (0.0 to 1.0)
        force_reload: If True, creates a new instance even if cached
        
    Returns:
        An initialized GeminiLLM instance
    """
    cache_key = f"gemini_{model_name}_{temperature}"
    
    if cache_key not in _llm_cache or force_reload:
        # Ensure API key is available
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize and cache the LLM
        _llm_cache[cache_key] = GeminiLLM(
            model_name=model_name,
            temperature=temperature
        )
    
    return _llm_cache[cache_key]

def get_watsonx_llm(
    model_id: str = "ibm/granite-13b-instruct-v2",
    temperature: float = 0.0,
    max_new_tokens: int = 1000,
    force_reload: bool = False
) -> ChatWatsonx:
    """
    Get a WatsonX LLM instance with specified parameters.
    
    Args:
        model_id: The model ID to use
        temperature: Controls randomness (0.0 to 1.0)
        max_new_tokens: Maximum number of tokens to generate
        force_reload: If True, creates a new instance even if cached
        
    Returns:
        An initialized ChatWatsonx instance
    """
    cache_key = f"watsonx_{model_id}_{temperature}_{max_new_tokens}"
    
    if cache_key not in _llm_cache or force_reload:
        # Ensure API key and project ID are available
        watsonx_apikey = os.getenv("WATSONX_APIKEY")
        watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
        watsonx_url = os.getenv("WATSONX_URL")
        
        # Parameters for WatsonX
        parameters = TextChatParameters(max_tokens=500, temperature=0.0, top_p=1)
        
        # Initialize and cache the LLM
        _llm_cache[cache_key] = ChatWatsonx(
            model_id="meta-llama/llama-3-3-70b-instruct",
            # model_id=model_id,
            url=watsonx_url,
            apikey=watsonx_apikey,
            project_id=watsonx_project_id,
            params=parameters,
        )
    
    return _llm_cache[cache_key]

def get_llm(
    provider: str = "watsonx",
    **kwargs
) -> Any:
    """
    Unified function to get an LLM of any supported type.
    
    Args:
        provider: The LLM provider to use ("gemini", "watsonx")
        **kwargs: Parameters specific to the chosen provider
        
    Returns:
        An initialized LLM instance
    """
    provider = provider.lower()
    
    if provider == "gemini":
        return get_gemini_llm(**kwargs)
    elif provider == "watsonx":
        return get_watsonx_llm(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
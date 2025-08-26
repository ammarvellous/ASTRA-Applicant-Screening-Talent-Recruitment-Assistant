# gemini_llm.py
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM(LLM, BaseModel):
    """
    A LangChain-compatible wrapper for the Gemini 1.5 Flash model.
    """
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load API key from environment
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    @property
    def _llm_type(self) -> str:
        return "gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Calls the Gemini model with the prompt and returns text.
        """
        model = genai.GenerativeModel(self.model_name)
        
        # Set generation config
        generation_config = {
            "temperature": self.temperature,
            "top_p": 1.0,
            "top_k": 32
        }
        
        # The system prompt needs to be incorporated into the user prompt
        system_instruction = "You are a helpful AI assistant specialized in resume parsing."
        full_prompt = f"{system_instruction}\n\n{prompt}"
        
        response = model.generate_content(full_prompt, generation_config=generation_config)
        
        # Handle potential errors or empty responses
        if hasattr(response, "text"):
            return response.text
        else:
            # If there's an issue with the response
            return "Error: Unable to generate content."

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Return identifying parameters."""
        return {"model_name": self.model_name, "temperature": self.temperature}
        
    @property
    def _llm_kwargs(self) -> Mapping[str, Any]:
        """Return kwargs."""
        return {}

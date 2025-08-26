# gemini_llm.py
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from pydantic import BaseModel
import genai

class GeminiLLM(LLM, BaseModel):
    """
    A LangChain-compatible wrapper for the Gemini 1.5 Flash model.
    """
    model_name: str = "gemini-1.5-flash"

    @property
    def _llm_type(self) -> str:
        return "gemini"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Calls the Gemini model with the prompt and returns text.
        """
        model = genai.GenerativeModel(self.model_name)
        system_prompt = {
            "role": "system",
            "content": "You are a helpful AI assistant specialized in resume parsing."
        }
        user_prompt = {
            "role": "user",
            "content": prompt
        }

        response = model.generate_content([system_prompt, user_prompt])
        # Gemini responses are usually structured as response.output_text
        return response.output_text

    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

    def _llm_kwargs(self) -> Mapping[str, Any]:
        return {}

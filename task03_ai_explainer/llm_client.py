import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LLMClient:
    """
    A robust wrapper for the Google Gemini API.
    Handles authentication, error logging, and standardizing LLM calls.
    """
    def __init__(self, api_key: Optional[str] = None):
        import google.generativeai as genai
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. "
                "Please set it in your .env file or export it in your terminal."
            )
            
        genai.configure(api_key=self.api_key)
        # Use gemini-2.5-flash for free, fast, and high-quality responses
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def generate_response(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        """
        Sends a synchronous request to Gemini and returns the text response.
        """
        try:
            # Gemini handles system prompts slightly differently, so we combine them for simplicity 
            # if we are not explicitly using the SystemInstruction feature. 
            # For best results with gemini-1.5-flash, we can just pass the system prompt as the first instruction.
            combined_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
            
            response = self.model.generate_content(
                combined_prompt,
                generation_config=import_genai().GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.4,
                ),
                safety_settings={
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error communicating with Google Gemini API: {e}")
            raise

def import_genai():
    import google.generativeai as genai
    return genai

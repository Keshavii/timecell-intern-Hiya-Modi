import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Models to try in order — if the first hits a quota limit, fall back to the next
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

class LLMClient:
    """
    A robust wrapper for the Google Gemini API.
    Handles authentication, error logging, rate-limit retries, and model fallback.
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
        self._genai = genai
        self.model = genai.GenerativeModel(GEMINI_MODELS[0])
        self._current_model_idx = 0
        
    def generate_response(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        """
        Sends a request to Gemini with automatic retry on rate limits (429)
        and model fallback if the primary model's quota is exhausted.
        """
        combined_prompt = f"{system_prompt}\n\n---\n\n{user_message}"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    combined_prompt,
                    generation_config=self._genai.GenerationConfig(
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
                error_str = str(e)
                
                # Handle rate limiting (429)
                if "429" in error_str or "ResourceExhausted" in error_str:
                    # Try falling back to the next model first
                    if self._current_model_idx < len(GEMINI_MODELS) - 1:
                        self._current_model_idx += 1
                        fallback = GEMINI_MODELS[self._current_model_idx]
                        logger.warning(f"Rate limited on {GEMINI_MODELS[self._current_model_idx - 1]}. Falling back to {fallback}...")
                        self.model = self._genai.GenerativeModel(fallback)
                        continue  # Retry immediately with new model
                    
                    # All models exhausted — wait and retry
                    wait_time = 30 * (attempt + 1)  # 30s, 60s, 90s
                    logger.warning(f"All models rate-limited. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    print(f"  ⏳ Rate limited — waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error communicating with Google Gemini API: {e}")
                    raise
        
        raise RuntimeError("All retry attempts exhausted. Please wait a few minutes and try again.")


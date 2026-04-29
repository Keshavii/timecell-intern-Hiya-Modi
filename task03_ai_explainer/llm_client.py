import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ClaudeClient:
    """
    A robust wrapper for the Anthropic Claude API.
    Handles authentication, error logging, and standardizing calls.
    """
    def __init__(self, api_key: Optional[str] = None):
        import anthropic
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in your .env file or export it in your terminal."
            )
            
        self.client = anthropic.Anthropic(api_key=self.api_key)
        # Using the recommended model for general reasoning and coding tasks
        self.model = "claude-3-5-sonnet-20241022"
        
    def generate_response(self, system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
        """
        Sends a synchronous request to Claude and returns the text response.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.4, # Low temperature for more deterministic, analytical responses
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            # Claude returns a list of content blocks
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error communicating with Anthropic API: {e}")
            raise

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """
    Safely extracts and parses JSON from LLM output.
    
    Even with strict prompt instructions, LLMs sometimes wrap JSON in
    markdown code blocks (```json ... ```) or include conversational filler.
    This function intelligently strips that away.
    """
    text = raw_text.strip()
    
    # Heuristic 1: If it starts and ends with curlies, it's likely clean JSON
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass # Fall back to heuristic 2
            
    # Heuristic 2: Find the first '{' and last '}'
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_candidate = text[start_idx:end_idx+1]
        try:
            return json.loads(json_candidate)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode extracted JSON: {json_candidate}")
            raise ValueError(f"LLM output could not be parsed as JSON. Error: {e}")
            
    raise ValueError("No JSON object found in LLM output.")

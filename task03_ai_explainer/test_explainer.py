import pytest
from task03_ai_explainer.output_parser import parse_llm_json
from task03_ai_explainer.prompts import format_portfolio_for_prompt

def test_parse_llm_json_clean():
    """Test parsing a perfectly formatted, clean JSON string."""
    raw = '{"summary": "Test summary", "doing_well": "Test", "consider_changing": "Test", "verdict": "Balanced"}'
    parsed = parse_llm_json(raw)
    assert parsed["verdict"] == "Balanced"
    assert parsed["summary"] == "Test summary"

def test_parse_llm_json_markdown():
    """Test parsing JSON wrapped in standard markdown code blocks."""
    raw = "```json\n{\n  \"summary\": \"Test\",\n  \"doing_well\": \"Test\",\n  \"consider_changing\": \"Test\",\n  \"verdict\": \"Aggressive\"\n}\n```"
    parsed = parse_llm_json(raw)
    assert parsed["verdict"] == "Aggressive"

def test_parse_llm_json_with_chatter():
    """Test parsing JSON that includes conversational filler before and after."""
    raw = "Here is the JSON you requested:\n```json\n{\"summary\": \"Test\"}\n```\nHope this helps!"
    parsed = parse_llm_json(raw)
    assert parsed["summary"] == "Test"

def test_parse_llm_json_invalid():
    """Test that a ValueError is raised when no JSON is present."""
    raw = "This is just a regular sentence, no json here."
    with pytest.raises(ValueError, match="No JSON object found"):
        parse_llm_json(raw)

def test_format_portfolio_for_prompt():
    """Test that the portfolio is formatted correctly with Indian currency context."""
    p = {
        "total_value_inr": 10000000,
        "monthly_expenses_inr": 80000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80}
        ]
    }
    res = format_portfolio_for_prompt(p)
    assert "₹10,000,000.00" in res
    assert "₹80,000.00" in res
    assert "BTC: 30% allocation (Expected crash scenario: -80%)" in res

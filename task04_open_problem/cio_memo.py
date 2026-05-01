"""
CIO Memo Generator — Timecell's AI Chief Investment Officer.

This module takes Monte Carlo simulation results and generates a structured
Investment Committee (IC) Memo — the kind of document a real family office
would present to its clients.

This is NOT Task 03 (portfolio explainer). The key differences:
- Task 03: "Explain this portfolio in plain English" (educational)
- Task 04: "Run stochastic simulations, then synthesize into an institutional
            decision document with before/after rebalancing proof" (advisory)
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

CIO_SYSTEM_PROMPT = """You are Timecell's AI Chief Investment Officer (CIO) — a senior wealth advisor 
for ultra-high-net-worth Indian families.

You are generating an INVESTMENT COMMITTEE MEMO based on Monte Carlo simulation results.
This is NOT a general explanation. This is a formal advisory document.

Your memo must follow this EXACT JSON structure:
{
    "risk_rating": "LOW | MODERATE | ELEVATED | CRITICAL",
    "executive_summary": "2-3 sentences. State the ruin probability, what it means, and whether action is needed.",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "recommended_actions": ["action 1", "action 2", "action 3"],
    "client_talking_points": "A short script for the wealth manager to read aloud to the client. Start with 'Namaste.' The tone must be authoritative, reassuring, and elite — sounding like a veteran CIO at a top-tier family office. Do NOT sound like a robot reading a spreadsheet. Frame the risk not just as a percentage, but as an unacceptable threat to the client's specific goal. Frame the solution as a decisive move to 'protect the downside' and 'guarantee certainty.' Keep it conversational but highly professional."
}

RULES:
- Reference EXACT numbers from the simulation (ruin probability, percentiles, values in ₹ Crores/Lakhs)
- Risk ratings: LOW (<5% ruin), MODERATE (5-10%), ELEVATED (10-20%), CRITICAL (>20%)
- Be specific: "Reduce BTC from 30% to 15%" not "consider reducing crypto exposure"
- Use Indian financial context (₹, Crores, Lakhs, NIFTY, RBI rates)
- Return ONLY the JSON object. No markdown, no explanation outside JSON."""


def format_simulation_for_cio(portfolio: dict, original_results: dict, 
                               rebalance_data: dict = None, 
                               rebalanced_results: dict = None,
                               client_context: dict = None) -> str:
    """
    Formats the Monte Carlo results into a structured prompt for the CIO.
    Optionally includes client context from the CIO Interview.
    """
    lines = [
        "=== PORTFOLIO OVERVIEW ===",
        f"Total Value: ₹{portfolio['total_value_inr']:,.0f}",
        f"Monthly Expenses: ₹{portfolio.get('monthly_expenses_inr', 0):,.0f}",
        "",
        "Asset Allocation:",
    ]
    
    for asset in portfolio.get("assets", []):
        lines.append(f"  - {asset['name']}: {asset['allocation_pct']}% (crash scenario: {asset.get('expected_crash_pct', 'N/A')}%)")
    
    lines.extend([
        "",
        "=== MONTE CARLO SIMULATION RESULTS (CURRENT PORTFOLIO) ===",
        f"Simulations: {original_results['simulations_run']:,}",
        f"Projection Horizon: {original_results['years_projected']} years",
        f"Probability of Ruin: {original_results['ruin_probability_pct']:.2f}%",
        f"Median End Value: ₹{original_results['median_end_value_inr']:,.0f}",
    ])
    
    if "percentiles" in original_results:
        pct = original_results["percentiles"]
        lines.extend([
            f"5th Percentile (Worst): ₹{pct['p5']:,.0f}",
            f"25th Percentile: ₹{pct['p25']:,.0f}",
            f"75th Percentile: ₹{pct['p75']:,.0f}",
            f"95th Percentile (Best): ₹{pct['p95']:,.0f}",
        ])
    
    # Add rebalancing comparison if available
    if rebalance_data and rebalanced_results:
        lines.extend([
            "",
            "=== REBALANCED PORTFOLIO SIMULATION ===",
            "Changes made:",
        ])
        for change in rebalance_data.get("changes", []):
            lines.append(f"  - {change['asset']}: {change['action']} ({change['from_pct']}% → {change['to_pct']}%) — {change['reason']}")
        
        lines.extend([
            f"",
            f"New Ruin Probability: {rebalanced_results['ruin_probability_pct']:.2f}%",
            f"New Median End Value: ₹{rebalanced_results['median_end_value_inr']:,.0f}",
        ])
        
        if "percentiles" in rebalanced_results:
            rpct = rebalanced_results["percentiles"]
            lines.append(f"New 5th Percentile: ₹{rpct['p5']:,.0f}")
        
        improvement = original_results['ruin_probability_pct'] - rebalanced_results['ruin_probability_pct']
        lines.append(f"Ruin Probability Improvement: {improvement:+.2f} percentage points")
    
    # Inject client context from the CIO Interview
    if client_context:
        lines.extend([
            "",
            "=== CLIENT PROFILE (from CIO Interview) ===",
            f"Goal: {client_context.get('goal', 'Not specified')}",
            f"Definition of Financial Failure: {client_context.get('failure_definition', 'Not specified')}",
            f"Time Horizon: {client_context.get('time_horizon_years', 30)} years",
            "",
            "IMPORTANT: Tailor ALL advice to this specific client's goal, failure definition, and time horizon.",
            "Reference their exact situation in the executive summary, findings, and talking points.",
        ])
    
    return "\n".join(lines)


def generate_cio_memo(client, portfolio: dict, original_results: dict,
                      rebalance_data: dict = None,
                      rebalanced_results: dict = None,
                      client_context: dict = None) -> str:
    """
    Generates the Investment Committee Memo using the LLM.
    
    Args:
        client: LLM client instance (LLMClient wrapping Google Gemini)
        portfolio: Original portfolio dict
        original_results: Monte Carlo results for original portfolio
        rebalance_data: Output from rebalancer.suggest_rebalance()
        rebalanced_results: Monte Carlo results for rebalanced portfolio
        client_context: Optional dict from CIO Interview with goal, failure_definition, time_horizon
    
    Returns:
        str: Raw LLM response (JSON memo)
    """
    user_message = format_simulation_for_cio(
        portfolio, original_results, rebalance_data, rebalanced_results,
        client_context=client_context
    )
    
    return client.generate_response(
        system_prompt=CIO_SYSTEM_PROMPT,
        user_message=user_message,
        max_tokens=8192
    )

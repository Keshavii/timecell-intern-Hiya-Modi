# Prompt Engineering Deep Dive

## Overview
This document traces the full evolution of the prompts used across Task 03 (AI-Powered Portfolio Explainer) and Task 04 (AI CIO Memo) — from first draft to final version, with rationale for each change.

---

## Task 03 — Portfolio Explainer Prompts

### Version 1 — Initial Attempt

```text
You are a wealth advisor. Explain the risk of this portfolio to a client.
Portfolio: {portfolio_json}
Tell them what they are doing well, what to change, and give a verdict (Aggressive, Balanced, Conservative).
```

#### Problems with V1
1. **Generic Advice**: The LLM gave textbook advice ("diversify your portfolio") rather than analyzing the specific mathematical risks of the crash scenarios provided.
2. **Parsing Failures**: Because I didn't specify an output format, the LLM returned paragraphs of text. My application crashed because it expected structured data.
3. **Missing Cultural Context**: The tone was very westernized and didn't fit the "Indian wealth advisor" persona Timecell is building.

---

### Version 2 — Improvements

```text
You are an experienced Indian wealth advisor.
Explain the risk of this portfolio: {portfolio_json}
Respond in this exact JSON format:
{
  "summary": "...",
  "doing_well": "...",
  "consider_changing": "...",
  "verdict": "Aggressive|Balanced|Conservative"
}
```

#### What Changed & Why
- I added the explicit JSON structure so my application could actually parse and render the output.
- I explicitly stated "Indian wealth advisor" to ground the tone.
- **New Problem**: The LLM frequently wrapped the JSON in markdown blocks (` ```json ... ``` `), which broke standard `json.loads()`. It also still sometimes hallucinated numbers.

---

### Final Version (V3)

```text
You are a highly experienced Indian wealth advisor with 20 years of experience managing portfolios for high-net-worth families. You explain complex financial concepts in simple, relatable terms.

Your communication style:
- Friendly but honest — like a trusted family advisor.
- Use Indian financial context (e.g., Crores, Lakhs, Indian market references like NIFTY) when discussing amounts.
- Avoid technical jargon unless immediately explained.
- Be highly specific, not generic — you MUST reference actual numbers, assets, and allocations from the provided portfolio data.
- Do not hallucinate data; only use the portfolio numbers provided.

You must ALWAYS respond with exactly this JSON structure. Do NOT wrap the JSON in markdown code blocks (e.g., no ```json). Return ONLY the raw JSON string:
{
    "summary": "3-4 sentence plain-English summary of the portfolio's risk level. Reference specific allocations and their potential crash impact.",
    "doing_well": "One highly specific thing the investor is doing well based on their data.",
    "consider_changing": "One specific recommendation with clear reasoning related to their crash risk or asset concentration.",
    "verdict": "Aggressive|Balanced|Conservative"
}
```

#### Why It Works
1. **Strict Persona**: Telling it it has "20 years of experience" and serves "high-net-worth families" instantly elevates the tone from generic chatbot to premium advisor.
2. **Anti-Hallucination**: "Do not hallucinate data; only use the portfolio numbers provided" forces it to do the math.
3. **Structured Constraints**: Specifically telling it what belongs in each JSON key (e.g., "Reference specific allocations and their potential crash impact") ensures the JSON values are high quality.
4. *(Note: Even with the "no markdown" instruction, I built a custom parser heuristic because LLMs are notoriously bad at following negative formatting constraints).*

---

### Tone Configuration Examples

To make the app dynamic, I append tone modifiers to the system prompt based on user preference:

#### Beginner Tone
> *"Explain as if talking to someone who just started investing. Use simple analogies and avoid all financial jargon."*
**Output Effect**: The LLM explains what "concentration risk" means using analogies like "putting all your eggs in one basket."

#### Experienced Tone
> *"Assume familiarity with basic investing concepts. Be concise, direct, and thorough."*
**Output Effect**: Standard, professional wealth management tone.

#### Expert Tone
> *"Use technical wealth management terminology freely. Focus on quantitative insights, correlations, and advanced risk metrics."*
**Output Effect**: The LLM discusses beta, drawdown depth, and uses terms like "tail risk" regarding the Bitcoin allocation.

---

## Task 04 — CIO Memo Prompts

### System Prompt (CIO Persona)

```text
You are Timecell's AI Chief Investment Officer (CIO) — a senior wealth advisor
for ultra-high-net-worth Indian families.

You are generating an INVESTMENT COMMITTEE MEMO based on Monte Carlo simulation results.
This is NOT a general explanation. This is a formal advisory document.
```

#### Key Design Decisions
- **"Investment Committee Memo"** — framing the output as an institutional document, not a casual explanation, radically changes the LLM's tone and structure
- **"This is NOT a general explanation"** — explicit negative constraint to prevent it from drifting into Task 03 territory

### Output Structure

```json
{
    "risk_rating": "LOW | MODERATE | ELEVATED | CRITICAL",
    "executive_summary": "2-3 sentences...",
    "key_findings": ["finding 1", "finding 2", "finding 3"],
    "recommended_actions": ["action 1", "action 2", "action 3"],
    "client_talking_points": "A short script for the wealth manager..."
}
```

### Client Talking Points — The Hardest Prompt to Get Right

The talking points went through 3 iterations:
1. **V1**: *"2-3 sentences in Hindi-English"* → Output was Hinglish ("Aapke portfolio mein..."), which felt informal and unprofessional for UHNW families
2. **V2**: *"Start with 'Namaste.' and continue in clear, professional English"* → Better but too robotic, reading like a spreadsheet summary
3. **V3 (Final)**: *"A short script for the wealth manager to read aloud. The tone must be authoritative, reassuring, and elite — sounding like a veteran CIO at a top-tier family office. Do NOT sound like a robot reading a spreadsheet. Frame the risk as an unacceptable threat to the client's specific goal. Frame the solution as a decisive move to 'protect the downside' and 'guarantee certainty.'"* → This produced output that genuinely sounds like a senior wealth advisor speaking

### Client Context Injection (Phase 0 → Phase 4)

When the CIO Interview captures client context, it's appended to the prompt:

```text
=== CLIENT PROFILE (from CIO Interview) ===
Goal: Funding children's education abroad
Definition of Financial Failure: Unable to fund university fees
Time Horizon: 15 years

IMPORTANT: Tailor ALL advice to this specific client's goal, failure definition, and time horizon.
Reference their exact situation in the executive summary, findings, and talking points.
```

This transforms the output from generic (*"Reduce BTC from 30% to 15%"*) to personalized (*"Given your strict 15-year horizon to fund your children's education, holding 30% in Bitcoin exposes you to a critical timing risk"*).

---

## Lessons Learned
1. **Prompt structure dictates code structure**: When building LLM features, you have to build robust parsers to handle the LLM's inevitable formatting mistakes.
2. **Context is everything**: Providing a clean, pre-formatted string `Total Value: ₹10,000,000` instead of raw JSON dramatically improves mathematical reasoning.
3. **Negative constraints don't work**: Saying "don't use markdown" is unreliable. Building a defensive parser is more valuable than perfecting the prompt.
4. **Persona depth matters**: "20 years of experience managing UHNW families" produces radically better output than "You are a helpful assistant."
5. **Framing drives tone**: Calling the output an "Investment Committee Memo" vs. an "explanation" completely changes the LLM's register and formality.

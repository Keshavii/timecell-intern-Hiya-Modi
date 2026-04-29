# Prompt Engineering Deep Dive — Task 03

## Overview
This document traces the full evolution of the prompts used in Task 03 (AI-Powered Portfolio Explainer) — from first draft to final version, with side-by-side output comparisons.

---

## Version 1 — Initial Attempt

```text
You are a wealth advisor. Explain the risk of this portfolio to a client.
Portfolio: {portfolio_json}
Tell them what they are doing well, what to change, and give a verdict (Aggressive, Balanced, Conservative).
```

### Problems with V1
1. **Generic Advice**: The LLM gave textbook advice ("diversify your portfolio") rather than analyzing the specific mathematical risks of the crash scenarios provided.
2. **Parsing Failures**: Because I didn't specify an output format, the LLM returned paragraphs of text. My application crashed because it expected structured data.
3. **Missing Cultural Context**: The tone was very westernized and didn't fit the "Indian wealth advisor" persona Timecell is building.

---

## Version 2 — Improvements

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

### What Changed & Why
- I added the explicit JSON structure so my application could actually parse and render the output.
- I explicitly stated "Indian wealth advisor" to ground the tone.
- **New Problem**: The LLM frequently wrapped the JSON in markdown blocks (` ```json ... ``` `), which broke standard `json.loads()`. It also still sometimes hallucinated numbers.

---

## Final Version

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

### Why It Works
1. **Strict Persona**: Telling it it has "20 years of experience" and serves "high-net-worth families" instantly elevates the tone from generic chatbot to premium advisor.
2. **Anti-Hallucination**: "Do not hallucinate data; only use the portfolio numbers provided" forces it to do the math.
3. **Structured Constraints**: Specifically telling it what belongs in each JSON key (e.g., "Reference specific allocations and their potential crash impact") ensures the JSON values are high quality.
4. *(Note: Even with the "no markdown" instruction, I built a custom parser heuristic because LLMs are notoriously bad at following negative formatting constraints).*

---

## Tone Configuration Examples

To make the app dynamic, I append tone modifiers to the system prompt based on user preference:

### Beginner Tone
> *"Explain as if talking to someone who just started investing. Use simple analogies and avoid all financial jargon."*
**Output Effect**: The LLM explains what "concentration risk" means using analogies like "putting all your eggs in one basket."

### Experienced Tone
> *"Assume familiarity with basic investing concepts. Be concise, direct, and thorough."*
**Output Effect**: Standard, professional wealth management tone.

### Expert Tone
> *"Use technical wealth management terminology freely. Focus on quantitative insights, correlations, and advanced risk metrics."*
**Output Effect**: The LLM discusses beta, drawdown depth, and uses terms like "tail risk" regarding the Bitcoin allocation.

---

## Lessons Learned
1. **Prompt structure dictates code structure**: When building LLM features, you have to build robust parsers in your code to handle the LLM's inevitable formatting mistakes.
2. **Context is everything**: Providing a clean, pre-formatted string `Total Value: ₹10,000,000` instead of just dumping raw JSON into the prompt drastically improves the LLM's mathematical reasoning.

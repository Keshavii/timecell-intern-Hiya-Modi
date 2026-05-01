# AI Tools Usage — Timecell Internship Assessment

## Tools Used
- **Antigravity (AI coding assistant)** — Architecture guidance, code generation, review, and debugging
- **Google Gemini (`gemini-2.5-flash`)** — LLM backend for Task 03 (portfolio explainer) and Task 04 (CIO memo generation)

## Workflow
My approach to AI-assisted development followed a deliberate 4-step cycle:
1. **Think** — Understand the problem and plan the approach independently before touching any AI tool
2. **Prompt** — Use AI to generate initial code scaffolding and suggest patterns
3. **Refine** — Review AI output critically, correct errors, improve variable names and logic
4. **Validate** — Test thoroughly, verify edge cases manually, run the code and inspect output

## Task-by-Task AI Usage

### Task 01 — Portfolio Risk Calculator
- **Architecture**: AI suggested the dataclass pattern (`models.py`) for type-safe portfolio representation. I accepted this because it provides built-in `__repr__`, immutability signals, and clean factory methods.
- **Edge Cases**: AI generated the initial list of edge cases to test (empty portfolio, 100% cash, zero expenses). I added the `negative allocation` and `crash-to-zero` cases myself after thinking about what a real user might input.
- **Math Verification**: I manually calculated the expected post-crash value for the sample portfolio (BTC: 3M × 0.2 = 0.6M, NIFTY: 4M × 0.6 = 2.4M, etc.) and used those as test assertions. The AI-generated formula was correct, but I didn't trust it until I verified by hand.
- **Visualizer**: The `rich` library boilerplate was AI-generated. The color-coding logic (red for >50% crash risk, yellow for concentration, green for safe assets) was my design decision.

### Task 02 — Live Market Data Fetch
- **Provider Pattern**: AI suggested the Abstract Base Class pattern. I adopted it because it enforces a clean contract and makes adding new data sources trivial.
- **API Selection**: I chose CoinGecko and yfinance myself based on the requirement for free, keyless APIs. AI helped with the specific API endpoint URLs and response parsing.
- **Error Handling**: The exponential backoff retry logic was AI-suggested. I refined the sleep times (1s, 2s) and added the graceful degradation pattern (creating an error `AssetPrice` instead of crashing) myself.
- **Where AI was wrong**: AI initially suggested using `ticker.info` for yfinance, which is slow and rate-limited. I overrode this to use `ticker.fast_info` after testing showed it was 5x faster and more reliable.

### Task 03 — AI-Powered Portfolio Explainer
- **Prompt Engineering**: This was the most iterative AI collaboration. I went through 3 prompt versions (documented in `docs/PROMPT_ENGINEERING.md`). AI helped draft the initial system prompt, but the key improvements — anti-hallucination constraints, Indian financial context, pre-formatted portfolio data — were my own iterations after observing output quality.
- **Output Parser**: AI generated the basic JSON extraction logic. I added the heuristic fallback (find first `{` and last `}`) after observing that Gemini frequently wraps JSON in markdown blocks despite explicit instructions not to.
- **Critic System**: The self-critique architecture (a second LLM call auditing the first) was my idea inspired by Constitutional AI papers. AI helped implement the `CRITIC_SYSTEM_PROMPT`.

### Task 04 — AI CIO Investment Committee Memo
- **Concept**: The Monte Carlo ruin probability idea was mine — inspired by the "Safe Withdrawal Rate" research in retirement planning (the 4% rule). I chose this because it directly extends Timecell's core "crash survival" metric from deterministic to stochastic analysis.
- **CIO Interview**: The interactive interview feature (Phase 0) was a deliberate product decision — not just engineering. It mirrors Timecell's philosophy of asking hard qualifying questions before giving advice. The implementation was mine; AI helped with the `rich` Panel formatting.
- **Implementation**: AI helped with the numpy vectorization pattern (matrix of random shocks). I corrected the monthly return conversion formula (AI initially suggested dividing volatility by 12 instead of √12).
- **Rebalancer**: The rebalancing heuristic (cap volatile assets at 15%, redirect to fixed income) was my design. AI helped structure the output format.
- **CIO Memo Prompt**: The prompt engineering for the IC Memo was my own work — specifically the 4-tier risk rating system, the instruction to frame risk as a threat to the client's goal, and the directive for elite CIO tone in the talking points.
- **Asset Profiles**: The historical return/volatility estimates for each asset class were sourced from publicly available data and manually entered.

## Where AI Helped Most
- **Boilerplate reduction**: Setting up `rich` tables, `pytest` fixtures, `dataclass` definitions — AI saved significant time on repetitive structural code.
- **API documentation**: AI quickly surfaced the correct CoinGecko endpoint format and yfinance `fast_info` interface.
- **Test scaffolding**: AI generated the initial test structure, which I then customized with specific mathematical assertions.

## Where I Had to Override AI
1. **yfinance `info` vs `fast_info`**: AI suggested the slower, less reliable `ticker.info` dictionary. I switched to `fast_info` after testing.
2. **Monthly volatility conversion**: AI initially divided annual volatility by 12 for Monte Carlo. The correct formula is dividing by √12 — a common error that would have produced wildly inaccurate simulation results.
3. **Prompt design**: AI's first prompt attempt was too generic ("You are a helpful assistant..."). I had to iteratively refine the persona, constraints, and output structure through 3 versions to get consistent, high-quality output.
4. **Concentration threshold**: AI suggested `>= 40%` for the concentration warning. The spec says `> 40%`, so I corrected to strict greater-than.
5. **Safety filters**: Gemini's safety filters were blocking financial advisory content. I had to explicitly disable them to get complete, untruncated CIO memo output.

# Timecell AI Internship — Technical Assessment
### Hiya's Submission

> An AI-powered wealth management toolkit: portfolio risk analysis, live market data, AI-driven explanations, and a creative open problem — built for [Timecell.ai](https://timecell.ai).

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.10+
- An API key for one of: Anthropic Claude (recommended), OpenAI, or Google Gemini

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/timecell-intern-hiya.git
cd timecell-intern-hiya

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your API key(s)
```

### Running Each Task

```bash
# Task 01 — Portfolio Risk Calculator
python -m task01_risk_calculator.risk_calculator

# Task 02 — Live Market Data Fetch
python -m task02_market_data.fetcher

# Task 03 — AI-Powered Portfolio Explainer
python -m task03_ai_explainer.explainer

# Task 04 — Portfolio Stress Test Simulator
python -m task04_open_problem.stress_tester

# Run all tests
pytest -v
```

---

## 📊 Task 01 — Portfolio Risk Calculator (30 pts)

### Approach
*[To be filled after implementation]*

### Key Design Decisions
- Used Python `dataclasses` for type-safe portfolio and asset models
- Implemented both worst-case and moderate crash scenarios (bonus)
- Built a pure-Python CLI bar chart for allocation visualization (bonus)

### Edge Cases Handled
- Empty portfolio (no assets)
- 100% CASH portfolio (zero crash impact)
- Zero monthly expenses (infinite runway)
- Allocations that don't sum to 100%
- Single-asset portfolios
- All assets crashing to zero

### How I Used AI
*[To be filled — document specific AI-assisted decisions]*

---

## 📡 Task 02 — Live Market Data Fetch (20 pts)

### Approach
- **Provider Pattern**: Created an Abstract Base Class (`DataProvider`) to enforce a standard contract (`fetch_price -> AssetPrice`).
- **Concrete Providers**: Implemented `YFinanceProvider` and `CoinGeckoProvider` to handle API-specific logic and standardize the output formatting.
- **Resilient Orchestrator**: The main `fetch_all_prices` function uses a loop with **exponential backoff** (retrying 1s, then 2s) and guarantees the script will never crash, even if the internet goes down.
- **Beautiful UI**: Used `rich` to render a clean terminal table that gracefully displays failed APIs inline rather than breaking the output.

### API Choices and Why
| Asset | Provider | Why |
|-------|----------|-----|
| BTC, ETH | CoinGecko | Free, no API key required, reliable |
| NIFTY 50 | yfinance | Free, covers Indian indices |
| RELIANCE | yfinance | NSE-listed stock, demonstrates Indian market coverage |
| GOLD | yfinance | Commodity coverage via futures ticker |

### Error Handling Strategy
- Per-asset `try/except` — one failure never crashes the whole fetch
- Structured logging via Python `logging` module
- Retry logic with exponential backoff
- Partial results displayed even when some fetches fail

---

## 🤖 Task 03 — AI-Powered Portfolio Explainer (30 pts)

### Approach
- Built a robust `ClaudeClient` wrapper around the Anthropic API (`claude-3-5-sonnet-20241022`).
- Wrote a custom heuristic JSON parser (`output_parser.py`) to safely extract data even when the LLM outputs conversational filler or markdown blocks.
- Added a **Self-Critique Bonus**: a second LLM call (`critic.py`) acting as a Senior Auditor that reviews the first LLM's advice for mathematical accuracy and actionability.
- Parameterized the tone using system prompt modifiers (`beginner`, `experienced`, `expert`).

### Why Claude?
Timecell's own platform is powered by Claude. Choosing Anthropic Claude as the LLM provider demonstrates alignment with the company's technical stack and philosophy.

### Prompt Engineering Journey
See [docs/PROMPT_ENGINEERING.md](docs/PROMPT_ENGINEERING.md) for the full prompt evolution — from v1 to final version, with before/after comparisons.

### What Worked, What Didn't
- **What didn't work**: In Version 1, simply asking for the JSON format resulted in the LLM giving generic advice like "diversify your assets" instead of actually doing the math on the crash percentages.
- **What worked**: Explicitly forbidding hallucination and demanding the LLM reference the numbers in the provided data (`format_portfolio_for_prompt`). Adding the heuristic parser to strip ```json blocks was also necessary, as LLMs frequently ignore "do not use markdown" instructions.

### Sample Outputs
Running the explainer on a 100% Crypto portfolio yields an "Aggressive" verdict, with the LLM specifically warning that a -80% crash on BTC will obliterate the 1 Crore total value, leaving an unsustainable runway. The self-critique engine successfully verified this logic.

---

## 🧪 Task 04 — Portfolio Stress Test Simulator (20 pts)

### Why I Built This
Timecell's core promise is **"crash survival, runway, portfolio math — with the reasoning, not just the answer."** 

While Task 1 handles *deterministic* risk (e.g., "If the market crashes exactly 40%, what happens?"), real-world wealth management deals with *stochastic* risk (randomness). This tool answers the most terrifying question a wealthy family has: **"What is the statistical probability that I run out of money before I die?"**

### How It Works (Monte Carlo Engine)
Using Python's `numpy` library for high-performance vectorized math, this script:
1. Calculates the weighted annualized return and volatility of the provided portfolio.
2. Generates a massive matrix of random market shocks simulating **10,000 independent 30-year timelines**.
3. Steps through each month, applying market chaos and deducting the family's monthly expenses.
4. Calculates exactly how many of those 10,000 timelines end in bankruptcy to compute the **Probability of Ruin**.

### Technical Elegance
By using vectorized operations instead of nested Python loops, the engine can simulate **3,600,000 individual months** of market data in a fraction of a second, demonstrating production-ready computational finance skills.

## 🤖 AI Tools Used

See [docs/AI_USAGE.md](docs/AI_USAGE.md) for a detailed breakdown of how AI tools were used across all tasks.

---

## 💡 Reflections

### Hardest Part & How I Approached It
*[To be filled after completion]*

---

## 📂 Project Structure

```
timecell-intern-hiya/
├── README.md                     # This file
├── requirements.txt              # Dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
│
├── task01_risk_calculator/       # Portfolio Risk Calculator
│   ├── __init__.py
│   ├── risk_calculator.py        # Core compute_risk_metrics()
│   ├── models.py                 # Dataclasses for Portfolio, Asset
│   ├── visualizer.py             # CLI bar chart (bonus)
│   ├── scenarios.py              # Multi-scenario analysis (bonus)
│   └── test_risk_calculator.py   # Unit tests
│
├── task02_market_data/           # Live Market Data Fetch
│   ├── __init__.py
│   ├── fetcher.py                # Main data fetcher
│   ├── providers/                # Data provider implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base class
│   │   ├── yfinance_provider.py  # Stock/index fetcher
│   │   └── coingecko_provider.py # Crypto fetcher
│   ├── formatter.py              # Terminal table formatter
│   └── test_fetcher.py           # Tests
│
├── task03_ai_explainer/          # AI-Powered Portfolio Explainer
│   ├── __init__.py
│   ├── explainer.py              # Main orchestrator
│   ├── prompts.py                # Prompt templates (versioned)
│   ├── llm_client.py             # LLM API wrapper
│   ├── output_parser.py          # Structured output extraction
│   ├── critic.py                 # Self-critique (bonus)
│   └── test_explainer.py         # Tests
│
├── task04_open_problem/          # Portfolio Stress Test Simulator
│   ├── __init__.py
│   ├── README.md                 # Detailed explanation
│   ├── stress_tester.py          # Main implementation
│   └── test_stress_tester.py     # Tests
│
└── docs/
    ├── AI_USAGE.md               # AI tool usage documentation
    └── PROMPT_ENGINEERING.md     # Prompt design deep dive
```

---

*Built with ❤️ for the Timecell AI Summer Internship 2025*

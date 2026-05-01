# Timecell AI Internship — Technical Assessment

> An AI-powered wealth management toolkit that mirrors Timecell's core philosophy: **act like a private Chief Investment Officer**, not a dashboard. Portfolio risk analysis, live market data, AI-driven explanations, and a creative open problem — built for [Timecell.ai](https://timecell.ai).

---

## Objective

This project is my submission for the Timecell AI Summer Internship 2025 Technical Assessment. It comprises four tasks that collectively demonstrate the skills required for an Engineering Intern role in AI & Fintech:

1. **Quantitative Thinking** — A portfolio risk calculator with deterministic and stochastic crash analysis
2. **Resilient Data Engineering** — A live market data fetcher with exponential backoff and graceful degradation
3. **AI/LLM Integration** — A prompt-engineered portfolio explainer with self-critique and configurable tone
4. **Product Judgment & Initiative** — An original AI CIO Memo pipeline that embodies Timecell's product philosophy

Every task was built with the same question in mind: *"Would Timecell ship this?"*

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/amitamodi/timecell-intern-hiya.git
cd timecell-intern-hiya

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running Each Task

```bash
# Task 01 — Portfolio Risk Calculator (chart + scenario comparison)
python -m task01_risk_calculator.risk_calculator

# Task 02 — Live Market Data Fetch
python -m task02_market_data.fetcher

# Task 03 — AI-Powered Portfolio Explainer
python -m task03_ai_explainer.explainer                          # Default portfolio
python -m task03_ai_explainer.explainer --portfolio examples/sample_portfolio.json  # Custom portfolio
python -m task03_ai_explainer.explainer --tone beginner --critic  # Beginner tone + self-critique

# Task 04 — AI CIO Investment Committee Memo
python -m task04_open_problem.stress_tester

# Run all tests (28 tests)
pytest -v
```

---

## 📊 Task 01 — Portfolio Risk Calculator (30 pts)

### The Problem
Given a portfolio of assets, compute key risk metrics that a wealth manager would use to assess whether the portfolio is safe.

### My Approach & Thought Process
I built a modular risk engine with four cleanly separated concerns, because in production fintech, you never want your math tangled with your presentation layer:

1. **Models** (`models.py`) — Type-safe `Portfolio` and `Asset` dataclasses with `from_dict()` factory methods. I chose dataclasses over raw dicts because they catch malformed input at construction time rather than deep inside a calculation loop.
2. **Calculator** (`risk_calculator.py`) — A pure function `compute_risk_metrics()` that processes each asset independently, computing post-crash values using the remaining-value multiplier approach (`1 + crash_pct/100`), then aggregates for portfolio-level metrics.
3. **Visualization** (`visualizer.py`) — A color-coded CLI bar chart using `rich`, dynamically colored by risk level (red for high-crash assets, yellow for concentration, green for safe havens).
4. **Scenarios** (`scenarios.py`) — A multi-scenario analyzer that reuses the core calculator with halved crash magnitudes for a moderate-case comparison.

### Why This Design Aligns with Timecell
Timecell runs inside Claude Code — a terminal, not a dashboard. My CLI bar chart and rich table output mirror that philosophy: beautiful terminal-first UX that a wealth manager can glance at instantly.

### Edge Cases Handled
- Empty portfolio (no assets) · 100% CASH portfolio (zero crash impact) · Zero monthly expenses (infinite runway) · Allocations that don't sum to 100% · Single-asset portfolios · All assets crashing to zero · Negative allocation validation

### Bonuses Implemented
- ✅ Multi-scenario comparison (worst case + moderate case side-by-side)
- ✅ Pure-Python CLI bar chart for allocation visualization

### How I Used AI
- AI scaffolded the dataclass pattern and initial module structure
- AI suggested the comprehensive edge case list — I validated each scenario by computing the math by hand (e.g., BTC: 3M × 0.2 = 0.6M, NIFTY: 4M × 0.6 = 2.4M → Total: 5.7M → 71.25 months runway)
- The CLI bar chart color scheme and risk-based coloring logic was my own design decision; AI generated the `rich` library boilerplate

---

## 📡 Task 02 — Live Market Data Fetch (20 pts)

### The Problem
Build a resilient data fetcher that pulls real-time asset prices from multiple APIs without ever crashing.

### My Approach & Thought Process
In production fintech, data pipelines fail silently all the time — APIs go down, rate limits hit, networks flake. I designed around this reality:

- **Provider Pattern**: Created an Abstract Base Class (`DataProvider`) to enforce a standard contract (`fetch_price → AssetPrice`). This makes adding a new data source (e.g., Alpha Vantage) a single-file change.
- **Concrete Providers**: `YFinanceProvider` (Indian equities + commodities) and `CoinGeckoProvider` (crypto). Both normalize output into the same `AssetPrice` format.
- **Resilient Orchestrator**: The main `fetch_all_prices` function wraps each fetch in exponential backoff retries (1s, then 2s) and guarantees the script never crashes, even if the internet goes down entirely.

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
- Retry logic with exponential backoff (up to 2 retries)
- Partial results displayed even when some fetches fail — never a blank screen

### Why This Design Aligns with Timecell
Timecell connects to live market data as a core product feature. Demonstrating that I can build a fetcher that *never crashes* and *always shows partial results* proves I understand what production data engineering looks like.

---

## 🤖 Task 03 — AI-Powered Portfolio Explainer (30 pts)

### The Problem
Use an LLM to generate a plain-English explanation of a portfolio's risk — in the tone of a friendly but honest financial advisor talking to a non-expert client.

### My Approach & Thought Process
This task required three distinct skills working together: prompt engineering, robust LLM output parsing, and clean code architecture.

**Architecture** (6 modules, strict separation of concerns):
- `explainer.py` — Main orchestrator
- `prompts.py` — Versioned prompt templates with documented evolution
- `llm_client.py` — Thin wrapper around Google Gemini API (`gemini-2.5-flash`)
- `output_parser.py` — Heuristic JSON parser that handles LLM formatting quirks
- `critic.py` — Self-critique engine (bonus: second LLM call audits the first)
- `test_explainer.py` — Unit tests for parser and prompt formatting

### LLM Provider Choice: Google Gemini
I chose Google Gemini (`gemini-2.5-flash`) for several reasons:
- Free tier with generous rate limits for development
- Extremely fast inference — important for a good developer experience during testing
- High-quality structured JSON output with minimal formatting errors
- The `LLMClient` wrapper is provider-agnostic by design — swapping to Claude or GPT-4 requires changing only the constructor

### Prompt Engineering Journey
See [docs/PROMPT_ENGINEERING.md](docs/PROMPT_ENGINEERING.md) for the full evolution, but in summary:
- **V1 (Failed):** Generic prompt → LLM gave textbook advice like "diversify your portfolio" instead of analyzing the actual crash percentages
- **V2 (Better):** Added JSON structure → LLM wrapped output in markdown blocks, breaking the parser. Also hallucinated numbers.
- **V3 (Final):** Anti-hallucination constraints + Indian financial context + pre-formatted portfolio data as human-readable text → Consistent, mathematically grounded, culturally appropriate output

**The key insight:** Providing a clean, pre-formatted string (`Total Value: ₹10,000,000`) instead of dumping raw JSON into the prompt dramatically improved the LLM's mathematical reasoning.

### What Didn't Work & How I Fixed It
- LLMs reliably ignore "don't use markdown" instructions. I built a defensive heuristic parser (`output_parser.py`) that strips `\`\`\`json` blocks and finds the first `{` to last `}` substring. Engineering around the LLM's weaknesses turned out to be more valuable than trying to prompt them away.

### Bonuses Implemented
- ✅ Configurable tone (beginner / experienced / expert) via system prompt modifiers
- ✅ Self-critique engine — a second LLM call acts as a Senior Wealth Management Auditor reviewing the first response for mathematical accuracy and actionability
- ✅ Cross-task integration — displays Task 01's deterministic risk metrics alongside the LLM's qualitative analysis

---

## 🧪 Task 04 — AI CIO Investment Committee Memo (20 pts)

### Why I Built This
Task 04 had no specification — *that was the point.* I read the Timecell website, the assessment brief, and Sandeep's note at the bottom: *"The first engineering hire at a startup does not wait to be told what to build."*

Timecell's core product philosophy is acting as a **private Chief Investment Officer** for wealthy Indian families. A real CIO doesn't just show you a dashboard — they *interrogate your goals, run the numbers, and present a formal advisory document.* 

So I built exactly that: a 5-phase pipeline that transforms raw portfolio data into an institutional-grade Investment Committee Memo, personalized to each client's specific goals.

### How It Works (5-Phase Pipeline)

| Phase | What Happens | Module |
|-------|-------------|--------|
| **Phase 0: CIO Interview** | Asks 3 qualifying questions — the client's goal, their definition of financial failure, and their time horizon. This context personalizes everything downstream. | `stress_tester.py` |
| **Phase 1: Monte Carlo Engine** | Runs 10,000 stochastic market simulations using numpy vectorization, across the client's specific time horizon | `stress_tester.py` |
| **Phase 2: Rebalancing Engine** | Pure-logic module that caps volatile assets at 15% and redirects freed allocation to fixed income | `rebalancer.py` |
| **Phase 3: Proof by Re-simulation** | Re-runs Monte Carlo on the rebalanced portfolio to **mathematically prove** the improvement in ruin probability | `stress_tester.py` |
| **Phase 4: AI CIO Memo** | Feeds all simulation data + client context into Gemini, which generates an institutional Investment Committee Memo | `cio_memo.py` |

### What Makes This Different From Task 03
This is the most important distinction in the entire project:

| | Task 03 (Explainer) | Task 04 (CIO Memo) |
|---|---|---|
| **Role** | Financial educator | Institutional decision-maker |
| **Input** | Raw portfolio | Monte Carlo simulation results + client goals |
| **Output** | Plain-English explanation | Investment Committee Memo |
| **Key Feature** | Tone adjustment | Before/after rebalancing proof |
| **Quantitative** | References crash percentages | Runs 10,000 stochastic simulations |
| **Personalization** | Generic | Tailored to client's specific goal and failure definition |

### The CIO Interview (Phase 0) — Why It Matters
The interview transforms this tool from a **calculator** into a **consultant.** Instead of immediately crunching numbers, the terminal pauses and asks:

1. **"What is this capital meant to achieve?"** (e.g., Generational wealth, Children's education)
2. **"What does financial failure look like?"** (e.g., Falling below ₹50 Lakhs)
3. **"What is your real time horizon?"** (e.g., 15 years)

The answers are injected into the Gemini prompt, producing hyper-personalized advice. Without the interview, the AI says *"Reduce BTC from 30% to 15%."* With the interview, it says *"Given your strict 15-year horizon to fund generational wealth, holding 30% in Bitcoin exposes you to a critical timing risk."*

This is Timecell's entire differentiation — the product asks hard qualifying questions before giving advice. No other product does this.

### Risk Rating System
The pipeline uses a consistent 4-tier risk rating system across both the Python terminal output and the AI CIO Memo:

| Rating | Ruin Probability | What It Means |
|--------|-----------------|---------------|
| 🟢 LOW | < 5% | Portfolio is highly likely to survive the full time horizon |
| 🟡 MODERATE | 5% – 10% | Generally stable, minor rebalancing suggested |
| 🟠 ELEVATED | 10% – 20% | Uncomfortably high risk — immediate rebalancing mandated |
| 🔴 CRITICAL | > 20% | Financially dangerous — drastic reallocation required |

### Technical Elegance
- The Monte Carlo engine simulates **3,600,000 individual months** of market data in under a second using numpy vectorization
- The rebalancer (`rebalancer.py`) is pure Python logic with zero LLM dependency, making it fully unit-testable
- The CIO doesn't just *opine* — it **proves** its recommendation by re-running the simulation on the proposed portfolio

See [task04_open_problem/README.md](task04_open_problem/README.md) for the full technical deep dive and test coverage.

---

## 🤖 AI Tools Used

See [docs/AI_USAGE.md](docs/AI_USAGE.md) for a detailed, per-task breakdown. In summary:

- **Antigravity (AI coding assistant)** — Architecture guidance, code generation, review, and debugging
- **Google Gemini (`gemini-2.5-flash`)** — LLM backend for Task 03 (portfolio explainer) and Task 04 (CIO memo generation)

My AI workflow followed a deliberate 4-step cycle: **Think → Prompt → Refine → Validate.** I never committed AI-generated code without understanding every line and verifying the math by hand.

**Where I overrode AI:**
1. AI suggested `ticker.info` for yfinance (slow, rate-limited) — I switched to `fast_info` after testing
2. AI divided annual volatility by 12 for Monte Carlo — the correct formula is `σ/√12` (a common error that would have produced wildly inaccurate results)
3. AI's first prompt attempt was too generic — I iterated through 3 versions to get consistent, grounded output

---

## 💡 Reflections: The Hardest Parts & How I Approached Them

### 1. Product Sense > Just Writing Code (Task 04)
The hardest part was figuring out what Task 04 should actually be. My first instinct was a standard Monte Carlo stress tester — solid math, nice output, done. But after reading Timecell's product philosophy more carefully, I realized the Monte Carlo alone didn't answer the real question: "does this person understand what we're building?" Timecell isn't a calculator — it's a CIO that asks hard questions before giving advice.

So, I scrapped the generic approach and rebuilt Task 04 as an interactive CIO Interview pipeline that captures a client's goals and failure definitions before running the simulations. It then feeds that human context into Gemini to produce hyper-personalized advice. Deciding what not to build, and focusing purely on what would actually matter to a wealth manager using this tool, took more effort than writing the code.

### 2. Defensive Engineering: Taming the LLM (Task 03)
On the strictly technical side, getting the LLM to consistently produce structured, mathematically grounded advice instead of generic platitudes was a massive challenge. When the LLM repeatedly ignored "do not use markdown" instructions for JSON outputs, I realized trying to "prompt away" its weaknesses was a losing battle. Instead, I took a defensive engineering approach and built a heuristic parser (`output_parser.py`) designed to automatically strip markdown and extract the JSON payload. Engineering around the AI's flaws proved far more reliable than hoping it would behave.

### 3. High-Performance Stochastic Math
Finally, ensuring the Monte Carlo engine could simulate 3,600,000 individual market shocks in a fraction of a second without ruining the terminal UX was a fun challenge. It required catching a subtle but critical math error — the monthly volatility conversion must use `σ/√12`, not `σ/12` — and strictly utilizing numpy vectorization and matrix broadcasting to ensure the simulation executes in under 0.2 seconds.

---

## 📂 Project Structure

```
timecell-intern-hiya/
├── README.md                     # This file
├── requirements.txt              # Dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore rules
│
├── task01_risk_calculator/       # Portfolio Risk Calculator (30 pts)
│   ├── __init__.py
│   ├── risk_calculator.py        # Core compute_risk_metrics()
│   ├── models.py                 # Dataclasses for Portfolio, Asset
│   ├── visualizer.py             # CLI bar chart (bonus)
│   ├── scenarios.py              # Multi-scenario analysis (bonus)
│   └── test_risk_calculator.py   # 10 unit tests
│
├── task02_market_data/           # Live Market Data Fetch (20 pts)
│   ├── __init__.py
│   ├── fetcher.py                # Resilient data fetcher
│   ├── providers/                # Data provider implementations
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base class
│   │   ├── yfinance_provider.py  # Stock/index fetcher
│   │   └── coingecko_provider.py # Crypto fetcher
│   ├── formatter.py              # Terminal table formatter
│   └── test_fetcher.py           # 4 tests (mocked network calls)
│
├── task03_ai_explainer/          # AI-Powered Portfolio Explainer (30 pts)
│   ├── __init__.py
│   ├── explainer.py              # Main orchestrator
│   ├── prompts.py                # Prompt templates (versioned, documented)
│   ├── llm_client.py             # LLMClient — Google Gemini wrapper
│   ├── output_parser.py          # Heuristic JSON extraction
│   ├── critic.py                 # Self-critique engine (bonus)
│   └── test_explainer.py         # 5 tests (parser + formatter)
│
├── task04_open_problem/          # AI CIO Investment Committee Memo (20 pts)
│   ├── __init__.py
│   ├── README.md                 # Detailed rationale & test coverage
│   ├── stress_tester.py          # Monte Carlo engine + CIO Interview + pipeline
│   ├── rebalancer.py             # Pure-logic portfolio rebalancer
│   ├── cio_memo.py               # AI CIO memo generator (Gemini)
│   └── test_stress_tester.py     # 9 tests
│
├── examples/
│   └── sample_portfolio.json     # Sample portfolio for Task 03 CLI
│
└── docs/
    ├── AI_USAGE.md               # AI tool usage documentation
    └── PROMPT_ENGINEERING.md     # Prompt design deep dive
```

### Test Summary
- **28 total tests** across all 4 tasks
- All passing: `pytest -v` → `28 passed`
- Tests cover: math correctness, edge cases, error handling, network failures (mocked), JSON parsing edge cases, rebalancer invariants, and integration tests

---

*Built with ❤️ for the Timecell AI Summer Internship 2025*

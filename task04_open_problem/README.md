# Task 04 — AI CIO Investment Committee Memo

## The Philosophy

Timecell's product isn't just a dashboard — it acts as a **private Chief Investment Officer** for high-net-worth Indian families. This tool embodies that philosophy: a 5-phase pipeline that **interviews, analyzes, rebalances, re-proves, and advises.**

The key insight: A real CIO never looks at a spreadsheet without first asking, *"Who is this money for, and what are they trying to achieve?"*

## Why This Is Not Task 03

| | Task 03 (Explainer) | Task 04 (CIO Memo) |
|---|---|---|
| **Role** | Financial educator | Institutional decision-maker |
| **Input** | Raw portfolio | Monte Carlo results + client goals |
| **Output** | Plain-English explanation | Investment Committee Memo |
| **Key Feature** | Tone adjustment | Before/after rebalancing proof |
| **Quantitative** | References crash percentages | Runs 10,000 stochastic simulations |
| **Personalization** | Generic | Tailored to client's goal, failure definition, and time horizon |

## The 5-Phase Pipeline

### Phase 0: CIO Interview (`conduct_cio_interview()`)
Before running any numbers, the terminal pauses and asks three qualifying questions:
1. **"What is this capital meant to achieve?"** — Captures the client's goal (generational wealth, education, retirement)
2. **"What does financial failure look like?"** — Defines the client's personal risk threshold
3. **"What is your real time horizon?"** — Drives the actual simulation length (not hardcoded)

The answers are stored in a `client_context` dict and injected into Phase 4's Gemini prompt, producing hyper-personalized advice. The time horizon also directly controls the Monte Carlo engine (Phase 1 and 3).

### Phase 1: Monte Carlo Engine (`run_monte_carlo()`)
Using numpy vectorization, simulates **10,000 independent market paths** across the client's time horizon:
- Calculates weighted portfolio return (μ) and volatility (σ) from asset profiles
- Converts to monthly distributions (μ/12, σ/√12)
- Generates a `(10,000 × months)` matrix of random market shocks
- Deducts monthly expenses, tracks ruin events
- Outputs: ruin probability, percentile bands (5th, 25th, 50th, 75th, 95th)

### Phase 2: Rebalancing Engine (`rebalancer.py`)
Pure Python logic (no LLM dependency = fully testable):
- Identifies high-volatility assets (crash risk > 50%) with over-concentrated allocations (> 15%)
- Caps volatile assets at 15% maximum
- Redirects freed allocation to Fixed Income
- Returns a structured diff of changes with reasons

### Phase 3: Proof by Re-simulation
Re-runs the Monte Carlo engine on the rebalanced portfolio:
- Uses the same 10,000 simulations × same time horizon
- Calculates the **improvement** in ruin probability
- This is the killer feature: the CIO doesn't just opine — it **mathematically proves** its recommendation

### Phase 4: AI CIO Memo (`cio_memo.py`)
Feeds all simulation data + client context to Gemini, which generates an institutional Investment Committee Memo:
- **Risk Rating**: LOW / MODERATE / ELEVATED / CRITICAL (consistent with terminal output)
- **Executive Summary**: 2-3 sentences referencing exact simulation numbers and the client's goal
- **Key Findings**: Data-driven insights tied to the client's failure definition
- **Recommended Actions**: Specific, actionable steps with exact numbers
- **Client Talking Points**: An authoritative, elite-sounding script for a relationship manager to read aloud

## Risk Rating System

| Rating | Ruin Probability | Meaning |
|--------|-----------------|---------|
| 🟢 LOW | < 5% | Highly likely to survive the full time horizon |
| 🟡 MODERATE | 5% – 10% | Generally stable, minor rebalancing suggested |
| 🟠 ELEVATED | 10% – 20% | Uncomfortably high — immediate rebalancing mandated |
| 🔴 CRITICAL | > 20% | Financially dangerous — drastic reallocation required |

## Sample Output Flow

```
Phase 0: CIO Interview → Goal: "Children's education" · Failure: "Below ₹50L" · Horizon: 15 years
Phase 1: Monte Carlo → Ruin Probability: 12.43%
Phase 2: Rebalancer → BTC: 30% → 15%, +15% Fixed Income
Phase 3: Re-simulate → New Ruin Probability: 6.58% (↓ 5.85 pp)
Phase 4: CIO Memo → RISK RATING: ELEVATED → Personalized Findings → Elite Talking Points
```

## Test Coverage (9 tests)

| Test Name | What It Verifies |
|------|-----------------|
| `test_monte_carlo_runs_successfully` | Engine returns correct structure + percentile ordering |
| `test_guaranteed_ruin` | 100% ruin when monthly expenses massively exceed capital |
| `test_guaranteed_survival` | 0% ruin when capital is virtually infinite |
| `test_invalid_portfolio` | Gracefully raises ValueError on empty/zero portfolio |
| `test_rebalancer_caps_volatile_assets` | BTC successfully capped from 30% → 15% |
| `test_rebalancer_no_changes_needed` | A conservative 100% CASH portfolio remains untouched |
| `test_rebalancer_preserves_portfolio_total` | Ensures the mathematical invariant (allocations = 100%) holds |
| `test_rebalanced_portfolio_reduces_ruin` | Integration: Proves that Phase 2's output actually improves Phase 1's metrics |
| `test_cio_format_includes_key_data` | Ensures the LLM prompt is injected with all critical deterministic data |

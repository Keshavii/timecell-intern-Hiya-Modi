# Task 04 — Monte Carlo Ruin Probability Simulator

## The Original Idea vs The Refined Implementation

The initial roadmap proposed a deterministic historical crash simulator. However, Timecell's philosophy emphasizes deep quantitative reasoning, not just bolting APIs together. 

To demonstrate true fintech engineering capabilities, I pivoted to building a **Stochastic Monte Carlo Simulator**. 

## Why This Matters for Timecell

While Task 1 handles *deterministic* risk (e.g., "If the market crashes exactly 40%, what happens?"), real-world wealth management deals with *stochastic* risk (randomness).

This tool answers the most terrifying question a wealthy family has: **"What is the mathematical probability that I run out of money before I die?"**

## How It Works

Using Python's `numpy` library for high-performance vectorized math, this script:
1. Calculates the weighted annualized return (μ) and volatility (σ) of the provided portfolio.
2. Converts these to monthly distributions.
3. Generates a massive matrix of random market shocks simulating **10,000 independent 30-year timelines**.
4. Steps through each month, applying market chaos and deducting the family's monthly expenses.
5. Calculates exactly how many of those 10,000 timelines end in bankruptcy (Value = 0) to compute the **Probability of Ruin**.

## Technical Elegance
By using vectorized operations instead of nested Python loops, the engine can simulate 3,600,000 individual months of market data in a fraction of a second, demonstrating production-ready computational finance skills.

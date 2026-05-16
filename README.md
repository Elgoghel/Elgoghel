![Sharpe ratio across all 5 seeds, 2024 OOS, from Every Seed Every Result (Elgoghel 2026)](https://cdn.jsdelivr.net/gh/Elgoghel/Elgoghel@main/assets/sharpe-chart-animated.svg)

## Marwan Elgoghel

Software Engineering + Math & Stats minors at Monmouth University. Graduating May 2027. Building ML systems for financial and prediction markets.

### Research

**[Every Seed, Every Result](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6382938)** (SSRN preprint, March 2026)

Financial RL papers cherry-pick seeds. Train 5 agents (same code, same data, different random seed), publish only the best one. Your reported Sharpe inflates 15%, CAGR nearly doubles. The fix is the one clinical trials use: intent-to-treat. Pre-register every seed, report every outcome, no exclusions. To walk the talk I trained a 26.5M SAC on the S&P 500 with 5 pre-registered seeds. ITT median 2024 OOS Sharpe: 1.73, which does not beat SPY's 1.87. The protocol made me say so.

### Shipping

**[Seed Ledger](https://seedledger.onrender.com)** is a site for showing research alongside the actual seeds and metrics behind it, so claims are auditable instead of cherry-picked. Same philosophy as the paper. Full stack built solo: FastAPI plus SQLAlchemy on the backend, React 19 on the frontend, Postgres on Render. [Code](https://github.com/Elgoghel/seedledger).

**Polymarket / Kalshi trading bot** runs live with real capital. Risk-first by design: hard kill switches, fractional Kelly sizing, drawdown limits before clever signals. Private repo.

### Currently

Looking for SWE and ML internships, Summer 2026. NYC, NJ, or remote.

### Contact

elgoghel@gmail.com  ·  [linkedin.com/in/marwanelgoghel](https://linkedin.com/in/marwanelgoghel)

*Last updated: 2026-05-15*

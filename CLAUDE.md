# noarb

Static-arbitrage detector for vanilla options + futures, formulated as a linear program.

## Commands
- `uv sync` — create/update `.venv` (Python 3.13, see `.python-version`)
- `uv run pytest` — tests
- `uv run python examples/parity_example.py` — demo

## Layout
- `src/noarb/instrument.py` — `Instrument` (call/put/future, bid/ask, sizes, payoff)
- `src/noarb/lp.py` — `build_lp` / `find_arbitrage`; LP formulation in the module docstring
- `tests/` — known-arbitrage and no-arbitrage markets

## Model
- One LP per expiry (each expiry has its own future).
- Variables: separate buy (at ask) and sell (at bid) amounts per instrument, bounded by quote size, plus free `t` = guaranteed payoff at expiry.
- Objective: maximise cash today + DF * t.
- States: S = 0 and every strike, plus a slope >= 0 constraint above the top strike. Exact because payoffs are piecewise linear with kinks only at strikes.
- scipy `linprog` form is `A_ub @ x <= b_ub`, so ">=" constraints are negated. Duals of state rows = state prices (FTAP).
- Futures cost nothing today; their trade price is paid at expiry.

## Assumptions / not yet handled
- European exercise, single discount factor `DF`, flat per-unit `fee`.
- No margin, no calendar (cross-expiry) arbitrage, no live data feed.

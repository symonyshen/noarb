# noarb

Detects static (risk-free) arbitrage in a universe of vanilla options and
futures on a single expiry, by solving a linear program.

An arbitrage is a portfolio that costs nothing (or pays you) today and never
loses money at expiry, whatever the underlying does. By the Fundamental
Theorem of Asset Pricing, none exists exactly when positive state prices
exist that price every instrument — the LP's dual values are those prices.

## Setup

```bash
uv sync
```

## Usage

```python
from noarb import Instrument, find_arbitrage

universe = [
    Instrument("F",   "future",  0, 99.9, 100.0, 10, 10),
    Instrument("C95", "call",   95,  6.8,   7.0, 10, 10),
    Instrument("P95", "put",    95,  3.0,   3.2, 10, 10),
]
result = find_arbitrage(universe)
print(result.profit, result.trades)
```

```bash
uv run python examples/parity_example.py
uv run pytest
```

## How it works

See the docstring in `src/noarb/lp.py` for the LP formulation.

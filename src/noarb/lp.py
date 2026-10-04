"""Static-arbitrage detection for one expiry as a linear program.

Variables x = [buy_1..buy_n, sell_1..sell_n, t], all trades >= 0 and capped
by quoted size; t (free) is the amount guaranteed at expiry.

    maximise   cash_today . x  +  DF * t
    subject to payoff(S_j) . x >= t   for S_j in {0} U strikes
               slope . x       >= 0   (payoff not falling above top strike)

Portfolio payoffs are piecewise linear with kinks only at strikes, so these
finitely many constraints guarantee payoff >= t for every S >= 0.

scipy's linprog wants A_ub @ x <= b_ub, so both ">=" rows are negated.
The duals of the state rows are the implied state prices.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from noarb.instrument import Instrument


@dataclass
class ArbitrageResult:
    profit: float                      # present value of locked-in profit
    trades: dict[str, float]           # e.g. {"BUY C95": 10.0, "SELL F": 10.0}
    guaranteed_payoff: float           # t: amount received at expiry in every state
    state_prices: dict[float, float]   # grid point S_j -> dual value

    @property
    def is_arbitrage(self) -> bool:
        return bool(self.trades)


def build_lp(instruments: list[Instrument], DF: float = 1.0, fee: float = 0.0):
    """Return (c, A_ub, b_ub, bounds, grid) in scipy.optimize.linprog form."""
    grid = [0.0] + sorted({i.strike for i in instruments if i.kind != "future"})

    cash, pay, slope = [], [], []
    for i in instruments:  # BUY variables: pay ask (options today, futures at expiry)
        fut = i.kind == "future"
        cash.append(0.0 if fut else -i.ask)
        pay.append([i.payoff(S) - (i.ask if fut else 0.0) for S in grid])
        slope.append(i.slope_at_infinity())
    for i in instruments:  # SELL variables: receive bid
        fut = i.kind == "future"
        cash.append(0.0 if fut else i.bid)
        pay.append([-(i.payoff(S) - (i.bid if fut else 0.0)) for S in grid])
        slope.append(-i.slope_at_infinity())

    cash = np.array(cash) - fee
    P = np.array(pay).T  # (states) x (2n)

    c = -np.append(cash, DF)  # linprog minimises
    A_ub = np.vstack([
        np.hstack([-P, np.ones((len(grid), 1))]),  # t - payoff(S_j) <= 0
        np.append(-np.array(slope), 0.0),          # -slope <= 0
    ])
    b_ub = np.zeros(len(grid) + 1)
    bounds = ([(0, i.ask_size) for i in instruments]
              + [(0, i.bid_size) for i in instruments]
              + [(None, None)])
    return c, A_ub, b_ub, bounds, grid


def find_arbitrage(instruments: list[Instrument], DF: float = 1.0, fee: float = 0.0,
                   min_profit: float = 1e-9) -> ArbitrageResult:
    """Find the most profitable static arbitrage among `instruments` (one expiry)."""
    c, A_ub, b_ub, bounds, grid = build_lp(instruments, DF, fee)
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")

    profit = float(-res.fun)
    x = res.x
    n = len(instruments)
    trades: dict[str, float] = {}
    if profit > min_profit:
        for k, i in enumerate(instruments):
            if x[k] > 1e-9:
                trades[f"BUY {i.name}"] = float(x[k])
            if x[n + k] > 1e-9:
                trades[f"SELL {i.name}"] = float(x[n + k])

    state_prices = {S: float(-m) for S, m in zip(grid, res.ineqlin.marginals[: len(grid)])}
    return ArbitrageResult(
        profit=profit if trades else 0.0,
        trades=trades,
        guaranteed_payoff=float(x[-1]),
        state_prices=state_prices,
    )

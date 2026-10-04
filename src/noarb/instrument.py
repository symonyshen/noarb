from dataclasses import dataclass
from typing import Literal

Kind = Literal["call", "put", "future"]


@dataclass(frozen=True)
class Instrument:
    """A tradable contract on one expiry, quoted with bid/ask and sizes.

    For a future, `strike` is ignored; its trade price (bid or ask) is
    paid at expiry rather than today.
    """

    name: str
    kind: Kind
    strike: float
    bid: float
    ask: float
    bid_size: float
    ask_size: float

    def payoff(self, S: float) -> float:
        """Payoff at expiry of one long unit when the underlying ends at S,
        before subtracting the trade price (futures handle that separately)."""
        if self.kind == "call":
            return max(S - self.strike, 0.0)
        if self.kind == "put":
            return max(self.strike - S, 0.0)
        return S

    def slope_at_infinity(self) -> float:
        """d(payoff)/dS for S above every strike."""
        return 1.0 if self.kind in ("call", "future") else 0.0

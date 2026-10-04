"""Put-call parity violation: C95 - P95 = 4 < F - K = 4.9 (at the futures bid)."""

from noarb import Instrument, find_arbitrage

universe = [
    Instrument("F",    "future",   0,  99.9, 100.0, 10, 10),
    Instrument("C95",  "call",    95,   6.8,   7.0, 10, 10),
    Instrument("P95",  "put",     95,   3.0,   3.2, 10, 10),
    Instrument("C100", "call",   100,   4.0,   4.2, 10, 10),
    Instrument("P100", "put",    100,   4.0,   4.2, 10, 10),
]

result = find_arbitrage(universe)
print(f"arbitrage: {result.is_arbitrage}")
print(f"profit:    {result.profit:.4f}")
for trade, qty in result.trades.items():
    print(f"  {trade:<10} {qty:g}")

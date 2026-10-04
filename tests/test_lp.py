import pytest

from noarb import Instrument, find_arbitrage


def market(c95_bid, c95_ask, p95_bid, p95_ask):
    return [
        Instrument("F",    "future",   0,  99.9, 100.0, 10, 10),
        Instrument("C95",  "call",    95, c95_bid, c95_ask, 10, 10),
        Instrument("P95",  "put",     95, p95_bid, p95_ask, 10, 10),
        Instrument("C100", "call",   100,   4.0,   4.2, 10, 10),
        Instrument("P100", "put",    100,   4.0,   4.2, 10, 10),
    ]


def test_parity_violation_is_found():
    result = find_arbitrage(market(6.8, 7.0, 3.0, 3.2))
    # 10 x (F_bid - K - (C_ask - P_bid)) = 10 x (99.9 - 95 - 4)
    assert result.profit == pytest.approx(9.0)
    assert result.trades == pytest.approx({"BUY C95": 10, "SELL P95": 10, "SELL F": 10})


def test_fair_market_has_no_arbitrage():
    result = find_arbitrage(market(7.0, 7.2, 2.0, 2.2))
    assert not result.is_arbitrage
    assert result.profit == 0.0


def test_fees_can_remove_arbitrage():
    # 3 legs x fee 0.5 = 1.5 per unit > 0.9 edge
    result = find_arbitrage(market(6.8, 7.0, 3.0, 3.2), fee=0.5)
    assert not result.is_arbitrage

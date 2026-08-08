from batip.trading.candidates import (
    CandidateScanner,
    TradeCandidate,
)


def test_candidate_creation():
    scanner = CandidateScanner()

    candidate = scanner.create(
        {
            "symbol": "RELIANCE",
            "action": "TRADE",
            "direction": "Bullish",
            "score": 14,
            "confidence": 95,
            "entry": 100,
            "stop_loss": 95,
            "target_1": 110,
            "target_2": 120,
            "position_size": 20,
            "maximum_loss": 1000,
            "risk_reward_1": 2,
            "risk_reward_2": 4,
        }
    )

    assert isinstance(candidate, TradeCandidate)
    assert candidate.symbol == "RELIANCE"
    assert candidate.action == "TRADE"
    assert candidate.score == 14
    assert candidate.position_size == 20
    assert candidate.maximum_loss == 1000


def test_candidate_ranking():
    scanner = CandidateScanner()

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "score": 10,
            "confidence": 80,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "score": 14,
            "confidence": 90,
        },
        {
            "symbol": "C",
            "action": "TRADE",
            "score": 12,
            "confidence": 85,
        },
    ]

    result = scanner.scan(candidates)

    assert [candidate.symbol for candidate in result] == [
        "B",
        "C",
        "A",
    ]


def test_avoid_candidates_are_filtered():
    scanner = CandidateScanner()

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "AVOID",
            "score": 20,
        },
    ]

    result = scanner.scan(candidates)

    assert len(result) == 1
    assert result[0].symbol == "A"


def test_top_n_candidates():
    scanner = CandidateScanner()

    candidates = [
        {"symbol": "A", "action": "TRADE", "score": 10},
        {"symbol": "B", "action": "TRADE", "score": 14},
        {"symbol": "C", "action": "TRADE", "score": 12},
    ]

    result = scanner.top_n(candidates, 2)

    assert len(result) == 2
    assert result[0].symbol == "B"
    assert result[1].symbol == "C"


def test_trade_candidates_rank_above_watch():
    scanner = CandidateScanner()

    candidates = [
        {
            "symbol": "WATCH_STOCK",
            "action": "WATCH",
            "score": 20,
        },
        {
            "symbol": "TRADE_STOCK",
            "action": "TRADE",
            "score": 10,
        },
    ]

    result = scanner.scan(candidates)

    assert result[0].symbol == "TRADE_STOCK"
    assert result[1].symbol == "WATCH_STOCK"


def test_trade_candidates_only():
    scanner = CandidateScanner()

    candidates = [
        {"symbol": "A", "action": "TRADE", "score": 10},
        {"symbol": "B", "action": "WATCH", "score": 20},
        {"symbol": "C", "action": "AVOID", "score": 30},
    ]

    result = scanner.trade_candidates(candidates)

    assert len(result) == 1
    assert result[0].symbol == "A"


def test_top_n_zero_returns_empty():
    scanner = CandidateScanner()

    result = scanner.top_n(
        [{"symbol": "A", "action": "TRADE", "score": 10}],
        0,
    )

    assert result == []


def test_candidate_to_dict():
    candidate = TradeCandidate.from_mapping(
        {
            "symbol": "TEST",
            "action": "TRADE",
            "score": 14,
            "confidence": 95,
        }
    )

    result = candidate.to_dict()

    assert result["symbol"] == "TEST"
    assert result["action"] == "TRADE"
    assert result["score"] == 14
    assert result["confidence"] == 95
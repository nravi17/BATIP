from batip.trading.portfolio import PortfolioAllocator


def test_empty_candidates():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    result = allocator.allocate([])

    assert result.positions == []
    assert result.total_risk == 0
    assert result.total_capital_deployed == 0
    assert result.remaining_capital == 100000
    assert result.valid is True


def test_select_trade_candidates():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "RELIANCE",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 14,
        },
        {
            "symbol": "HDFCBANK",
            "action": "TRADE",
            "position_size": 10,
            "entry": 200,
            "maximum_loss": 1000,
            "score": 13,
        },
    ]

    result = allocator.allocate(candidates)

    assert len(result.positions) == 2
    assert result.positions[0]["symbol"] == "RELIANCE"
    assert result.positions[1]["symbol"] == "HDFCBANK"


def test_watch_candidates_not_selected():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "RELIANCE",
            "action": "WATCH",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 14,
        },
    ]

    result = allocator.allocate(candidates)

    assert result.positions == []


def test_max_positions():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=5,
        max_positions=2,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 10,
            "entry": 100,
            "maximum_loss": 500,
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "position_size": 10,
            "entry": 100,
            "maximum_loss": 500,
            "score": 9,
        },
        {
            "symbol": "C",
            "action": "TRADE",
            "position_size": 10,
            "entry": 100,
            "maximum_loss": 500,
            "score": 8,
        },
    ]

    result = allocator.allocate(candidates)

    assert len(result.positions) == 2
    assert result.positions[0]["symbol"] == "A"
    assert result.positions[1]["symbol"] == "B"


def test_max_portfolio_risk():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=2,
        max_positions=5,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 10,
            "entry": 100,
            "maximum_loss": 1500,
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "position_size": 10,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 9,
        },
    ]

    result = allocator.allocate(candidates)

    assert len(result.positions) == 1
    assert result.positions[0]["symbol"] == "A"
    assert result.total_risk == 1500


def test_capital_limit():
    allocator = PortfolioAllocator(
        capital=10000,
        max_portfolio_risk_percent=20,
        max_positions=5,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 100,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "position_size": 50,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 9,
        },
    ]

    result = allocator.allocate(candidates)

    assert len(result.positions) == 1
    assert result.positions[0]["symbol"] == "A"


def test_remaining_capital():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 10,
        },
    ]

    result = allocator.allocate(candidates)

    assert result.total_capital_deployed == 2000
    assert result.remaining_capital == 98000


def test_total_maximum_loss():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "position_size": 10,
            "entry": 200,
            "maximum_loss": 1000,
            "score": 9,
        },
    ]

    result = allocator.allocate(candidates)

    assert result.total_risk == 2000


def test_portfolio_is_valid():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=3,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 10,
        },
    ]

    result = allocator.allocate(candidates)

    assert result.valid is True


def test_risk_limit_rejects_candidate():
    allocator = PortfolioAllocator(
        capital=100000,
        max_portfolio_risk_percent=2,
        max_positions=3,
    )

    candidates = [
        {
            "symbol": "A",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1500,
            "score": 10,
        },
        {
            "symbol": "B",
            "action": "TRADE",
            "position_size": 20,
            "entry": 100,
            "maximum_loss": 1000,
            "score": 9,
        },
    ]

    result = allocator.allocate(candidates)

    assert len(result.positions) == 1
    assert result.positions[0]["symbol"] == "A"
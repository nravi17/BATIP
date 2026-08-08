from batip.trading.journal import TradeJournal


def test_record_winning_trade():
    journal = TradeJournal()

    trade = journal.record_trade(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    assert trade.symbol == "RELIANCE"
    assert trade.side == "BUY"
    assert trade.quantity == 20
    assert trade.entry_price == 100
    assert trade.exit_price == 110
    assert trade.pnl == 200
    assert trade.result == "WIN"


def test_record_losing_trade():
    journal = TradeJournal()

    trade = journal.record_trade(
        symbol="HDFCBANK",
        side="BUY",
        quantity=20,
        entry_price=100,
        exit_price=95,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="STOP_LOSS",
    )

    assert trade.pnl == -100
    assert trade.result == "LOSS"


def test_short_trade_pnl():
    journal = TradeJournal()

    trade = journal.record_trade(
        symbol="INFY",
        side="SELL",
        quantity=20,
        entry_price=100,
        exit_price=90,
        stop_loss=105,
        target_1=90,
        target_2=80,
        exit_reason="TARGET_1",
    )

    assert trade.pnl == 200
    assert trade.result == "WIN"


def test_trade_count():
    journal = TradeJournal()

    journal.record_trade(
        symbol="A",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    journal.record_trade(
        symbol="B",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=95,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="STOP_LOSS",
    )

    assert journal.trade_count == 2


def test_total_pnl():
    journal = TradeJournal()

    journal.record_trade(
        symbol="A",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    journal.record_trade(
        symbol="B",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=95,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="STOP_LOSS",
    )

    assert journal.total_pnl == 50


def test_win_rate():
    journal = TradeJournal()

    journal.record_trade(
        symbol="A",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    journal.record_trade(
        symbol="B",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=95,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="STOP_LOSS",
    )

    journal.record_trade(
        symbol="C",
        side="SELL",
        quantity=10,
        entry_price=100,
        exit_price=90,
        stop_loss=105,
        target_1=90,
        target_2=80,
        exit_reason="TARGET_1",
    )

    assert journal.win_rate == 66.67


def test_profit_factor():
    journal = TradeJournal()

    journal.record_trade(
        symbol="A",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    journal.record_trade(
        symbol="B",
        side="BUY",
        quantity=10,
        entry_price=100,
        exit_price=95,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="STOP_LOSS",
    )

    assert journal.profit_factor == 2.0


def test_empty_journal_metrics():
    journal = TradeJournal()

    assert journal.trade_count == 0
    assert journal.total_pnl == 0
    assert journal.win_rate == 0
    assert journal.profit_factor == 0


def test_get_trade_by_id():
    journal = TradeJournal()

    trade = journal.record_trade(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry_price=100,
        exit_price=110,
        stop_loss=95,
        target_1=110,
        target_2=120,
        exit_reason="TARGET_1",
    )

    result = journal.get_trade(trade.trade_id)

    assert result is trade
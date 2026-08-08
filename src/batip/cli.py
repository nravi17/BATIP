"""
BATIP Phase 2 CLI
"""

from batip.analytics.market_analyzer import MarketAnalyzer
from batip.providers.nse_provider import NSEProvider


def print_report(
    symbol: str = "BANKNIFTY",
) -> None:

    provider = NSEProvider()

    chain = provider.get_option_chain(
        symbol
    )

    analysis = MarketAnalyzer(
        chain
    ).analyze()

    print()
    print("=" * 72)
    print("                 BATIP MARKET ANALYSIS")
    print("=" * 72)

    print()
    print(
        f"Symbol              : "
        f"{analysis.symbol}"
    )

    print(
        f"Spot                : "
        f"{analysis.spot:,.2f}"
    )

    print(
        f"Expiry              : "
        f"{analysis.expiry}"
    )

    print(
        f"ATM Strike          : "
        f"{analysis.atm_strike:,.0f}"
    )

    print()
    print("-" * 72)
    print("OPTION SENTIMENT")
    print("-" * 72)

    print(
        f"PCR                 : "
        f"{analysis.pcr:.2f}"
    )

    print(
        f"PCR Signal          : "
        f"{analysis.pcr_signal}"
    )

    print(
        f"Max Pain            : "
        f"{analysis.max_pain:,.0f}"
    )

    print(
        f"Max Pain Distance   : "
        f"{analysis.max_pain_distance:+,.2f}"
    )

    print()
    print("-" * 72)
    print("SUPPORT / RESISTANCE")
    print("-" * 72)

    print(
        f"Support             : "
        f"{analysis.support:,.0f}"
    )

    print(
        f"Strong Support      : "
        f"{analysis.strong_support:,.0f}"
    )

    print(
        f"Resistance          : "
        f"{analysis.resistance:,.0f}"
    )

    print(
        f"Strong Resistance   : "
        f"{analysis.strong_resistance:,.0f}"
    )

    print()
    print("-" * 72)
    print("OI WALLS")
    print("-" * 72)

    print(
        f"Put OI Wall         : "
        f"{analysis.put_oi_wall:,.0f}"
    )

    print(
        f"Call OI Wall        : "
        f"{analysis.call_oi_wall:,.0f}"
    )

    print(
        f"Max Put ΔOI Strike  : "
        f"{analysis.put_change_oi_wall:,.0f}"
    )

    print(
        f"Max Call ΔOI Strike : "
        f"{analysis.call_change_oi_wall:,.0f}"
    )

    print()
    print("-" * 72)
    print("OI SENTIMENT")
    print("-" * 72)

    print(
        f"Bullish OI          : "
        f"{analysis.bullish_oi}"
    )

    print(
        f"Bearish OI          : "
        f"{analysis.bearish_oi}"
    )

    print(
        f"Neutral OI          : "
        f"{analysis.neutral_oi}"
    )

    print()
    print(
        f"Bullish Score       : "
        f"{analysis.bullish_score}"
    )

    print(
        f"Bearish Score       : "
        f"{analysis.bearish_score}"
    )

    print()
    print("=" * 72)

    if analysis.bias == "BULLISH":
        icon = "🟢"
    elif analysis.bias == "BEARISH":
        icon = "🔴"
    else:
        icon = "🟡"

    print(
        f"{icon} MARKET BIAS       : "
        f"{analysis.bias}"
    )

    print(
        f"   Confidence       : "
        f"{analysis.confidence:.1f}%"
    )

    print(
        f"   ACTION           : "
        f"{analysis.action}"
    )

    print("=" * 72)

    print()
    print("-" * 72)
    print("TRADE LEVELS")
    print("-" * 72)

    print(
        f"Entry               : "
        f"{analysis.entry:,.2f}"
    )

    if analysis.stop_loss:
        print(
            f"Stop Loss           : "
            f"{analysis.stop_loss:,.2f}"
        )
    else:
        print(
            "Stop Loss           : WAIT"
        )

    print(
        f"Target 1            : "
        f"{analysis.target_1:,.2f}"
    )

    print(
        f"Target 2            : "
        f"{analysis.target_2:,.2f}"
    )

    print()

    if analysis.action == "BUY":
        print(
            "🟢 TRADE VIEW: "
            "Bullish setup detected."
        )

    elif analysis.action == "SELL":
        print(
            "🔴 TRADE VIEW: "
            "Bearish setup detected."
        )

    else:
        print(
            "🟡 TRADE VIEW: "
            "No high-confidence setup."
        )

    print()
    print("=" * 72)
    print()


if __name__ == "__main__":
    print_report()
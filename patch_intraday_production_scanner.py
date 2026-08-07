from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "ui" / "app.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8-sig")

start_marker = "    def _run_intraday_scan("
end_marker = "    def _receive_intraday_results("

start = text.find(start_marker)

if start < 0:
    print("ERROR: _run_intraday_scan() not found.")
    sys.exit(2)

end = text.find(end_marker, start)

if end < 0:
    print("ERROR: _receive_intraday_results() not found.")
    sys.exit(3)

new_method = '''    def _run_intraday_scan(
        self,
        filters: Dict,
    ) -> None:
        """
        Run the shared production scanner system.

        Uses the same ScannerBootstrap singleton populated by
        DataManager from the live Upstox feed and historical
        candle pipeline.
        """

        try:

            from core.scanner.scanner_bootstrap import (
                get_scanner_system,
            )

            print(
                "[INTRADAY] Scan requested:",
                filters,
            )

            scanner_system = get_scanner_system()

            if not getattr(
                scanner_system,
                "initialized",
                False,
            ):
                scanner_system.initialize()

            status_before = scanner_system.status()

            bridge_status = status_before.get(
                "bridge",
                {},
            )

            print(
                "[PRODUCTION SCANNER] Bridge symbols:",
                bridge_status.get(
                    "symbols",
                    0,
                ),
            )

            print(
                "[PRODUCTION SCANNER] Registered scanners:",
                len(
                    status_before.get(
                        "registered_scanners",
                        [],
                    )
                ),
            )

            signals = scanner_system.scan_now()

            if signals is None:
                signals = []

            print(
                "[PRODUCTION SCANNER] Raw signals:",
                len(signals),
            )

            opportunities = []

            for signal in signals:

                signal_type = getattr(
                    signal,
                    "signal_type",
                    "",
                )

                if hasattr(signal_type, "value"):
                    signal_type = signal_type.value

                strength = getattr(
                    signal,
                    "strength",
                    "",
                )

                if hasattr(strength, "value"):
                    strength = strength.value

                indicators = getattr(
                    signal,
                    "indicators",
                    {},
                ) or {}

                metadata = getattr(
                    signal,
                    "metadata",
                    {},
                ) or {}

                entry = float(
                    getattr(
                        signal,
                        "entry",
                        0.0,
                    )
                    or 0.0
                )

                price = float(
                    getattr(
                        signal,
                        "price",
                        0.0,
                    )
                    or 0.0
                )

                if entry <= 0:
                    entry = price

                score = float(
                    getattr(
                        signal,
                        "score",
                        0.0,
                    )
                    or 0.0
                )

                confidence = float(
                    getattr(
                        signal,
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )

                if score <= 1.0 and score > 0:
                    score *= 100.0

                if confidence <= 1.0 and confidence > 0:
                    confidence *= 100.0

                rvol = (
                    indicators.get("rvol")
                    or indicators.get(
                        "relative_volume"
                    )
                    or metadata.get("rvol")
                    or metadata.get(
                        "relative_volume"
                    )
                    or 0.0
                )

                opportunity = {
                    "symbol": getattr(
                        signal,
                        "symbol",
                        "",
                    ),
                    "instrument_key": getattr(
                        signal,
                        "instrument_key",
                        "",
                    ),
                    "signal": str(
                        signal_type
                    ),
                    "signal_type": str(
                        signal_type
                    ),
                    "strength": str(
                        strength
                    ),
                    "pattern": getattr(
                        signal,
                        "pattern",
                        "",
                    ),
                    "scanner": getattr(
                        signal,
                        "scanner_name",
                        "",
                    ),
                    "scanner_name": getattr(
                        signal,
                        "scanner_name",
                        "",
                    ),
                    "timeframe": getattr(
                        signal,
                        "timeframe",
                        "",
                    ),
                    "score": score,
                    "confidence": confidence,
                    "price": price,
                    "ltp": price,
                    "entry": entry,
                    "stop_loss": float(
                        getattr(
                            signal,
                            "stop_loss",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target": float(
                        getattr(
                            signal,
                            "target1",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target1": float(
                        getattr(
                            signal,
                            "target1",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target2": float(
                        getattr(
                            signal,
                            "target2",
                            0.0,
                        )
                        or 0.0
                    ),
                    "target3": float(
                        getattr(
                            signal,
                            "target3",
                            0.0,
                        )
                        or 0.0
                    ),
                    "risk_reward": float(
                        getattr(
                            signal,
                            "risk_reward",
                            0.0,
                        )
                        or 0.0
                    ),
                    "rr": float(
                        getattr(
                            signal,
                            "risk_reward",
                            0.0,
                        )
                        or 0.0
                    ),
                    "volume": getattr(
                        signal,
                        "volume",
                        0,
                    ),
                    "average_volume": getattr(
                        signal,
                        "average_volume",
                        0,
                    ),
                    "rvol": float(
                        rvol or 0.0
                    ),
                    "indicators": indicators,
                    "metadata": metadata,
                }

                opportunities.append(
                    opportunity
                )

            minimum_score = float(
                filters.get(
                    "minimum_score",
                    0,
                )
                or 0
            )

            if minimum_score > 0:

                opportunities = [
                    item
                    for item in opportunities
                    if float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ) >= minimum_score
                ]

            direction = str(
                filters.get(
                    "direction",
                    "Both",
                )
            ).strip().lower()

            if direction not in (
                "",
                "both",
                "all",
            ):

                if direction in (
                    "buy",
                    "bullish",
                    "long",
                ):
                    allowed = {
                        "BUY",
                        "BULLISH",
                        "LONG",
                    }

                elif direction in (
                    "sell",
                    "bearish",
                    "short",
                ):
                    allowed = {
                        "SELL",
                        "BEARISH",
                        "SHORT",
                    }

                else:
                    allowed = set()

                if allowed:

                    opportunities = [
                        item
                        for item in opportunities
                        if str(
                            item.get(
                                "signal",
                                "",
                            )
                        ).upper() in allowed
                    ]

            opportunities.sort(
                key=lambda item: (
                    float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ),
                    float(
                        item.get(
                            "confidence",
                            0.0,
                        )
                        or 0.0
                    ),
                ),
                reverse=True,
            )

            print(
                "[PRODUCTION SCANNER] UI opportunities:",
                len(opportunities),
            )

            self._receive_intraday_results(
                opportunities
            )

        except Exception as exc:

            import traceback

            print(
                "[INTRADAY] Production scan failed:",
                exc,
            )

            traceback.print_exc()

            if hasattr(
                self,
                "intraday_page",
            ):

                self.intraday_page.scan_failed(
                    str(exc)
                )


'''

updated = (
    text[:start]
    + new_method
    + text[end:]
)

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_production_scanner_wiring_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)

TARGET.write_text(
    updated,
    encoding="utf-8",
)

try:

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

except Exception as exc:

    shutil.copy2(
        backup,
        TARGET,
    )

    print("=" * 72)
    print(
        "PATCH FAILED - ORIGINAL RESTORED"
    )
    print("=" * 72)
    print(exc)
    sys.exit(4)

print("=" * 72)
print(
    "STOCKVERSITY PRODUCTION INTRADAY SCANNER WIRING INSTALLED"
)
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("RUN SCANNER now uses:")
print(
    "  Shared ScannerBootstrap singleton"
)
print(
    "  -> MarketDataBridge"
)
print(
    "  -> 10 production scanners"
)
print(
    "  -> Signal objects"
)
print(
    "  -> UI opportunity dictionaries"
)
print(
    "  -> Intraday + Dashboard"
)
print()
print("Legacy scan route bypassed:")
print(
    "  NSEDataEngine -> ScannerExecutor -> OpportunityRanker"
)
print()
print("Existing Upstox/WebSocket wiring unchanged.")
print("Syntax validation: PASSED")
print("=" * 72)
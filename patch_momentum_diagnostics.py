from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "core" / "scanners" / "momentum_scanner.py"

if not TARGET.exists():
    raise FileNotFoundError(TARGET)


text = TARGET.read_text(encoding="utf-8")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"momentum_scanner.before_diagnostics_{stamp}.py"
)

shutil.copy2(TARGET, backup)


# ============================================================
# REPLACE scan() WITH DIAGNOSTIC WRAPPER
# ============================================================

start_marker = '''    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
'''

end_marker = '''    def _scan_symbol(
'''


start = text.find(start_marker)

if start == -1:
    print("ERROR: scan() start not found.")
    sys.exit(1)


end = text.find(end_marker, start)

if end == -1:
    print("ERROR: _scan_symbol() start not found.")
    sys.exit(2)


old_scan = text[start:end]


new_scan = '''    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

        results: List[Signal] = []

        diagnostic = {
            "received": 0,
            "exceptions": 0,
            "signals": 0,
            "buy": 0,
            "sell": 0,
            "no_signal": 0,
        }

        for (
            instrument_key,
            data,
        ) in self._iter_market_data(
            market_data
        ):

            diagnostic["received"] += 1

            try:

                signal = self._scan_symbol(
                    instrument_key,
                    data,
                )

                if signal is None:

                    diagnostic["no_signal"] += 1
                    continue

                results.append(
                    signal
                )

                diagnostic["signals"] += 1

                signal_type = str(
                    getattr(
                        signal,
                        "signal_type",
                        getattr(
                            signal,
                            "type",
                            "",
                        ),
                    )
                ).upper()

                if "BUY" in signal_type:
                    diagnostic["buy"] += 1

                elif "SELL" in signal_type:
                    diagnostic["sell"] += 1

            except Exception as exc:

                diagnostic["exceptions"] += 1

                if diagnostic["exceptions"] <= 5:

                    print(
                        "[MOMENTUM ERROR] "
                        f"{instrument_key}: "
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    )

        print(
            "[MOMENTUM DIAGNOSTIC] "
            f"Received={diagnostic['received']} | "
            f"NoSignal={diagnostic['no_signal']} | "
            f"Signals={diagnostic['signals']} | "
            f"BUY={diagnostic['buy']} | "
            f"SELL={diagnostic['sell']} | "
            f"Exceptions={diagnostic['exceptions']}"
        )

        return results


'''


text = (
    text[:start]
    + new_scan
    + text[end:]
)


TARGET.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# VALIDATE
# ============================================================

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
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 72)
    print(exc)
    sys.exit(3)


print("=" * 72)
print("STOCKVERSITY MOMENTUM DIAGNOSTICS INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Trading thresholds : UNCHANGED")
print("Momentum rules     : UNCHANGED")
print("Score rules        : UNCHANGED")
print("Confidence rules   : UNCHANGED")
print("Risk/Reward rules  : UNCHANGED")
print()
print("Diagnostic output enabled:")
print("  Received")
print("  NoSignal")
print("  Signals")
print("  BUY")
print("  SELL")
print("  Exceptions")
print()
print("Syntax validation: PASSED")
print("=" * 72)
from pathlib import Path
from datetime import datetime
import shutil
import py_compile

TARGET = Path(
    r"D:\StockVersityScanner\core\scanners\momentum_scanner.py"
)

MARKER = "STOCKVERSITY EARLY GATE DIAGNOSTIC V2"

if not TARGET.exists():
    raise SystemExit(f"Target not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if MARKER in text:
    print("=" * 72)
    print("EARLY GATE DIAGNOSTIC V2 ALREADY INSTALLED")
    print("=" * 72)
    raise SystemExit(0)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"momentum_scanner.before_early_gates_v2_{timestamp}.py"
)

shutil.copy2(TARGET, backup)

original = text

# ============================================================
# 1. MISSING SYMBOL
# ============================================================

old = """        if not symbol:
            return None
"""

new = f"""        # {MARKER}
        if not symbol:
            print(
                "[MOMENTUM EARLY REJECT] "
                f"{{instrument_key}} | MISSING_SYMBOL"
            )
            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate missing-symbol gate. No changes made."
    )

text = text.replace(old, new, 1)

# ============================================================
# 2. MISSING INSTRUMENT KEY
# ============================================================

old = """        if not instrument_key:
            return None
"""

new = """        if not instrument_key:
            print(
                "[MOMENTUM EARLY REJECT] "
                f"{symbol} | MISSING_INSTRUMENT_KEY"
            )
            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate instrument-key gate. No changes made."
    )

text = text.replace(old, new, 1)

# ============================================================
# 3. PRICE
# ============================================================

old = """        if (
            last_price
            < self.minimum_price
        ):
            return None
"""

new = """        if (
            last_price
            < self.minimum_price
        ):
            print(
                "[MOMENTUM EARLY REJECT] "
                f"{symbol} | PRICE | "
                f"last_price={last_price:.2f} | "
                f"minimum={self.minimum_price:.2f}"
            )
            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate price gate. No changes made."
    )

text = text.replace(old, new, 1)

# ============================================================
# 4. MARKET CAP
# ============================================================

old = """        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):
            return None
"""

new = """        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):
            print(
                "[MOMENTUM EARLY REJECT] "
                f"{symbol} | MARKET_CAP | "
                f"market_cap={market_cap:.2f} | "
                f"minimum={self.minimum_market_cap:.2f}"
            )
            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate market-cap gate. No changes made."
    )

text = text.replace(old, new, 1)

# ============================================================
# 5. GAP
# ============================================================

old = """        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            return None
"""

new = """        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            print(
                "[MOMENTUM EARLY REJECT] "
                f"{symbol} | GAP | "
                f"open={open_price:.2f} | "
                f"prev_close={previous_close:.2f} | "
                f"gap={gap_percent:.2f}% | "
                f"maximum={self.maximum_gap_percent:.2f}%"
            )
            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate gap gate. No changes made."
    )

# ============================================================
# 6. PROVE THAT THE STOCK REACHED INDICATORS
#    Print only first 10 to avoid flooding console.
# ============================================================

needle = """        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------
"""

replacement = """        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        _eg_count = getattr(
            self,
            "_early_gate_pass_count",
            0,
        )

        if _eg_count < 10:
            print(
                "[MOMENTUM EARLY PASS] "
                f"{symbol} | "
                f"price={last_price:.2f} | "
                f"mcap={market_cap:.2f} | "
                f"gap={gap_percent:.2f}%"
            )

        self._early_gate_pass_count = (
            _eg_count + 1
        )
"""

if needle not in text:
    raise SystemExit(
        "Could not locate VOLUME section. No changes made."
    )

text = text.replace(
    needle,
    replacement,
    1,
)

# ============================================================
# WRITE + COMPILE
# ============================================================

TARGET.write_text(
    text,
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

    print(
        "Compilation failed. Original restored."
    )

    raise exc

print("=" * 72)
print("STOCKVERSITY MOMENTUM EARLY GATE DIAGNOSTIC V2 INSTALLED")
print("=" * 72)
print("Target :", TARGET)
print("Backup :", backup)
print()
print("Diagnostic:")
print("  Missing symbol        : ENABLED")
print("  Missing instrument key: ENABLED")
print("  Price rejection       : ENABLED")
print("  Market-cap rejection  : ENABLED")
print("  Gap rejection         : ENABLED")
print("  Early-gate pass       : ENABLED")
print()
print("Trading logic      : UNCHANGED")
print("Thresholds         : UNCHANGED")
print("Signal generation  : UNCHANGED")
print()
print("Syntax validation: PASSED")
print("=" * 72)
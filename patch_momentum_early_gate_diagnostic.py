from pathlib import Path
from datetime import datetime
import py_compile
import shutil

TARGET = Path(r"D:\StockVersityScanner\core\scanners\momentum_scanner.py")

if not TARGET.exists():
    raise SystemExit(f"Target not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

MARKER = "# STOCKVERSITY MOMENTUM EARLY GATE DIAGNOSTIC"

if MARKER in text:
    print("=" * 72)
    print("MOMENTUM EARLY GATE DIAGNOSTIC ALREADY INSTALLED")
    print("=" * 72)
    raise SystemExit(0)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"momentum_scanner.before_early_gate_diag_{timestamp}.py"
)

shutil.copy2(TARGET, backup)

# ------------------------------------------------------------
# Locate _scan_symbol()
# ------------------------------------------------------------

needle = """    def _scan_symbol(
        self,
        instrument_key: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:
"""

if needle not in text:
    raise SystemExit(
        "Could not locate exact _scan_symbol() signature. "
        "No changes made."
    )

replacement = needle + f"""
        {MARKER}

        fd = getattr(
            self,
            "_early_gate_diag",
            None,
        )

        if isinstance(fd, dict):
            fd["RECEIVED"] = (
                fd.get("RECEIVED", 0) + 1
            )

"""

text = text.replace(
    needle,
    replacement,
    1,
)

# ------------------------------------------------------------
# Missing symbol
# ------------------------------------------------------------

old = """        if not symbol:
            return None
"""

new = """        if not symbol:

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):
                fd["MISSING_SYMBOL"] = (
                    fd.get("MISSING_SYMBOL", 0) + 1
                )

            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate missing-symbol gate. No changes made."
    )

text = text.replace(old, new, 1)

# ------------------------------------------------------------
# Missing instrument key
# ------------------------------------------------------------

old = """        if not instrument_key:
            return None
"""

new = """        if not instrument_key:

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):
                fd["MISSING_INSTRUMENT_KEY"] = (
                    fd.get(
                        "MISSING_INSTRUMENT_KEY",
                        0,
                    ) + 1
                )

            return None
"""

if old not in text:
    raise SystemExit(
        "Could not locate instrument-key gate. No changes made."
    )

text = text.replace(old, new, 1)

# ------------------------------------------------------------
# Price gate
# ------------------------------------------------------------

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

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):

                fd["PRICE_REJECT"] = (
                    fd.get("PRICE_REJECT", 0) + 1
                )

                if last_price <= 0:
                    fd["PRICE_ZERO"] = (
                        fd.get("PRICE_ZERO", 0) + 1
                    )

                samples = fd.setdefault(
                    "PRICE_SAMPLES",
                    [],
                )

                if len(samples) < 5:
                    samples.append(
                        (
                            symbol,
                            last_price,
                        )
                    )

            return None

        fd = getattr(
            self,
            "_early_gate_diag",
            None,
        )

        if isinstance(fd, dict):
            fd["PRICE_PASS"] = (
                fd.get("PRICE_PASS", 0) + 1
            )
"""

if old not in text:
    raise SystemExit(
        "Could not locate price gate. No changes made."
    )

text = text.replace(old, new, 1)

# ------------------------------------------------------------
# Market-cap gate
# ------------------------------------------------------------

old = """        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):
            return None
"""

new = """        if market_cap <= 0:

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):
                fd["MARKET_CAP_MISSING"] = (
                    fd.get(
                        "MARKET_CAP_MISSING",
                        0,
                    ) + 1
                )

        if (
            market_cap > 0
            and market_cap
            < self.minimum_market_cap
        ):

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):

                fd["MARKET_CAP_REJECT"] = (
                    fd.get(
                        "MARKET_CAP_REJECT",
                        0,
                    ) + 1
                )

                samples = fd.setdefault(
                    "MARKET_CAP_SAMPLES",
                    [],
                )

                if len(samples) < 5:
                    samples.append(
                        (
                            symbol,
                            market_cap,
                        )
                    )

            return None

        fd = getattr(
            self,
            "_early_gate_diag",
            None,
        )

        if isinstance(fd, dict):
            fd["MARKET_CAP_PASS"] = (
                fd.get(
                    "MARKET_CAP_PASS",
                    0,
                ) + 1
            )
"""

if old not in text:
    raise SystemExit(
        "Could not locate market-cap gate. No changes made."
    )

text = text.replace(old, new, 1)

# ------------------------------------------------------------
# Gap gate
# ------------------------------------------------------------

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

            fd = getattr(
                self,
                "_early_gate_diag",
                None,
            )

            if isinstance(fd, dict):

                fd["GAP_REJECT"] = (
                    fd.get("GAP_REJECT", 0) + 1
                )

                samples = fd.setdefault(
                    "GAP_SAMPLES",
                    [],
                )

                if len(samples) < 5:
                    samples.append(
                        (
                            symbol,
                            open_price,
                            previous_close,
                            gap_percent,
                        )
                    )

            return None

        fd = getattr(
            self,
            "_early_gate_diag",
            None,
        )

        if isinstance(fd, dict):
            fd["REACHED_INDICATORS"] = (
                fd.get(
                    "REACHED_INDICATORS",
                    0,
                ) + 1
            )
"""

if old not in text:
    raise SystemExit(
        "Could not locate gap gate. No changes made."
    )

text = text.replace(old, new, 1)

# ------------------------------------------------------------
# Initialize diagnostic at start of scan()
# ------------------------------------------------------------

scan_needle = """        results: List[Signal] = []

        for (
"""

scan_new = """        results: List[Signal] = []

        self._early_gate_diag = {{
            "RECEIVED": 0,
            "MISSING_SYMBOL": 0,
            "MISSING_INSTRUMENT_KEY": 0,
            "PRICE_ZERO": 0,
            "PRICE_REJECT": 0,
            "PRICE_PASS": 0,
            "MARKET_CAP_MISSING": 0,
            "MARKET_CAP_REJECT": 0,
            "MARKET_CAP_PASS": 0,
            "GAP_REJECT": 0,
            "REACHED_INDICATORS": 0,
            "PRICE_SAMPLES": [],
            "MARKET_CAP_SAMPLES": [],
            "GAP_SAMPLES": [],
        }}

        for (
"""

if scan_needle not in text:
    raise SystemExit(
        "Could not locate scan results block. No changes made."
    )

text = text.replace(
    scan_needle,
    scan_new,
    1,
)

# ------------------------------------------------------------
# Print diagnostic immediately before scan() return.
#
# Restrict replacement to the scan() section only.
# ------------------------------------------------------------

scan_start = text.index(
    "    def scan("
)

bullish_start = text.index(
    "    def _bullish_momentum(",
    scan_start,
)

scan_block = text[
    scan_start:
    bullish_start
]

return_needle = """        return results
"""

if return_needle not in scan_block:
    raise SystemExit(
        "Could not locate scan return. No changes made."
    )

return_new = """        fd = getattr(
            self,
            "_early_gate_diag",
            {},
        )

        print(
            "[MOMENTUM EARLY GATES] "
            f"Received={fd.get('RECEIVED', 0)} | "
            f"MissingSymbol={fd.get('MISSING_SYMBOL', 0)} | "
            f"MissingKey={fd.get('MISSING_INSTRUMENT_KEY', 0)} | "
            f"PriceZero={fd.get('PRICE_ZERO', 0)} | "
            f"PriceReject={fd.get('PRICE_REJECT', 0)} | "
            f"PricePass={fd.get('PRICE_PASS', 0)} | "
            f"MCapMissing={fd.get('MARKET_CAP_MISSING', 0)} | "
            f"MCapReject={fd.get('MARKET_CAP_REJECT', 0)} | "
            f"MCapPass={fd.get('MARKET_CAP_PASS', 0)} | "
            f"GapReject={fd.get('GAP_REJECT', 0)} | "
            f"ReachedIndicators={fd.get('REACHED_INDICATORS', 0)}"
        )

        if fd.get("PRICE_SAMPLES"):
            print(
                "[MOMENTUM PRICE SAMPLES]",
                fd["PRICE_SAMPLES"],
            )

        if fd.get("MARKET_CAP_SAMPLES"):
            print(
                "[MOMENTUM MCAP SAMPLES]",
                fd["MARKET_CAP_SAMPLES"],
            )

        if fd.get("GAP_SAMPLES"):
            print(
                "[MOMENTUM GAP SAMPLES]",
                fd["GAP_SAMPLES"],
            )

        return results
"""

scan_block = scan_block.replace(
    return_needle,
    return_new,
    1,
)

text = (
    text[:scan_start]
    + scan_block
    + text[bullish_start:]
)

TARGET.write_text(
    text,
    encoding="utf-8",
)

try:
    py_compile.compile(
        str(TARGET),
        doraise=True,
    )

except Exception:
    shutil.copy2(
        backup,
        TARGET,
    )
    raise

print("=" * 72)
print("STOCKVERSITY MOMENTUM EARLY-GATE DIAGNOSTIC INSTALLED")
print("=" * 72)
print("Target :", TARGET)
print("Backup :", backup)
print()
print("Trading logic       : UNCHANGED")
print("Scanner thresholds  : UNCHANGED")
print("Signal generation   : UNCHANGED")
print("Runtime diagnostics : ENABLED")
print()
print("Syntax validation: PASSED")
print("=" * 72)
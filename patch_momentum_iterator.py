from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys


ROOT = Path(__file__).resolve().parent

TARGET = (
    ROOT
    / "core"
    / "scanners"
    / "momentum_scanner.py"
)


if not TARGET.exists():

    print(
        f"ERROR: Target not found: {TARGET}"
    )

    sys.exit(1)


text = TARGET.read_text(
    encoding="utf-8"
)


# ============================================================
# ALREADY INSTALLED?
# ============================================================

if "def _iter_market_data(" in text:

    print("=" * 72)
    print(
        "MOMENTUM _iter_market_data ALREADY EXISTS"
    )
    print("=" * 72)

    sys.exit(0)


# ============================================================
# BACKUP
# ============================================================

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "momentum_scanner.before_iterator_fix_"
    f"{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


# ============================================================
# INSERT BEFORE scan()
# ============================================================

marker = '''    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
'''


if marker not in text:

    print("=" * 72)
    print("PATCH NOT APPLIED")
    print("=" * 72)
    print(
        "Could not locate MomentumScanner.scan()."
    )
    print(
        "Original file has NOT been changed."
    )

    sys.exit(2)


method = '''    def _iter_market_data(
        self,
        market_data: Dict[str, Any],
    ) -> Iterable[
        Tuple[str, Dict[str, Any]]
    ]:
        """
        Normalize common StockVersity market-data
        container formats.
        """

        if not isinstance(
            market_data,
            dict,
        ):
            return

        # ---------------------------------------------
        # FORMAT:
        # {"symbols": {...}}
        # ---------------------------------------------

        symbols = market_data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            dict,
        ):

            for key, value in symbols.items():

                if isinstance(
                    value,
                    dict,
                ):

                    instrument_key = str(
                        _get(
                            value,
                            "instrument_key",
                            default=key,
                        )
                    )

                    yield (
                        instrument_key,
                        value,
                    )

            return

        # ---------------------------------------------
        # FORMAT:
        # {"data": {...}}
        # ---------------------------------------------

        data_block = market_data.get(
            "data"
        )

        if isinstance(
            data_block,
            dict,
        ):

            for key, value in data_block.items():

                if isinstance(
                    value,
                    dict,
                ):

                    instrument_key = str(
                        _get(
                            value,
                            "instrument_key",
                            default=key,
                        )
                    )

                    yield (
                        instrument_key,
                        value,
                    )

            return

        # ---------------------------------------------
        # DIRECT FORMAT
        # ---------------------------------------------

        for key, value in market_data.items():

            if not isinstance(
                value,
                dict,
            ):
                continue

            instrument_key = str(
                _get(
                    value,
                    "instrument_key",
                    default=key,
                )
            )

            yield (
                instrument_key,
                value,
            )


'''


updated = text.replace(
    marker,
    method + marker,
    1,
)


TARGET.write_text(
    updated,
    encoding="utf-8",
)


# ============================================================
# COMPILE VALIDATION
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
    print(
        "PATCH FAILED - ORIGINAL RESTORED"
    )
    print("=" * 72)
    print(exc)

    sys.exit(3)


# ============================================================
# SUCCESS
# ============================================================

print("=" * 72)
print(
    "STOCKVERSITY MOMENTUM ITERATOR FIX INSTALLED"
)
print("=" * 72)

print(
    f"Target : {TARGET}"
)

print(
    f"Backup : {backup}"
)

print()

print(
    "Added:"
)

print(
    "  MomentumScanner._iter_market_data()"
)

print()

print(
    "Supported market-data formats:"
)

print(
    '  {"symbols": {...}}'
)

print(
    '  {"data": {...}}'
)

print(
    "  direct instrument dictionary"
)

print()

print(
    "Implementation source : ORBScanner proven iterator"
)

print()

print(
    "Momentum rules        : UNCHANGED"
)

print(
    "Indicators            : UNCHANGED"
)

print(
    "Score thresholds      : UNCHANGED"
)

print(
    "Risk/Reward           : UNCHANGED"
)

print(
    "Scanner engine        : UNCHANGED"
)

print()

print(
    "Syntax validation: PASSED"
)

print("=" * 72)
# STOCKVERSITY_PATCH_VERSION = "UI_SIGNAL_INDICATOR_BRIDGE_V3"

from pathlib import Path
from datetime import datetime
import shutil
import py_compile


TARGET = Path(
    r"D:\StockVersityScanner\ui\app.py"
)


# ============================================================
# BASIC SAFETY
# ============================================================

if not TARGET.exists():

    raise FileNotFoundError(
        f"Target not found: {TARGET}"
    )


original = TARGET.read_text(
    encoding="utf-8"
)

text = original


print("=" * 72)
print("STOCKVERSITY PATCH V3")
print("UI SIGNAL INDICATOR BRIDGE")
print("=" * 72)


# ============================================================
# ALREADY INSTALLED CHECK
# ============================================================

MARKER = (
    "STOCKVERSITY UI SIGNAL "
    "INDICATOR BRIDGE V3"
)

if MARKER in text:

    raise RuntimeError(
        "V3 indicator bridge is already "
        "installed in ui/app.py. "
        "No changes made."
    )


# ============================================================
# LOCATE ACTIVE SIGNAL CONVERSION AREA
# ============================================================

opportunity_anchor = (
    '                opportunity = {'
)

opportunity_pos = text.find(
    opportunity_anchor
)

if opportunity_pos == -1:

    raise RuntimeError(
        "Could not locate opportunity dictionary. "
        "No changes made."
    )


# Search backwards from opportunity dictionary for the
# active RVOL assignment.

rvol_pos = text.rfind(
    "                rvol = (",
    0,
    opportunity_pos,
)

if rvol_pos == -1:

    raise RuntimeError(
        "Could not locate active RVOL assignment "
        "before opportunity dictionary. "
        "No changes made."
    )


# ============================================================
# FIND END OF CURRENT RVOL BLOCK
# ============================================================

#
# The confirmed block ends immediately before:
#
#     opportunity = {
#
# Therefore we can replace everything from the active
# "rvol = (" up to opportunity dictionary.
#
# This is safer than depending on exact whitespace inside
# the old RVOL expression.
#

between = text[
    rvol_pos:opportunity_pos
]

if (
    'indicators.get("rvol")'
    not in between
):

    raise RuntimeError(
        "Located RVOL assignment does not look "
        "like the expected signal conversion block. "
        "No changes made."
    )


if (
    'metadata.get("rvol")'
    not in between
):

    raise RuntimeError(
        "Located RVOL assignment is missing "
        "expected metadata RVOL lookup. "
        "No changes made."
    )


# ============================================================
# NEW INDICATOR RESOLUTION BLOCK
# ============================================================

new_indicator_block = '''                # =================================================
                # STOCKVERSITY UI SIGNAL INDICATOR BRIDGE V3
                # =================================================
                #
                # Resolve scanner indicator values from:
                #
                #   1. signal.indicators
                #   2. signal.metadata
                #   3. direct Signal attributes
                #
                # This does NOT alter scanner qualification,
                # scoring, filtering or trading logic.
                # =================================================

                def _ui_signal_value(
                    *names,
                    default=0.0,
                ):

                    for name in names:

                        value = indicators.get(
                            name
                        )

                        if (
                            value is not None
                            and value != ""
                        ):
                            return value

                        value = metadata.get(
                            name
                        )

                        if (
                            value is not None
                            and value != ""
                        ):
                            return value

                        value = getattr(
                            signal,
                            name,
                            None,
                        )

                        if (
                            value is not None
                            and value != ""
                        ):
                            return value

                    return default


                rvol = _ui_signal_value(
                    "rvol",
                    "relative_volume",
                    "volume_ratio",
                )


                ema9 = _ui_signal_value(
                    "ema9"
                )

                ema20 = _ui_signal_value(
                    "ema20"
                )

                ema21 = _ui_signal_value(
                    "ema21"
                )

                ema50 = _ui_signal_value(
                    "ema50"
                )

                ema100 = _ui_signal_value(
                    "ema100"
                )

                ema200 = _ui_signal_value(
                    "ema200"
                )


                rsi = _ui_signal_value(
                    "rsi"
                )


                macd = _ui_signal_value(
                    "macd"
                )

                macd_signal = _ui_signal_value(
                    "macd_signal"
                )

                macd_histogram = (
                    _ui_signal_value(
                        "macd_histogram",
                        "macd_hist",
                    )
                )


                adx = _ui_signal_value(
                    "adx"
                )

                plus_di = _ui_signal_value(
                    "plus_di",
                    "di_plus",
                )

                minus_di = _ui_signal_value(
                    "minus_di",
                    "di_minus",
                )


                atr = _ui_signal_value(
                    "atr"
                )

                vwap = _ui_signal_value(
                    "vwap"
                )

                volume_sma20 = (
                    _ui_signal_value(
                        "volume_sma20"
                    )
                )


'''

text = (
    text[:rvol_pos]
    + new_indicator_block
    + text[opportunity_pos:]
)


print(
    "[PATCH V3] Indicator resolver prepared."
)


# ============================================================
# LOCATE OPPORTUNITY RVOL FIELD
# ============================================================

opportunity_pos = text.find(
    opportunity_anchor
)

if opportunity_pos == -1:

    raise RuntimeError(
        "Opportunity dictionary disappeared "
        "during patch preparation. "
        "No changes made."
    )


rvol_field_anchor = '''                    "rvol": float(
                        rvol or 0.0
                    ),
'''

rvol_field_pos = text.find(
    rvol_field_anchor,
    opportunity_pos,
)

if rvol_field_pos == -1:

    raise RuntimeError(
        "Could not locate RVOL field inside "
        "opportunity dictionary. "
        "No changes made."
    )


# ============================================================
# REPLACEMENT OPPORTUNITY FIELDS
# ============================================================

new_opportunity_fields = '''                    # -----------------------------------------
                    # Scanner indicators exposed directly to UI
                    # -----------------------------------------

                    "rvol": float(
                        rvol or 0.0
                    ),

                    "relative_volume": float(
                        rvol or 0.0
                    ),

                    "volume_ratio": float(
                        rvol or 0.0
                    ),

                    "ema9": float(
                        ema9 or 0.0
                    ),

                    "ema20": float(
                        ema20 or 0.0
                    ),

                    "ema21": float(
                        ema21 or 0.0
                    ),

                    "ema50": float(
                        ema50 or 0.0
                    ),

                    "ema100": float(
                        ema100 or 0.0
                    ),

                    "ema200": float(
                        ema200 or 0.0
                    ),

                    "rsi": float(
                        rsi or 0.0
                    ),

                    "macd": float(
                        macd or 0.0
                    ),

                    "macd_signal": float(
                        macd_signal or 0.0
                    ),

                    "macd_histogram": float(
                        macd_histogram or 0.0
                    ),

                    "adx": float(
                        adx or 0.0
                    ),

                    "plus_di": float(
                        plus_di or 0.0
                    ),

                    "minus_di": float(
                        minus_di or 0.0
                    ),

                    "atr": float(
                        atr or 0.0
                    ),

                    "vwap": float(
                        vwap or 0.0
                    ),

                    "volume_sma20": float(
                        volume_sma20 or 0.0
                    ),
'''

text = (
    text[:rvol_field_pos]
    + new_opportunity_fields
    + text[
        rvol_field_pos
        + len(rvol_field_anchor):
    ]
)


print(
    "[PATCH V3] Opportunity fields prepared."
)


# ============================================================
# PRE-WRITE VALIDATION
# ============================================================

required_items = [

    MARKER,

    "def _ui_signal_value(",

    '"relative_volume": float(',

    '"volume_ratio": float(',

    '"ema9": float(',

    '"ema20": float(',

    '"ema50": float(',

    '"ema200": float(',

    '"rsi": float(',

    '"macd": float(',

    '"macd_signal": float(',

    '"macd_histogram": float(',

    '"adx": float(',

    '"plus_di": float(',

    '"minus_di": float(',

    '"atr": float(',

    '"vwap": float(',

    '"volume_sma20": float(',
]


missing = [

    item
    for item in required_items
    if item not in text
]


if missing:

    raise RuntimeError(
        "Patch preparation validation failed. "
        "Missing: "
        + ", ".join(missing)
        + ". No changes made."
    )


# ============================================================
# MAKE SURE WE DID NOT REMOVE SCORE MODEL
# ============================================================

critical_existing_items = [

    '"raw_score": raw_score',

    '"rank_score": rank_score',

    '"confidence": confidence',

    '"score": score',

    'opportunities.append(',
]


missing_critical = [

    item
    for item in critical_existing_items
    if item not in text
]


if missing_critical:

    raise RuntimeError(
        "Safety check failed. Existing scanner/UI "
        "conversion elements appear missing: "
        + ", ".join(missing_critical)
        + ". No changes made."
    )


# ============================================================
# CREATE TIMESTAMPED BACKUP
# ============================================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    "app.before_ui_indicator_bridge_v3_"
    f"{timestamp}.py"
)


shutil.copy2(
    TARGET,
    backup,
)


print(
    f"[PATCH V3] Backup created: {backup}"
)


# ============================================================
# WRITE PATCH
# ============================================================

try:

    TARGET.write_text(
        text,
        encoding="utf-8",
    )


    # --------------------------------------------------------
    # PYTHON SYNTAX CHECK
    # --------------------------------------------------------

    py_compile.compile(
        str(TARGET),
        doraise=True,
    )


except Exception as exc:

    print()
    print(
        "[PATCH V3] VALIDATION FAILED."
    )

    print(
        "[PATCH V3] Restoring original file..."
    )

    shutil.copy2(
        backup,
        TARGET,
    )

    print(
        "[PATCH V3] Original ui/app.py restored."
    )

    raise RuntimeError(
        "Patch failed Python validation. "
        f"Original restored. Error: {exc}"
    )


# ============================================================
# POST-WRITE VERIFY
# ============================================================

written = TARGET.read_text(
    encoding="utf-8"
)


for item in required_items:

    if item not in written:

        shutil.copy2(
            backup,
            TARGET,
        )

        raise RuntimeError(
            "Post-write verification failed. "
            "Original ui/app.py restored."
        )


# ============================================================
# SUCCESS
# ============================================================

print()
print("=" * 72)
print("PATCH V3 INSTALLED SUCCESSFULLY")
print("=" * 72)

print(
    f"Target : {TARGET}"
)

print(
    f"Backup : {backup}"
)

print()

print(
    "Signal indicator bridge:"
)

print(
    "  RVOL / Volume Ratio     : ADDED"
)

print(
    "  EMA 9/20/21/50/100/200 : ADDED"
)

print(
    "  RSI                     : ADDED"
)

print(
    "  MACD                    : ADDED"
)

print(
    "  MACD Signal             : ADDED"
)

print(
    "  MACD Histogram          : ADDED"
)

print(
    "  ADX / DI+ / DI-         : ADDED"
)

print(
    "  ATR                     : ADDED"
)

print(
    "  VWAP                    : ADDED"
)

print(
    "  Volume SMA20            : ADDED"
)

print()

print(
    "Scanner qualification : UNCHANGED"
)

print(
    "Minimum score         : UNCHANGED"
)

print(
    "Confidence logic      : UNCHANGED"
)

print(
    "Ranking model         : UNCHANGED"
)

print(
    "Trading logic         : UNCHANGED"
)

print()

print(
    "Python syntax         : PASSED"
)

print("=" * 72)
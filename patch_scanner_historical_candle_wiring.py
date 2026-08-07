from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "data_manager.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8")

helper_marker = "    def _forward_history_to_scanner("
call_marker = "        self._forward_history_to_scanner("

get_section = """    # =====================================================
    # GET DATAFRAME
    # =====================================================
"""

helper = '''    # =====================================================
    # FORWARD HISTORICAL DATA TO SHARED SCANNER
    # =====================================================

    def _forward_history_to_scanner(
        self,
        instrument_key: str,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:
        """Forward an existing OHLCV DataFrame to the shared scanner."""

        try:
            if dataframe is None or dataframe.empty:
                return

            scanner_system = get_scanner_system()

            if not getattr(scanner_system, "initialized", False):
                scanner_system.initialize()

            records = []

            for index, row in dataframe.iterrows():
                timestamp = row.get("timestamp", row.get("time", row.get("datetime", index)))
                records.append({
                    "timestamp": timestamp,
                    "open": row.get("open", row.get("Open", 0.0)),
                    "high": row.get("high", row.get("High", 0.0)),
                    "low": row.get("low", row.get("Low", 0.0)),
                    "close": row.get("close", row.get("Close", 0.0)),
                    "volume": row.get("volume", row.get("Volume", 0)),
                })

            if not records:
                return

            scanner_system.add_candles(
                instrument_key,
                timeframe,
                records,
                max_candles=500,
            )

        except Exception:
            self.logger.exception(
                "Scanner historical candle forwarding failed."
            )

'''

if helper_marker not in text:
    if get_section not in text:
        print("ERROR: Could not locate GET DATAFRAME section.")
        sys.exit(2)
    text = text.replace(get_section, helper + get_section, 1)

if call_marker not in text:
    anchor = """            ] = datetime.now()

    # =====================================================
    # FORWARD HISTORICAL DATA TO SHARED SCANNER
"""
    replacement = """            ] = datetime.now()

        self._forward_history_to_scanner(
            instrument_key,
            timeframe,
            dataframe,
        )

    # =====================================================
    # FORWARD HISTORICAL DATA TO SHARED SCANNER
"""
    if anchor not in text:
        print("ERROR: Could not locate set_data insertion point.")
        sys.exit(3)
    text = text.replace(anchor, replacement, 1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(f"data_manager.before_scanner_history_wiring_{stamp}.py")
shutil.copy2(TARGET, backup)
TARGET.write_text(text, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    print("=" * 68)
    print("SCANNER HISTORY PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(4)

print("=" * 68)
print("STOCKVERSITY SCANNER HISTORICAL CANDLE WIRING INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Connected: DataManager.set_data -> ScannerBootstrap.add_candles -> MarketDataBridge")
print("No second websocket or duplicate historical API request created.")
print("Maximum scanner candle history per timeframe: 500")
print("Syntax validation: PASSED")
print("=" * 68)

from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
TARGET = ROOT / "core" / "upstox_client.py"

if not TARGET.exists():
    print(f"ERROR: Target not found: {TARGET}")
    sys.exit(1)

text = TARGET.read_text(encoding="utf-8-sig")

old = '''        response = self._request_retry(

            self.history_api.get_historical_candle_data1,

            instrument_key,

            "days",

            "1",

            to_date,

            from_date,

        )
'''

new = '''        # ----------------------------------------------------------
        # Upstox History V3 timeframe normalization
        # ----------------------------------------------------------
        # V3 expects:
        #   instrument_key, unit, interval, to_date, from_date
        #
        # Supported units:
        #   minutes 1-300
        #   hours   1-5
        #   days    1
        #   weeks   1
        #   months  1

        raw_interval = str(interval).strip()
        normalized = raw_interval.lower()

        aliases = {
            "day": ("days", "1"),
            "1d": ("days", "1"),
            "d": ("days", "1"),

            "week": ("weeks", "1"),
            "1w": ("weeks", "1"),
            "w": ("weeks", "1"),

            "month": ("months", "1"),
            "1mo": ("months", "1"),
            "1mth": ("months", "1"),
        }

        if normalized in aliases:
            unit, v3_interval = aliases[normalized]

        elif normalized.endswith("m") and normalized[:-1].isdigit():
            minutes = int(normalized[:-1])

            if not 1 <= minutes <= 300:
                raise ValueError(
                    f"Unsupported Upstox minute timeframe: {raw_interval}"
                )

            unit = "minutes"
            v3_interval = str(minutes)

        elif normalized.endswith("h") and normalized[:-1].isdigit():
            hours = int(normalized[:-1])

            if not 1 <= hours <= 5:
                raise ValueError(
                    f"Unsupported Upstox hour timeframe: {raw_interval}"
                )

            unit = "hours"
            v3_interval = str(hours)

        else:
            raise ValueError(
                f"Unsupported historical timeframe: {raw_interval}"
            )

        response = self._request_retry(

            self.history_api.get_historical_candle_data1,

            instrument_key,

            unit,

            v3_interval,

            to_date,

            from_date,

        )
'''

if old not in text:
    print("=" * 68)
    print("PATCH NOT APPLIED")
    print("=" * 68)
    print("Expected temporary daily-history block was not found.")
    print("No changes made.")
    sys.exit(2)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"upstox_client.before_v3_timeframe_fix_{stamp}.py"
)

shutil.copy2(TARGET, backup)

updated = text.replace(old, new, 1)

TARGET.write_text(updated, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)

except Exception as exc:
    shutil.copy2(backup, TARGET)

    print("=" * 68)
    print("PATCH FAILED - ORIGINAL RESTORED")
    print("=" * 68)
    print(f"Reason: {exc}")
    sys.exit(3)

print("=" * 68)
print("STOCKVERSITY UPSTOX V3 TIMEFRAME NORMALIZATION INSTALLED")
print("=" * 68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Supported mappings:")
print("  1m-300m -> minutes")
print("  1h-5h   -> hours")
print("  day/1d  -> days/1")
print("  week/1w -> weeks/1")
print("  month/1mo -> months/1")
print()
print("Syntax validation: PASSED")
print("=" * 68)
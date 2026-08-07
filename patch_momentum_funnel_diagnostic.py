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

if "[MOMENTUM FUNNEL]" in text:
    print("MOMENTUM FUNNEL DIAGNOSTIC ALREADY INSTALLED")
    sys.exit(0)

marker = '''        bullish = self._bullish_momentum(
'''

if marker not in text:
    print("ERROR: bullish call marker not found.")
    sys.exit(1)


diagnostic = '''        # =================================================
        # MOMENTUM FUNNEL DIAGNOSTIC - READ ONLY
        # =================================================

        short_ema_diag = (
            ema20 if ema20 > 0 else ema21
        )

        bull_fail = []
        bear_fail = []

        # ---------------- BULL ----------------

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio < self.minimum_rvol
        ):
            bull_fail.append("RVOL")

        if (
            self.require_vwap
            and vwap > 0
            and last_price <= vwap
        ):
            bull_fail.append("VWAP")

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            bull_fail.append("ADX")

        if (
            plus_di > 0
            and minus_di > 0
            and plus_di <= minus_di
        ):
            bull_fail.append("DI")

        if rsi > 0 and rsi < 52:
            bull_fail.append("RSI_LOW")

        if rsi > 85:
            bull_fail.append("RSI_HIGH")

        if self.require_ema_alignment:

            if ema9 > 0 and last_price < ema9:
                bull_fail.append("EMA9")

            if (
                short_ema_diag > 0
                and last_price < short_ema_diag
            ):
                bull_fail.append("EMA_SHORT")

            if (
                short_ema_diag > 0
                and ema50 > 0
                and short_ema_diag < ema50
            ):
                bull_fail.append("EMA50")

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 < ema200
            ):
                bull_fail.append("EMA200")

        if (
            (macd != 0 or macd_signal != 0)
            and macd <= macd_signal
        ):
            bull_fail.append("MACD")

        if (
            macd_histogram != 0
            and macd_histogram < 0
        ):
            bull_fail.append("MACD_HIST")

        # ---------------- BEAR ----------------

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio < self.minimum_rvol
        ):
            bear_fail.append("RVOL")

        if (
            self.require_vwap
            and vwap > 0
            and last_price >= vwap
        ):
            bear_fail.append("VWAP")

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            bear_fail.append("ADX")

        if (
            plus_di > 0
            and minus_di > 0
            and minus_di <= plus_di
        ):
            bear_fail.append("DI")

        if rsi > 0 and rsi > 48:
            bear_fail.append("RSI_HIGH")

        if rsi > 0 and rsi < 15:
            bear_fail.append("RSI_LOW")

        if self.require_ema_alignment:

            if ema9 > 0 and last_price > ema9:
                bear_fail.append("EMA9")

            if (
                short_ema_diag > 0
                and last_price > short_ema_diag
            ):
                bear_fail.append("EMA_SHORT")

            if (
                short_ema_diag > 0
                and ema50 > 0
                and short_ema_diag > ema50
            ):
                bear_fail.append("EMA50")

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 > ema200
            ):
                bear_fail.append("EMA200")

        if (
            (macd != 0 or macd_signal != 0)
            and macd >= macd_signal
        ):
            bear_fail.append("MACD")

        if (
            macd_histogram != 0
            and macd_histogram > 0
        ):
            bear_fail.append("MACD_HIST")

        # Store counters on scanner instance.
        if not hasattr(self, "_funnel_diag"):
            self._funnel_diag = {
                "TOTAL": 0,
                "BULL_PASS": 0,
                "BEAR_PASS": 0,
                "BULL_FAIL": {},
                "BEAR_FAIL": {},
            }

        fd = self._funnel_diag
        fd["TOTAL"] += 1

        if not bull_fail:
            fd["BULL_PASS"] += 1

        if not bear_fail:
            fd["BEAR_PASS"] += 1

        for reason in bull_fail:
            fd["BULL_FAIL"][reason] = (
                fd["BULL_FAIL"].get(reason, 0) + 1
            )

        for reason in bear_fail:
            fd["BEAR_FAIL"][reason] = (
                fd["BEAR_FAIL"].get(reason, 0) + 1
            )

'''


text = text.replace(
    marker,
    diagnostic + marker,
    1,
)


# Print funnel at end of scan, immediately before existing diagnostic.
print_marker = '''        print(
            "[MOMENTUM DIAGNOSTIC] "
'''

if print_marker not in text:
    print("ERROR: existing MOMENTUM DIAGNOSTIC not found.")
    sys.exit(2)


print_block = '''        fd = getattr(self, "_funnel_diag", {})

        if fd:
            print(
                "[MOMENTUM FUNNEL] "
                f"Total={fd.get('TOTAL', 0)} | "
                f"BullPass={fd.get('BULL_PASS', 0)} | "
                f"BearPass={fd.get('BEAR_PASS', 0)}"
            )

            print(
                "[MOMENTUM BULL FAIL] "
                + " | ".join(
                    f"{k}={v}"
                    for k, v in sorted(
                        fd.get("BULL_FAIL", {}).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                )
            )

            print(
                "[MOMENTUM BEAR FAIL] "
                + " | ".join(
                    f"{k}={v}"
                    for k, v in sorted(
                        fd.get("BEAR_FAIL", {}).items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                )
            )

'''


text = text.replace(
    print_marker,
    print_block + print_marker,
    1,
)


stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = TARGET.with_name(
    f"momentum_scanner.before_funnel_{stamp}.py"
)

shutil.copy2(TARGET, backup)

TARGET.write_text(text, encoding="utf-8")


try:
    py_compile.compile(str(TARGET), doraise=True)

except Exception as exc:

    shutil.copy2(backup, TARGET)

    print("PATCH FAILED - ORIGINAL RESTORED")
    print(exc)
    sys.exit(3)


print("=" * 72)
print("STOCKVERSITY MOMENTUM FUNNEL DIAGNOSTIC INSTALLED")
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print("Trading logic     : UNCHANGED")
print("Thresholds        : UNCHANGED")
print("Signal generation : UNCHANGED")
print("Diagnostic only   : ENABLED")
print()
print("Syntax validation: PASSED")
print("=" * 72)
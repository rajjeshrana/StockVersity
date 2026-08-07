from pathlib import Path
import inspect

from core.scanner.market_data_bridge import MarketDataBridge

print("=" * 80)
print("STOCKVERSITY BRIDGE / SYMBOL SCHEMA DIAGNOSTIC")
print("=" * 80)

print("\n=== MarketDataBridge.update_quote ===")
try:
    print(inspect.getsource(MarketDataBridge.update_quote))
except Exception as exc:
    print("Could not inspect update_quote:", repr(exc))

print("\n=== MarketDataBridge.normalize_quote ===")
try:
    print(inspect.getsource(MarketDataBridge.normalize_quote))
except Exception as exc:
    print("Could not inspect normalize_quote:", repr(exc))

print("\n=== MarketDataBridge.add_candle ===")
try:
    print(inspect.getsource(MarketDataBridge.add_candle))
except Exception as exc:
    print("Could not inspect add_candle:", repr(exc))

print("\n=== MarketDataBridge.add_candles ===")
try:
    print(inspect.getsource(MarketDataBridge.add_candles))
except Exception as exc:
    print("Could not inspect add_candles:", repr(exc))

print("\n=== SOURCE SEARCH: symbol assignment / bridge writes ===")

root = Path(r"D:\StockVersityScanner")

patterns = (
    '"symbol"',
    "'symbol'",
    '"trading_symbol"',
    "'trading_symbol'",
    '"tradingsymbol"',
    "'tradingsymbol'",
    "update_quote(",
    "add_candle(",
    "add_candles(",
)

for path in root.rglob("*.py"):

    path_text = str(path).lower()

    if (
        "__pycache__" in path_text
        or "before_" in path_text
        or "backup" in path_text
        or "patch_" in path_text
    ):
        continue

    try:
        lines = path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()
    except Exception:
        continue

    matches = []

    for lineno, line in enumerate(lines, 1):

        if any(
            pattern in line
            for pattern in patterns
        ):
            matches.append(
                (lineno, line.strip())
            )

    if matches:

        print(f"\nFILE: {path}")

        for lineno, line in matches[:40]:
            print(
                f"  {lineno:5}: {line}"
            )

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)

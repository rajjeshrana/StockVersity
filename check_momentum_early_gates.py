from collections import Counter

from core.scanner.scanner_bootstrap import get_scanner_system


def f(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


system = get_scanner_system()
system.initialize()

manager = system.manager
engine = manager.engine

scanner = engine.scanners.get("MomentumScanner")

if scanner is None:
    raise RuntimeError("MomentumScanner not found")


print("=" * 80)
print("MOMENTUM EARLY-GATE RUNTIME DIAGNOSTIC")
print("=" * 80)

print("minimum_price      :", scanner.minimum_price)
print("minimum_market_cap :", scanner.minimum_market_cap)
print("maximum_gap_percent:", scanner.maximum_gap_percent)
print()

# ------------------------------------------------------------
# GET LIVE BRIDGE
# ------------------------------------------------------------

bridge = getattr(system, "bridge", None)

if bridge is None:
    bridge = getattr(system, "market_data_bridge", None)

if bridge is None:
    print("ERROR: scanner system has no bridge attribute.")
    print("SYSTEM ATTRIBUTES:")
    print([x for x in dir(system) if not x.startswith("_")])
    raise SystemExit(1)


# Try common bridge storage attributes.
market_data = None

for attr in (
    "market_data",
    "data",
    "quotes",
    "symbols",
    "_market_data",
    "_data",
    "_quotes",
    "_symbols",
):

    value = getattr(bridge, attr, None)

    if isinstance(value, dict) and value:
        market_data = value
        print("Bridge storage :", attr)
        break


# Some bridge implementations expose a snapshot method.
if market_data is None:

    for method_name in (
        "snapshot",
        "get_market_data",
        "get_all",
    ):

        method = getattr(bridge, method_name, None)

        if callable(method):
            try:
                value = method()

                if isinstance(value, dict) and value:
                    market_data = value
                    print("Bridge source  :", method_name + "()")
                    break

            except Exception:
                pass


if market_data is None:
    print()
    print("Could not locate populated bridge market-data storage.")
    print()
    print("BRIDGE TYPE:", type(bridge))
    print("BRIDGE ATTRIBUTES:")
    print([x for x in dir(bridge) if not x.startswith("__")])
    raise SystemExit(1)


# Normalize {"symbols": {...}} / {"data": {...}} if needed.
if (
    isinstance(market_data.get("symbols"), dict)
    and market_data.get("symbols")
):
    market_data = market_data["symbols"]

elif (
    isinstance(market_data.get("data"), dict)
    and market_data.get("data")
):
    market_data = market_data["data"]


print("Records        :", len(market_data))
print()


counts = Counter()

samples = {
    "missing_symbol": [],
    "price": [],
    "market_cap": [],
    "gap": [],
    "passed": [],
}


for key, data in market_data.items():

    if not isinstance(data, dict):
        counts["not_dict"] += 1
        continue

    counts["received"] += 1

    symbol = str(
        data.get("symbol")
        or data.get("trading_symbol")
        or data.get("tradingsymbol")
        or ""
    ).upper().strip()

    instrument_key = str(
        data.get("instrument_key")
        or key
        or ""
    ).strip()

    # --------------------------------------------------------
    # SYMBOL
    # --------------------------------------------------------

    if not symbol:

        counts["missing_symbol"] += 1

        if len(samples["missing_symbol"]) < 10:
            samples["missing_symbol"].append(
                (
                    key,
                    list(data.keys())[:30],
                )
            )

        continue

    if not instrument_key:
        counts["missing_instrument_key"] += 1
        continue

    counts["has_symbol"] += 1

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    last_price = f(
        data.get("last_price")
        if data.get("last_price") is not None
        else data.get("ltp")
        if data.get("ltp") is not None
        else data.get("close")
        if data.get("close") is not None
        else data.get("close_price")
    )

    if last_price <= 0:
        counts["price_zero"] += 1

    if last_price < scanner.minimum_price:

        counts["price_reject"] += 1

        if len(samples["price"]) < 10:
            samples["price"].append(
                (
                    symbol,
                    last_price,
                    data.get("last_price"),
                    data.get("ltp"),
                    data.get("close"),
                    data.get("close_price"),
                )
            )

        continue

    counts["price_pass"] += 1

    # --------------------------------------------------------
    # MARKET CAP
    # --------------------------------------------------------

    market_cap = f(
        data.get("market_cap")
        if data.get("market_cap") is not None
        else data.get("market_cap_cr")
    )

    if market_cap <= 0:
        counts["market_cap_missing"] += 1

    if (
        market_cap > 0
        and market_cap < scanner.minimum_market_cap
    ):

        counts["market_cap_reject"] += 1

        if len(samples["market_cap"]) < 10:
            samples["market_cap"].append(
                (
                    symbol,
                    market_cap,
                )
            )

        continue

    counts["market_cap_pass"] += 1

    # --------------------------------------------------------
    # GAP
    # --------------------------------------------------------

    open_price = f(
        data.get("open_price")
        if data.get("open_price") is not None
        else data.get("open")
    )

    previous_close = f(
        data.get("previous_close")
        if data.get("previous_close") is not None
        else data.get("prev_close")
    )

    try:
        gap_percent = scanner._calculate_gap(
            open_price,
            previous_close,
        )
    except Exception:
        gap_percent = 0.0
        counts["gap_calc_error"] += 1

    if abs(gap_percent) > scanner.maximum_gap_percent:

        counts["gap_reject"] += 1

        if len(samples["gap"]) < 10:
            samples["gap"].append(
                (
                    symbol,
                    open_price,
                    previous_close,
                    gap_percent,
                )
            )

        continue

    counts["gap_pass"] += 1

    # --------------------------------------------------------
    # REACHED INDICATORS
    # --------------------------------------------------------

    counts["reached_indicators"] += 1

    if len(samples["passed"]) < 15:

        samples["passed"].append(
            {
                "symbol": symbol,
                "price": last_price,
                "market_cap": market_cap,
                "open": open_price,
                "previous_close": previous_close,
                "gap": gap_percent,
                "ema9": data.get("ema9"),
                "ema20": data.get("ema20"),
                "ema50": data.get("ema50"),
                "ema200": data.get("ema200"),
                "rsi": data.get("rsi"),
                "macd": data.get("macd"),
                "adx": data.get("adx"),
                "vwap": data.get("vwap"),
                "rvol": data.get("rvol"),
            }
        )


print("=" * 80)
print("FUNNEL")
print("=" * 80)

for name in (
    "received",
    "not_dict",
    "missing_symbol",
    "missing_instrument_key",
    "has_symbol",
    "price_zero",
    "price_reject",
    "price_pass",
    "market_cap_missing",
    "market_cap_reject",
    "market_cap_pass",
    "gap_reject",
    "gap_pass",
    "gap_calc_error",
    "reached_indicators",
):
    print(f"{name:25s}: {counts[name]}")


print()
print("=" * 80)
print("PRICE REJECTION SAMPLES")
print("=" * 80)

for x in samples["price"]:
    print(x)


print()
print("=" * 80)
print("MISSING SYMBOL SAMPLES")
print("=" * 80)

for x in samples["missing_symbol"]:
    print(x)


print()
print("=" * 80)
print("MARKET-CAP REJECTION SAMPLES")
print("=" * 80)

for x in samples["market_cap"]:
    print(x)


print()
print("=" * 80)
print("GAP REJECTION SAMPLES")
print("=" * 80)

for x in samples["gap"]:
    print(x)


print()
print("=" * 80)
print("REACHED INDICATOR STAGE - SAMPLE")
print("=" * 80)

for x in samples["passed"]:
    print(x)


print()
print("=" * 80)

if counts["missing_symbol"] == counts["received"]:
    print("ROOT CAUSE: SYMBOL FIELD MISSING FOR ALL RECORDS")

elif counts["price_reject"] == counts["received"]:
    print("ROOT CAUSE: PRICE GATE REJECTS ALL RECORDS")

elif (
    counts["price_pass"] > 0
    and counts["market_cap_reject"] == counts["price_pass"]
):
    print("ROOT CAUSE: MARKET-CAP GATE REJECTS ALL PRICE-PASS RECORDS")

elif (
    counts["market_cap_pass"] > 0
    and counts["gap_reject"] == counts["market_cap_pass"]
):
    print("ROOT CAUSE: GAP GATE REJECTS ALL REMAINING RECORDS")

elif counts["reached_indicators"] > 0:
    print(
        "EARLY GATES ARE NOT THE ROOT CAUSE:",
        counts["reached_indicators"],
        "records reach indicators."
    )

else:
    print("ROOT CAUSE REQUIRES NEXT-STAGE INSPECTION")

print("=" * 80)
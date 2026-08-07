from pathlib import Path

path = Path("core/market_data/market_data_parser.py")
text = path.read_text(encoding="utf-8")

start_marker = "    def _parse_ltpc("
end_marker = "    def _extract_ohlc("

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1:
    raise RuntimeError("_parse_ltpc() not found")

if end == -1:
    raise RuntimeError("_extract_ohlc() not found")

new_method = '''    def _parse_ltpc(
        self,
        instrument_key: str,
        ltpc: Dict[str, Any],
    ) -> Tick:
        """
        Parse Upstox LTPC feed.

        LTPC fields:
            ltp = last traded price
            ltt = last traded timestamp
            cp  = previous close
        """

        timestamp = self._timestamp(
            ltpc.get("ltt")
        )

        ltp = self._float(
            ltpc.get("ltp")
        )

        previous_close = self._float(
            ltpc.get("cp")
        )

        return Tick(
            instrument_key=instrument_key,
            timestamp=timestamp,
            ltp=ltp,
            previous_close=previous_close,
            close=previous_close,
            volume=0,
            open=0.0,
            high=0.0,
            low=0.0,
            bid_price=0.0,
            bid_quantity=0,
            ask_price=0.0,
            ask_quantity=0,
            open_interest=0.0,
        )

    # =====================================================
    # EXTRACT OHLC
    # =====================================================

'''

# Preserve everything else in the parser exactly.
text = (
    text[:start]
    + new_method
    + text[end:]
)

path.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print("LTPC PATCH COMPLETE")
print("last_price removed:", "last_price=" not in new_method)
print("ltp field added:", "ltp=ltp" in new_method)
print("bid_price field added:", "bid_price=" in new_method)
print("ask_price field added:", "ask_price=" in new_method)

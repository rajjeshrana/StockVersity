"""StockVersity Scanner Pro - Upstox NSE Instrument Master."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.request import Request, urlopen

NSE_BOD_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
DEFAULT_CACHE_FILE = Path(__file__).resolve().parents[2] / "data" / "instruments" / "upstox_nse.json"


@dataclass(frozen=True)
class NSEEquityInstrument:
    instrument_key: str
    trading_symbol: str
    name: str
    isin: str
    short_name: str = ""
    exchange_token: str = ""
    lot_size: float = 1.0
    tick_size: float = 0.0
    security_type: str = ""

    @classmethod
    def from_dict(cls, row: Dict) -> "NSEEquityInstrument":
        return cls(
            instrument_key=str(row.get("instrument_key", "") or "").strip(),
            trading_symbol=str(row.get("trading_symbol", "") or "").strip(),
            name=str(row.get("name", "") or "").strip(),
            isin=str(row.get("isin", "") or "").strip(),
            short_name=str(row.get("short_name", "") or "").strip(),
            exchange_token=str(row.get("exchange_token", "") or "").strip(),
            lot_size=float(row.get("lot_size", 1.0) or 1.0),
            tick_size=float(row.get("tick_size", 0.0) or 0.0),
            security_type=str(row.get("security_type", "") or "").strip(),
        )


class UpstoxInstrumentMaster:
    def __init__(self, cache_file=None, max_cache_age_hours=18, timeout=45):
        self.cache_file = Path(cache_file) if cache_file else DEFAULT_CACHE_FILE
        self.max_cache_age = timedelta(hours=max_cache_age_hours)
        self.timeout = int(timeout)
        self._raw = []
        self._equities = []
        self._by_symbol = {}
        self._by_key = {}
        self._by_isin = {}

    def _cache_is_fresh(self):
        if not self.cache_file.exists():
            return False
        try:
            modified = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            return datetime.now() - modified <= self.max_cache_age
        except OSError:
            return False

    def _read_cache(self):
        with self.cache_file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise ValueError("Cached Upstox NSE instrument file is not a JSON list.")
        return payload

    def _write_cache(self, payload):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.cache_file.with_suffix(".tmp")
        with temp_file.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
        temp_file.replace(self.cache_file)

    def download(self):
        request = Request(
            NSE_BOD_URL,
            headers={
                "User-Agent": "StockVersityScanner/1.0",
                "Accept": "application/json,application/gzip,*/*",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            compressed = response.read()
        try:
            decoded = gzip.decompress(compressed)
        except OSError:
            decoded = compressed
        payload = json.loads(decoded.decode("utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Upstox NSE BOD response is not a JSON list.")
        self._write_cache(payload)
        return payload

    def load(self, force_download=False):
        if not force_download and self._cache_is_fresh():
            try:
                payload = self._read_cache()
            except Exception:
                payload = self.download()
        else:
            payload = self.download()
        self._raw = payload
        self._build_equity_index()
        return self

    def _build_equity_index(self):
        equities = []
        for row in self._raw:
            if not isinstance(row, dict):
                continue
            if str(row.get("segment", "")).upper() != "NSE_EQ":
                continue
            if str(row.get("instrument_type", "")).upper() != "EQ":
                continue
            key = str(row.get("instrument_key", "") or "").strip()
            symbol = str(row.get("trading_symbol", "") or "").strip()
            if key and symbol:
                equities.append(NSEEquityInstrument.from_dict(row))

        equities.sort(key=lambda item: item.trading_symbol.upper())
        self._equities = equities
        self._by_symbol = {x.trading_symbol.upper(): x for x in equities}
        self._by_key = {x.instrument_key: x for x in equities}
        self._by_isin = {x.isin.upper(): x for x in equities if x.isin}

    @property
    def equities(self):
        return list(self._equities)

    def instrument_keys(self):
        return [x.instrument_key for x in self._equities]

    def get_by_symbol(self, symbol):
        return self._by_symbol.get(str(symbol or "").strip().upper())

    def get_by_instrument_key(self, instrument_key):
        return self._by_key.get(str(instrument_key or "").strip())

    def get_by_isin(self, isin):
        return self._by_isin.get(str(isin or "").strip().upper())

    def search(self, query, limit=25):
        needle = str(query or "").strip().upper()
        if not needle:
            return []
        result = []
        for item in self._equities:
            haystack = f"{item.trading_symbol} {item.name} {item.short_name} {item.isin}".upper()
            if needle in haystack:
                result.append(item)
            if len(result) >= max(1, int(limit)):
                break
        return result

    def resolve_symbols(self, symbols: Iterable[str]):
        result = {}
        for symbol in symbols:
            normalized = str(symbol or "").strip().upper()
            item = self._by_symbol.get(normalized)
            if item is not None:
                result[normalized] = item
        return result

    def summary(self):
        return {
            "raw_instruments": len(self._raw),
            "nse_eq_instruments": len(self._equities),
            "cache_file": str(self.cache_file),
        }


InstrumentMaster = UpstoxInstrumentMaster


def _diagnostic():
    print("========================================")
    print("StockVersity Upstox Instrument Master")
    print("========================================")
    try:
        master = UpstoxInstrumentMaster().load()
    except Exception as exc:
        print("NSE instrument file: FAILED")
        print("ERROR:", exc)
        return 1

    print("NSE instrument file: OK")
    print("NSE EQ instruments:", len(master.equities))
    print("Cache:", master.cache_file)

    reliance = master.get_by_symbol("RELIANCE")
    if reliance is None:
        print("RELIANCE lookup: FAILED")
        return 1

    print("RELIANCE:", reliance.instrument_key)
    print("RELIANCE name:", reliance.name)
    print("Instrument cache: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(_diagnostic())

"""
StockVersity Scanner Pro
NIFTY 500 Universe Mapper

Downloads the official NIFTY 500 constituent CSV from NSE Indices and
maps its NSE symbols to the Upstox NSE instrument master.

Run:
    python -m core.market_data.nifty500_universe
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen

from core.market_data.instrument_master import (
    NSEEquityInstrument,
    UpstoxInstrumentMaster,
)

NIFTY500_CSV_URL = (
    "https://www.niftyindices.com/IndexConstituent/"
    "ind_nifty500list.csv"
)

DEFAULT_CACHE_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "instruments"
    / "nifty500_constituents.csv"
)

DEFAULT_MAPPING_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "instruments"
    / "nifty500_upstox_mapping.json"
)


@dataclass(frozen=True)
class Nifty500Stock:
    company_name: str
    industry: str
    symbol: str
    series: str
    isin_code: str
    instrument_key: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "company_name": self.company_name,
            "industry": self.industry,
            "symbol": self.symbol,
            "series": self.series,
            "isin_code": self.isin_code,
            "instrument_key": self.instrument_key,
        }


class Nifty500Universe:
    def __init__(
        self,
        instrument_master: Optional[UpstoxInstrumentMaster] = None,
        cache_file: Optional[str | Path] = None,
        mapping_file: Optional[str | Path] = None,
        max_cache_age_hours: int = 18,
        timeout: int = 45,
    ) -> None:
        self.master = instrument_master or UpstoxInstrumentMaster()
        self.cache_file = Path(cache_file) if cache_file else DEFAULT_CACHE_FILE
        self.mapping_file = Path(mapping_file) if mapping_file else DEFAULT_MAPPING_FILE
        self.max_cache_age = timedelta(hours=max_cache_age_hours)
        self.timeout = int(timeout)

        self.constituents: List[Dict[str, str]] = []
        self.stocks: List[Nifty500Stock] = []
        self.missing: List[Dict[str, str]] = []

    def _cache_is_fresh(self) -> bool:
        if not self.cache_file.exists():
            return False
        try:
            modified = datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            return datetime.now() - modified <= self.max_cache_age
        except OSError:
            return False

    def download_constituents(self) -> str:
        request = Request(
            NIFTY500_CSV_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/150 Safari/537.36"
                ),
                "Accept": "text/csv,text/plain,*/*",
                "Referer": "https://www.niftyindices.com/",
            },
        )

        with urlopen(request, timeout=self.timeout) as response:
            raw = response.read()

        text = raw.decode("utf-8-sig", errors="replace")

        if "Symbol" not in text or "Company Name" not in text:
            raise ValueError(
                "Downloaded NIFTY 500 file does not look like the expected constituent CSV."
            )

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(text, encoding="utf-8")
        return text

    def _load_csv_text(self, force_download: bool = False) -> str:
        if not force_download and self._cache_is_fresh():
            return self.cache_file.read_text(encoding="utf-8-sig")
        return self.download_constituents()

    @staticmethod
    def _normalize_row(row: Dict[str, str]) -> Dict[str, str]:
        clean = {
            str(key or "").strip(): str(value or "").strip()
            for key, value in row.items()
            if key is not None
        }
        return clean

    def load(
        self,
        force_download: bool = False,
        force_instrument_download: bool = False,
    ) -> "Nifty500Universe":
        if not self.master.equities:
            self.master.load(force_download=force_instrument_download)

        text = self._load_csv_text(force_download=force_download)
        reader = csv.DictReader(io.StringIO(text))

        rows = [
            self._normalize_row(row)
            for row in reader
            if row
        ]

        if not rows:
            raise ValueError("NIFTY 500 constituent CSV is empty.")

        self.constituents = rows
        self._map_to_upstox()
        self._save_mapping()
        return self

    def _map_to_upstox(self) -> None:
        mapped: List[Nifty500Stock] = []
        missing: List[Dict[str, str]] = []

        seen_keys = set()

        for row in self.constituents:
            symbol = row.get("Symbol", "").strip().upper()
            isin = (
                row.get("ISIN Code", "")
                or row.get("ISIN", "")
            ).strip().upper()

            instrument: Optional[NSEEquityInstrument] = None

            # ISIN is the strongest match when present.
            if isin:
                instrument = self.master.get_by_isin(isin)

            # Symbol is the fallback and also covers harmless CSV variations.
            if instrument is None and symbol:
                instrument = self.master.get_by_symbol(symbol)

            if instrument is None:
                missing.append(row)
                continue

            if instrument.instrument_key in seen_keys:
                continue

            seen_keys.add(instrument.instrument_key)

            mapped.append(
                Nifty500Stock(
                    company_name=row.get("Company Name", instrument.name),
                    industry=row.get("Industry", ""),
                    symbol=symbol or instrument.trading_symbol,
                    series=row.get("Series", ""),
                    isin_code=isin or instrument.isin,
                    instrument_key=instrument.instrument_key,
                )
            )

        self.stocks = mapped
        self.missing = missing

    def _save_mapping(self) -> None:
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source": NIFTY500_CSV_URL,
            "constituent_rows": len(self.constituents),
            "mapped_count": len(self.stocks),
            "missing_count": len(self.missing),
            "stocks": [stock.to_dict() for stock in self.stocks],
            "missing": self.missing,
        }
        self.mapping_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def instrument_keys(self) -> List[str]:
        return [stock.instrument_key for stock in self.stocks]

    def symbols(self) -> List[str]:
        return [stock.symbol for stock in self.stocks]

    def by_symbol(self) -> Dict[str, Nifty500Stock]:
        return {stock.symbol.upper(): stock for stock in self.stocks}

    def sector_groups(self) -> Dict[str, List[Nifty500Stock]]:
        groups: Dict[str, List[Nifty500Stock]] = {}
        for stock in self.stocks:
            sector = stock.industry.strip() or "Unknown"
            groups.setdefault(sector, []).append(stock)
        return groups

    def summary(self) -> Dict[str, object]:
        return {
            "constituent_rows": len(self.constituents),
            "mapped": len(self.stocks),
            "missing": len(self.missing),
            "unique_instrument_keys": len(set(self.instrument_keys())),
            "industries": len(self.sector_groups()),
            "cache_file": str(self.cache_file),
            "mapping_file": str(self.mapping_file),
        }


def _diagnostic() -> int:
    print("========================================")
    print("StockVersity NIFTY 500 Universe")
    print("========================================")

    try:
        universe = Nifty500Universe().load()
    except Exception as exc:
        print("NIFTY 500 constituent file: FAILED")
        print("ERROR:", exc)
        return 1

    info = universe.summary()

    print("NIFTY 500 constituent file: OK")
    print("Constituent rows:", info["constituent_rows"])
    print("Mapped to Upstox:", info["mapped"])
    print("Missing:", info["missing"])
    print("Unique instrument keys:", info["unique_instrument_keys"])
    print("Industry groups:", info["industries"])
    print("Mapping file:", info["mapping_file"])

    reliance = universe.by_symbol().get("RELIANCE")
    if reliance:
        print("RELIANCE:", reliance.instrument_key)
    else:
        print("RELIANCE: NOT FOUND")

    if universe.missing:
        print("")
        print("First missing symbols:")
        for row in universe.missing[:10]:
            print(
                " -",
                row.get("Symbol", "?"),
                "|",
                row.get("Company Name", ""),
                "|",
                row.get("ISIN Code", ""),
            )

    # Do not hard-fail merely because index methodology can produce
    # slightly more than 500 securities or a temporary symbol mismatch.
    if not universe.stocks:
        return 1

    print("NIFTY 500 mapping: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(_diagnostic())

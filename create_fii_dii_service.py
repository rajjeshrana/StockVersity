from pathlib import Path

path = Path("backend/services/fii_dii_service.py")

if path.exists():
    raise SystemExit(
        "SAFETY STOP: fii_dii_service.py already exists. "
        "File not overwritten."
    )

code = r'''"""
=========================================================
StockVersity Scanner Pro

FII / DII Service

Fetches NSE institutional cash-market activity and
normalizes it for the StockVersity dashboard.
=========================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from backend.services.nse_service import NseService


class FIIDIIService:
    """
    NSE FII / DII institutional activity service.

    Normalized result:

    {
        "date": "2026-08-04",
        "fii": {
            "buy": 0.0,
            "sell": 0.0,
            "net": 0.0,
        },
        "dii": {
            "buy": 0.0,
            "sell": 0.0,
            "net": 0.0,
        },
        "net": 0.0,
        "available": True,
    }
    """

    ENDPOINT = "/api/fiidiiTradeReact"

    def __init__(self):

        self.logger = logging.getLogger(
            __name__
        )

        self.nse = NseService()

        self._last_valid: Dict[str, Any] = {}

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _float(
        value: Any,
    ) -> float:

        if value is None:
            return 0.0

        if isinstance(
            value,
            (int, float),
        ):
            return float(value)

        text = str(value).strip()

        text = (
            text
            .replace(",", "")
            .replace("₹", "")
            .replace("Rs.", "")
            .replace("Rs", "")
        )

        try:
            return float(text)

        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    # -----------------------------------------------------

    @staticmethod
    def _normalize_date(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        text = str(value).strip()

        if not text:
            return ""

        formats = (
            "%d-%b-%Y",
            "%d-%b-%y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d %b %Y",
        )

        for fmt in formats:

            try:

                dt = datetime.strptime(
                    text,
                    fmt,
                )

                return dt.strftime(
                    "%Y-%m-%d"
                )

            except ValueError:
                pass

        return text

    # -----------------------------------------------------

    @staticmethod
    def _category(
        row: Dict[str, Any],
    ) -> str:

        candidates = (
            "category",
            "categoryName",
            "clientType",
            "client_type",
            "name",
        )

        for key in candidates:

            value = row.get(key)

            if value:
                return str(value).strip().upper()

        return ""

    # -----------------------------------------------------

    @staticmethod
    def _pick(
        row: Dict[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:

            if key in row:
                return row.get(key)

        return None

    # -----------------------------------------------------

    def _normalize_row(
        self,
        row: Dict[str, Any],
    ) -> Dict[str, float]:

        buy = self._float(
            self._pick(
                row,
                "buyValue",
                "buy_value",
                "buy",
                "buyAmount",
            )
        )

        sell = self._float(
            self._pick(
                row,
                "sellValue",
                "sell_value",
                "sell",
                "sellAmount",
            )
        )

        raw_net = self._pick(
            row,
            "netValue",
            "net_value",
            "net",
            "netAmount",
        )

        if raw_net is None:
            net = buy - sell
        else:
            net = self._float(
                raw_net
            )

        return {
            "buy": buy,
            "sell": sell,
            "net": net,
        }

    # -----------------------------------------------------

    def _extract_date(
        self,
        rows: list,
    ) -> str:

        date_keys = (
            "date",
            "tradeDate",
            "trade_date",
            "asOnDate",
        )

        for row in rows:

            if not isinstance(
                row,
                dict,
            ):
                continue

            for key in date_keys:

                value = row.get(key)

                if value:
                    return self._normalize_date(
                        value
                    )

        return ""

    # =====================================================
    # FETCH
    # =====================================================

    def fetch(
        self,
    ) -> Dict[str, Any]:

        try:

            self.nse.ensure_session()

            url = (
                self.nse.API
                + self.ENDPOINT
            )

            response = self.nse.session.get(
                url,
                timeout=12,
            )

            # NSE sometimes invalidates cookies.
            if response.status_code in (
                401,
                403,
            ):

                self.nse.refresh_session()

                response = self.nse.session.get(
                    url,
                    timeout=12,
                )

            response.raise_for_status()

            payload = response.json()

            if isinstance(
                payload,
                list,
            ):
                rows = payload

            elif isinstance(
                payload,
                dict,
            ):

                rows = (
                    payload.get("data")
                    or payload.get("records")
                    or payload.get("value")
                    or []
                )

            else:
                rows = []

            if not isinstance(
                rows,
                list,
            ):
                rows = []

            fii_row: Optional[
                Dict[str, Any]
            ] = None

            dii_row: Optional[
                Dict[str, Any]
            ] = None

            for row in rows:

                if not isinstance(
                    row,
                    dict,
                ):
                    continue

                category = self._category(
                    row
                )

                if (
                    "FII" in category
                    or "FPI" in category
                ):
                    fii_row = row

                elif "DII" in category:
                    dii_row = row

            if (
                fii_row is None
                or dii_row is None
            ):

                raise ValueError(
                    "NSE FII/DII rows not found "
                    "in response."
                )

            fii = self._normalize_row(
                fii_row
            )

            dii = self._normalize_row(
                dii_row
            )

            session_date = (
                self._extract_date(
                    rows
                )
            )

            result = {
                "date": session_date,
                "fii": fii,
                "dii": dii,
                "net": (
                    fii["net"]
                    + dii["net"]
                ),
                "available": True,
            }

            self._last_valid = result

            return result

        except Exception as exc:

            self.logger.exception(
                "Unable to fetch FII/DII data: %s",
                exc,
            )

            if self._last_valid:

                result = dict(
                    self._last_valid
                )

                result["stale"] = True

                return result

            return {
                "date": "",
                "fii": {
                    "buy": 0.0,
                    "sell": 0.0,
                    "net": 0.0,
                },
                "dii": {
                    "buy": 0.0,
                    "sell": 0.0,
                    "net": 0.0,
                },
                "net": 0.0,
                "available": False,
            }

    # =====================================================
    # CLOSE
    # =====================================================

    def close(
        self,
    ) -> None:

        try:
            self.nse.session.close()

        except Exception:
            pass


# =========================================================
# SELF TEST
# =========================================================

if __name__ == "__main__":

    import json

    service = FIIDIIService()

    try:

        result = service.fetch()

        print(
            "========================================"
        )
        print(
            "StockVersity FII / DII Service"
        )
        print(
            "========================================"
        )

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
        )

        print(
            "========================================"
        )

    finally:

        service.close()
'''

path.write_text(
    code,
    encoding="utf-8",
)

print()
print("========================================")
print("FII / DII SERVICE CREATED")
print("========================================")
print("File :", path)
print("NSE session : NseService")
print("Fake data   : NONE")
print("Date        : FROM NSE RESPONSE")
print("========================================")

"""
StockVersity Pro
Previous Session Market Loader

Purpose
-------
Loads the latest completed daily candle for the main NSE indices
through the EXISTING DataManager / Upstox historical-data pipeline.

This module does NOT create:
- another Upstox client
- another websocket
- another authentication session
- another market-data provider

It only consumes the existing DataManager instance.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, Optional

import pandas as pd


logger = logging.getLogger(__name__)


class PreviousSessionLoader:
    """
    Bootstrap dashboard index values from Upstox historical data.

    Intended use:
        - application startup
        - before first live websocket tick
        - weekends
        - holidays
        - pre-market
        - after market close

    Live websocket data remains authoritative once received.
    """

    INDEX_INSTRUMENTS = {
        "NIFTY": "NSE_INDEX|Nifty 50",
        "BANKNIFTY": "NSE_INDEX|Nifty Bank",
        "FINNIFTY": "NSE_INDEX|Nifty Fin Service",
        "INDIA VIX": "NSE_INDEX|India VIX",
    }

    def __init__(self, data_manager) -> None:
        self.data_manager = data_manager

    # =====================================================
    # PUBLIC API
    # =====================================================

    def load(self) -> Dict[str, Dict[str, Any]]:
        """
        Load latest completed daily values for configured indices.

        Returns
        -------
        {
            "NIFTY": {
                "ltp": 24500.10,
                "change": 120.25,
                "change_percent": 0.49,
                "previous_close": 24379.85,
                "source": "historical",
            },
            ...
        }
        """

        result: Dict[str, Dict[str, Any]] = {}

        for market_key, instrument_key in (
            self.INDEX_INSTRUMENTS.items()
        ):
            try:
                snapshot = self._load_instrument(
                    instrument_key
                )

                if snapshot:
                    result[market_key] = snapshot

            except Exception:
                logger.exception(
                    "Previous-session load failed for %s",
                    market_key,
                )

        return result

    # =====================================================
    # LOAD ONE INDEX
    # =====================================================

    def _load_instrument(
        self,
        instrument_key: str,
    ) -> Optional[Dict[str, Any]]:

        today = date.today()

        # Enough calendar history to safely cover weekends
        # and ordinary exchange holidays.
        from_date = (
            today - timedelta(days=15)
        ).isoformat()

        to_date = today.isoformat()

        dataframe = self.data_manager.load_history(
            instrument_key=instrument_key,
            timeframe="day",
            from_date=from_date,
            to_date=to_date,
        )

        if dataframe is None or dataframe.empty:
            logger.warning(
                "No historical candles returned for %s",
                instrument_key,
            )
            return None

        dataframe = dataframe.copy()

        dataframe = self._normalise_dataframe(
            dataframe
        )

        if dataframe.empty:
            return None

        #
        # We need at least two completed sessions:
        #
        # latest candle       -> displayed close
        # previous candle     -> change calculation
        #
        if len(dataframe) < 2:
            logger.warning(
                "Not enough daily candles for %s",
                instrument_key,
            )
            return None

        latest = dataframe.iloc[-1]
        previous = dataframe.iloc[-2]

        latest_close = self._number(
            latest.get("close")
        )

        previous_close = self._number(
            previous.get("close")
        )

        if latest_close is None:
            return None

        change = 0.0
        change_percent = 0.0

        if (
            previous_close is not None
            and previous_close != 0
        ):
            change = (
                latest_close - previous_close
            )

            change_percent = (
                change / previous_close
            ) * 100.0

        return {
            "ltp": latest_close,
            "price": latest_close,
            "close": latest_close,

            "previous_close": (
                previous_close
                if previous_close is not None
                else latest_close
            ),

            "change": change,
            "change_percent": change_percent,

            # Compatibility alias used by some UI code.
            "change_pct": change_percent,

            "open": self._number(
                latest.get("open")
            ),
            "high": self._number(
                latest.get("high")
            ),
            "low": self._number(
                latest.get("low")
            ),

            "volume": self._number(
                latest.get("volume")
            ),

            "source": "historical",
            "instrument_key": instrument_key,
            "session": self._extract_session(
                latest
            ),
        }

    # =====================================================
    # NORMALISE DATAFRAME
    # =====================================================

    @staticmethod
    def _normalise_dataframe(
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        if dataframe is None or dataframe.empty:
            return pd.DataFrame()

        df = dataframe.copy()

        #
        # Normalise column names.
        #
        df.columns = [
            str(column).strip().lower()
            for column in df.columns
        ]

        #
        # Detect timestamp/date column.
        #
        timestamp_column = None

        for candidate in (
            "timestamp",
            "datetime",
            "date",
            "time",
        ):
            if candidate in df.columns:
                timestamp_column = candidate
                break

        if timestamp_column is not None:
            try:
                df[timestamp_column] = (
                    pd.to_datetime(
                        df[timestamp_column],
                        errors="coerce",
                    )
                )

                df = df.sort_values(
                    timestamp_column
                )

            except Exception:
                logger.exception(
                    "Could not sort historical dataframe"
                )

        #
        # Remove rows without usable close.
        #
        if "close" not in df.columns:
            logger.warning(
                "Historical dataframe has no close column"
            )
            return pd.DataFrame()

        df["close"] = pd.to_numeric(
            df["close"],
            errors="coerce",
        )

        df = df.dropna(
            subset=["close"]
        )

        return df.reset_index(
            drop=True
        )

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        try:
            if pd.isna(value):
                return None
        except Exception:
            pass

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_session(
        row: pd.Series,
    ) -> Optional[str]:

        for key in (
            "timestamp",
            "datetime",
            "date",
            "time",
        ):
            value = row.get(key)

            if value is None:
                continue

            try:
                if pd.isna(value):
                    continue
            except Exception:
                pass

            try:
                timestamp = pd.to_datetime(
                    value
                )

                return timestamp.date().isoformat()

            except Exception:
                return str(value)

        return None
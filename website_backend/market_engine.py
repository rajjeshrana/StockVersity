from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import requests

logger = logging.getLogger("stockversity-market")


@dataclass
class Quote:
    symbol: str
    instrument_key: str | None = None
    price: float | None = None
    previous_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    timestamp: str | None = None
    source: str | None = None
    stale: bool = True
    error: str | None = None


class MarketEngine:
    """
    Independent website market engine.

    It does NOT read from the desktop application and does NOT call
    the old Upstox V2 market-feed endpoint.

    Indian instruments are read from Upstox V3 REST quotes.
    BTC uses public market data fallbacks.
    GOLD uses Yahoo gold futures as the no-key fallback; an optional
    Twelve Data key can be configured for a dedicated metals feed.
    """

    UPSTOX_V3 = "https://api.upstox.com/v3/market-quote/quotes"
    YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self) -> None:
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
        self.poll_seconds = max(
            1,
            int(os.getenv("MARKET_POLL_SECONDS", "2")),
        )

        self.instruments: dict[str, str] = {
            "NIFTY": os.getenv(
                "UPSTOX_NIFTY_KEY",
                "NSE_INDEX|Nifty 50",
            ).strip(),
            "BANKNIFTY": os.getenv(
                "UPSTOX_BANKNIFTY_KEY",
                "NSE_INDEX|Nifty Bank",
            ).strip(),
            "VIX": os.getenv(
                "UPSTOX_VIX_KEY",
                "NSE_INDEX|India VIX",
            ).strip(),
            "GIFT": os.getenv(
                "UPSTOX_GIFT_KEY",
                "GLOBAL_INDEX|SGX NIFTY",
            ).strip(),
        }

        self.quotes: dict[str, Quote] = {
            "NIFTY": Quote(
                symbol="NIFTY 50",
                instrument_key=self.instruments["NIFTY"],
            ),
            "BANKNIFTY": Quote(
                symbol="BANK NIFTY",
                instrument_key=self.instruments["BANKNIFTY"],
            ),
            "VIX": Quote(
                symbol="INDIA VIX",
                instrument_key=self.instruments["VIX"],
            ),
            "GIFT": Quote(
                symbol="GIFT NIFTY",
                instrument_key=self.instruments["GIFT"],
            ),
            "BTC": Quote(symbol="BTC/USD"),
            "GOLD": Quote(symbol="GOLD/USD"),
        }

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "StockVersity/1.0",
                "Accept": "application/json",
            }
        )

        self.running = False
        self.task: asyncio.Task | None = None
        self.last_cycle: str | None = None
        self.last_error: str | None = None
        self.upstox_connected = False

    async def start(self) -> None:
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(
            self._loop(),
            name="stockversity-market-engine",
        )
        logger.info("Independent market engine started.")

    async def stop(self) -> None:
        self.running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        self.session.close()
        logger.info("Independent market engine stopped.")

    async def _loop(self) -> None:
        backoff = 1

        while self.running:
            started = time.monotonic()

            try:
                await asyncio.to_thread(self.refresh_once)
                backoff = 1
            except Exception as exc:
                self.last_error = str(exc)
                logger.exception("Market refresh failed")
                await asyncio.sleep(min(backoff, 30))
                backoff = min(backoff * 2, 30)
                continue

            elapsed = time.monotonic() - started
            await asyncio.sleep(
                max(0.1, self.poll_seconds - elapsed)
            )

    def refresh_once(self) -> None:
        self._refresh_upstox_quotes()
        self._refresh_btc()
        self._refresh_gold()

        now = datetime.now(timezone.utc).isoformat()
        self.last_cycle = now

    def _refresh_upstox_quotes(self) -> None:
        if not self.access_token:
            self.upstox_connected = False
            for key in ("NIFTY", "BANKNIFTY", "VIX", "GIFT"):
                self.quotes[key].error = "UPSTOX_ACCESS_TOKEN not configured"
            return

        keys = [
            value
            for value in self.instruments.values()
            if value
        ]

        try:
            response = self.session.get(
                self.UPSTOX_V3,
                params={"instrument_key": ",".join(keys)},
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()

            data = payload.get("data", {})
            if not isinstance(data, dict):
                raise RuntimeError(
                    "Upstox V3 quote response contained no data object"
                )

            self.upstox_connected = True

            reverse = {
                instrument_key: logical
                for logical, instrument_key in self.instruments.items()
            }

            for instrument_key, quote_data in data.items():
                logical = reverse.get(instrument_key) or reverse.get(instrument_key.replace(":", "|"))
                if not logical:
                    continue
                self._apply_upstox_quote(
                    logical,
                    quote_data,
                )

            for logical in ("NIFTY", "BANKNIFTY", "VIX", "GIFT"):
                if self.quotes[logical].price is None:
                    self.quotes[logical].stale = True

        except Exception as exc:
            self.upstox_connected = False
            message = str(exc)
            logger.warning("Upstox V3 quote refresh failed: %s", message)
            for logical in ("NIFTY", "BANKNIFTY", "VIX", "GIFT"):
                self.quotes[logical].error = message
                self.quotes[logical].stale = True

    def _apply_upstox_quote(
        self,
        logical: str,
        quote_data: Any,
    ) -> None:
        if not isinstance(quote_data, dict):
            return

        price = self._number(
            quote_data.get("last_price")
        )
        previous_close = self._number(
            quote_data.get("prev_close_price")
        )

        # Some responses nest previous close or LTPC data.
        if price is None:
            ltpc = quote_data.get("ltpc")
            if isinstance(ltpc, dict):
                price = self._number(ltpc.get("ltp"))
                if previous_close is None:
                    previous_close = self._number(
                        ltpc.get("cp")
                    )

        net_change = self._number(
            quote_data.get("net_change")
        )

        # Upstox V3 index quotes may not provide prev_close_price.
        # Derive the true previous close from last price - net change.
        if (
            net_change is not None
            and price is not None
        ):
            previous_close = price - net_change

        change = net_change
        change_percent = None

        if (
            change is not None
            and previous_close not in (None, 0)
        ):
            change_percent = change / previous_close * 100.0

        q = self.quotes[logical]
        q.price = price
        q.previous_close = previous_close
        q.change = change
        q.change_percent = change_percent
        q.timestamp = datetime.now(timezone.utc).isoformat()
        q.source = "upstox-v3"
        q.stale = price is None
        q.error = None if price is not None else "No price in V3 response"

    def _refresh_btc(self) -> None:
        try:
            ticker_response = self.session.get(
                "https://api.india.delta.exchange/v2/tickers/BTCUSD",
                headers={"Accept": "application/json"},
                timeout=8,
            )
            ticker_response.raise_for_status()

            ticker_payload = ticker_response.json()
            ticker = ticker_payload.get("result", {})

            current_price = self._number(
                ticker.get("close")
            )

            if current_price is None:
                raise RuntimeError(
                    "Delta BTCUSD returned no live price"
                )

            now = int(time.time())

            candle_response = self.session.get(
                "https://api.india.delta.exchange/v2/history/candles",
                params={
                    "resolution": "1d",
                    "symbol": "BTCUSD",
                    "start": now - (4 * 86400),
                    "end": now,
                },
                headers={"Accept": "application/json"},
                timeout=8,
            )
            candle_response.raise_for_status()

            candle_payload = candle_response.json()
            candles = candle_payload.get("result", [])

            if not isinstance(candles, list) or len(candles) < 2:
                raise RuntimeError(
                    "Delta BTCUSD daily history unavailable"
                )

            candles = sorted(
                [
                    c for c in candles
                    if isinstance(c, dict)
                    and c.get("time") is not None
                ],
                key=lambda c: int(c["time"]),
                reverse=True,
            )

            # Latest candle may be the currently forming daily candle.
            # The next candle is therefore the previous completed daily close.
            previous_daily_close = self._number(
                candles[1].get("close")
            )

            if previous_daily_close is None:
                raise RuntimeError(
                    "Delta previous daily BTCUSD close unavailable"
                )

            change = current_price - previous_daily_close
            change_percent = (
                change / previous_daily_close * 100.0
            )

            q = self.quotes["BTC"]
            q.price = current_price
            q.previous_close = previous_daily_close
            q.change = change
            q.change_percent = change_percent
            q.timestamp = datetime.now(
                timezone.utc
            ).isoformat()
            q.source = "delta-btcusd-perpetual"
            q.stale = False
            q.error = None

        except Exception as exc:
            q = self.quotes["BTC"]
            q.error = str(exc)
            q.stale = True
    def _refresh_gold(self) -> None:
        # Delta Exchange India XAUTUSD perpetual.
        def gold_float(value):
            try:
                if value is None or value == "":
                    return None
                return float(value)
            except (TypeError, ValueError):
                return None

        # Prefer the previous daily candle close. If Delta does not return
        # a usable daily candle, derive the previous reference price from
        # Delta's 24h percentage so the header still has both values.

        ticker_url = "https://api.india.delta.exchange/v2/tickers/XAUTUSD"
        candles_url = "https://api.india.delta.exchange/v2/history/candles"

        try:
            ticker_response = self.session.get(
                ticker_url,
                timeout=8,
            )
            ticker_response.raise_for_status()
            ticker_payload = ticker_response.json()

            result = ticker_payload.get("result") or {}
            if isinstance(result, list):
                result = result[0] if result else {}

            price = gold_float(result.get("close"))

            if price is None:
                raise ValueError("Delta XAUTUSD returned no close price")

            previous_close = None

            # First choice: actual previous daily candle close.
            try:
                candle_response = self.session.get(
                    candles_url,
                    params={
                        "resolution": "1d",
                        "symbol": "XAUTUSD",
                    },
                    timeout=8,
                )
                candle_response.raise_for_status()
                candle_payload = candle_response.json()

                candles = candle_payload.get("result") or []

                if isinstance(candles, dict):
                    candles = (
                        candles.get("candles")
                        or candles.get("data")
                        or []
                    )

                if isinstance(candles, list):
                    parsed_candles = []

                    for candle in candles:
                        if isinstance(candle, dict):
                            close_value = (
                                candle.get("close")
                                or candle.get("c")
                            )
                            timestamp_value = (
                                candle.get("time")
                                or candle.get("timestamp")
                                or candle.get("t")
                            )
                        elif isinstance(candle, list) and len(candle) >= 5:
                            timestamp_value = candle[0]
                            close_value = candle[4]
                        else:
                            continue

                        close_value = gold_float(close_value)
                        timestamp_value = gold_float(timestamp_value)

                        if close_value is not None:
                            parsed_candles.append(
                                (timestamp_value, close_value)
                            )

                    parsed_candles.sort(
                        key=lambda item: item[0]
                        if item[0] is not None
                        else 0,
                        reverse=True,
                    )

                    # The newest candle can represent the current day.
                    # Use the most recent close that is below the current
                    # live price reference when possible; otherwise use the
                    # second candle, which is normally the preceding daily bar.
                    if len(parsed_candles) >= 2:
                        previous_close = parsed_candles[1][1]
                    elif parsed_candles:
                        previous_close = parsed_candles[0][1]

            except Exception as candle_exc:
                logger.debug(
                    "XAUTUSD daily candle lookup failed: %s",
                    candle_exc,
                )

            # Fallback: reconstruct the previous reference price from
            # Delta's ltp_change_24h percentage.
            if previous_close in (None, 0):
                pct_24h = gold_float(
                    result.get("ltp_change_24h")
                )

                if pct_24h is None:
                    pct_24h = gold_float(
                        result.get("change_24h")
                    )

                if pct_24h is not None and (100.0 + pct_24h) != 0:
                    previous_close = price / (
                        1.0 + pct_24h / 100.0
                    )

            change = None
            change_percent = None

            if previous_close not in (None, 0):
                change = price - previous_close
                change_percent = (
                    change / previous_close * 100.0
                )

            q = self.quotes["GOLD"]
            q.price = price
            q.previous_close = previous_close
            q.change = change
            q.change_percent = change_percent
            q.timestamp = datetime.now(timezone.utc).isoformat()
            q.source = "delta-xautusd-perpetual"
            q.stale = False
            q.error = None

        except Exception as exc:
            q = self.quotes["GOLD"]
            q.stale = q.price is None
            q.error = str(exc)

    def _refresh_external(
        self,
        logical: str,
        candidates: list[tuple[str, str, Any]],
        params: dict[str, str] | None = None,
    ) -> None:
        last_error = None

        for url, source, parser in candidates:
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=8,
                )
                response.raise_for_status()
                payload = response.json()

                parsed = parser(payload)

                if parsed and parsed[0] is not None:
                    price, previous_close = parsed

                    change = None
                    change_percent = None
                    if (
                        previous_close is not None
                        and previous_close != 0
                    ):
                        change = price - previous_close
                        change_percent = (
                            change / previous_close * 100.0
                        )

                    q = self.quotes[logical]
                    q.price = price
                    q.previous_close = previous_close
                    q.change = change
                    q.change_percent = change_percent
                    q.timestamp = datetime.now(
                        timezone.utc
                    ).isoformat()
                    q.source = source
                    q.stale = False
                    q.error = None
                    return

                last_error = "No usable price returned"

            except Exception as exc:
                last_error = str(exc)

        q = self.quotes[logical]
        q.error = last_error or "No provider available"
        q.stale = True

    @staticmethod
    def _parse_coinbase_btc(payload: Any):
        try:
            value = float(payload["data"]["amount"])
            return value, None
        except Exception:
            return None, None

    @staticmethod
    def _parse_twelve_price(payload: Any):
        try:
            return float(payload["price"]), None
        except Exception:
            return None, None

    @staticmethod
    def _parse_yahoo(payload: Any):
        result = payload.get("chart", {}).get("result")
        if not result:
            return None, None

        meta = result[0].get("meta", {})
        price = (
            meta.get("regularMarketPrice")
            or meta.get("previousClose")
        )
        previous_close = meta.get("previousClose")

        try:
            return (
                float(price) if price is not None else None,
                float(previous_close)
                if previous_close is not None
                else None,
            )
        except Exception:
            return None, None

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            if value is None or value == "":
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def payload(self) -> dict[str, Any]:
        results = []

        order = (
            "NIFTY",
            "BANKNIFTY",
            "VIX",
            "GIFT",
            "BTC",
            "GOLD",
        )

        for logical in order:
            item = asdict(self.quotes[logical])
            item["key"] = logical
            results.append(item)

        return {
            "ok": True,
            "count": len(
                [
                    q
                    for q in self.quotes.values()
                    if q.price is not None
                ]
            ),
            "results": results,
            "websocket": {
                "connected": self.upstox_connected,
                "mode": "UPSTOX_V3_LIVE_QUOTES",
                "provider": "upstox",
            },
            "server": {
                "independent": True,
                "source": "StockVersity standalone website backend",
                "last_cycle": self.last_cycle,
            },
        }

    def health(self) -> dict[str, Any]:
        live = sum(
            1
            for q in self.quotes.values()
            if q.price is not None and not q.stale
        )

        return {
            "ok": True,
            "service": "stockversity-market-engine",
            "independent": True,
            "running": self.running,
            "live_quotes": live,
            "total_quotes": len(self.quotes),
            "upstox_connected": self.upstox_connected,
            "last_cycle": self.last_cycle,
            "last_error": self.last_error,
        }
















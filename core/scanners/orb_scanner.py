"""
=========================================================
StockVersity Scanner Pro
ORB Scanner
Version : 2.1
=========================================================

File:
    core/scanners/orb_scanner.py

Purpose:
    Opening Range Breakout scanner for intraday trading.

Strategy
--------
• Build opening range from early-session candles
• Detect bullish breakout above ORB high
• Detect bearish breakdown below ORB low
• Require breakout confirmation
• Volume / RVOL confirmation
• VWAP alignment
• EMA trend alignment
• ADX / directional strength
• Gap filter
• ORB width filter
• Risk / reward validation
• Institutional-style scoring

Designed for:
    NSE intraday scanning
=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.scanner.base_scanner import BaseScanner
from core.scanner.signal import (
    MarketTrend,
    PatternType,
    Signal,
    SignalStrength,
    SignalType,
)


# =========================================================
# CONSTANTS
# =========================================================

SCANNER_NAME = "ORBScanner"
SCANNER_VERSION = "2.1"

DEFAULT_TIMEFRAME = "5m"

DEFAULT_ORB_MINUTES = 15

DEFAULT_MINIMUM_SCORE = 70.0

DEFAULT_MINIMUM_CONFIDENCE = 65.0

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_MINIMUM_RVOL = 1.5

DEFAULT_MINIMUM_ADX = 20.0

DEFAULT_MAX_GAP_PERCENT = 3.0

DEFAULT_MAX_ORB_WIDTH_PERCENT = 3.0

DEFAULT_BREAKOUT_BUFFER_PERCENT = 0.05


# =========================================================
# SAFE HELPERS
# =========================================================

def _float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert value to float.
    """

    try:

        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Safely convert value to int.
    """

    try:

        if value is None:
            return default

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _get(
    data: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Return first available key from dictionary.
    """

    for key in keys:

        if key in data:

            value = data.get(
                key
            )

            if value is not None:
                return value

    return default


# =========================================================
# ORB SCANNER
# =========================================================

class ORBScanner(BaseScanner):
    """
    Opening Range Breakout scanner.

    Primary use
    -----------
    Intraday momentum opportunities after the
    opening range has been established.

    Default opening range:
        09:15 - 09:30 IST

    Expected market-data formats
    ----------------------------
    The scanner accepts flexible symbol dictionaries.

    Example:

        {
            "NSE_EQ|INE...": {
                "instrument_key": "...",
                "symbol": "RELIANCE",
                "ltp": 1400,
                "open": 1380,
                "high": 1405,
                "low": 1375,
                "previous_close": 1385,
                "volume": 1000000,
                "average_volume": 500000,
                "vwap": 1392,
                "ema20": 1388,
                "ema50": 1370,
                "adx": 28,
                "plus_di": 30,
                "minus_di": 15,
                "orb_high": 1398,
                "orb_low": 1380
            }
        }

    Candle-based data is also supported where
    possible.
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        timeframe: str = DEFAULT_TIMEFRAME,
        orb_minutes: int = DEFAULT_ORB_MINUTES,
        minimum_score: float = DEFAULT_MINIMUM_SCORE,
        minimum_confidence: float = DEFAULT_MINIMUM_CONFIDENCE,
        minimum_rr: float = DEFAULT_MINIMUM_RR,
        minimum_rvol: float = DEFAULT_MINIMUM_RVOL,
        minimum_adx: float = DEFAULT_MINIMUM_ADX,
        maximum_gap_percent: float = DEFAULT_MAX_GAP_PERCENT,
        maximum_orb_width_percent: float = (
            DEFAULT_MAX_ORB_WIDTH_PERCENT
        ),
        breakout_buffer_percent: float = (
            DEFAULT_BREAKOUT_BUFFER_PERCENT
        ),
        require_volume: bool = True,
        require_vwap: bool = True,
        require_adx: bool = True,
        require_ema_alignment: bool = True,
        allow_buy: bool = True,
        allow_sell: bool = True,
    ) -> None:

        super().__init__(
            name=SCANNER_NAME,
            version=SCANNER_VERSION,
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # ORB CONFIGURATION
        # -------------------------------------------------

        self.orb_minutes = max(
            5,
            int(orb_minutes),
        )

        self.minimum_score = float(
            minimum_score
        )

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.minimum_rr = float(
            minimum_rr
        )

        self.minimum_rvol = max(
            0.0,
            float(minimum_rvol),
        )

        self.minimum_adx = max(
            0.0,
            float(minimum_adx),
        )

        self.maximum_gap_percent = max(
            0.0,
            float(maximum_gap_percent),
        )

        self.maximum_orb_width_percent = max(
            0.0,
            float(maximum_orb_width_percent),
        )

        self.breakout_buffer_percent = max(
            0.0,
            float(breakout_buffer_percent),
        )

        # -------------------------------------------------
        # FILTER CONTROL
        # -------------------------------------------------

        self.require_volume = bool(
            require_volume
        )

        self.require_vwap = bool(
            require_vwap
        )

        self.require_adx = bool(
            require_adx
        )

        self.require_ema_alignment = bool(
            require_ema_alignment
        )

        self.allow_buy = bool(
            allow_buy
        )

        self.allow_sell = bool(
            allow_sell
        )

        self.max_signals = 25

    # =====================================================
    # MAIN SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Scan all supplied instruments for ORB setups.
        """

        results: List[Signal] = []

        for (
            instrument_key,
            data,
        ) in self._iter_market_data(
            market_data
        ):

            try:

                signal = self._scan_symbol(
                    instrument_key,
                    data,
                )

                if signal is None:
                    continue

                results.append(
                    signal
                )

            except Exception as exc:

                self.log(
                    "ORB symbol error:",
                    instrument_key,
                    repr(exc),
                )

        return results

    # =====================================================
    # MARKET DATA ITERATOR
    # =====================================================

    def _iter_market_data(
        self,
        market_data: Dict[str, Any],
    ) -> Iterable[
        Tuple[str, Dict[str, Any]]
    ]:
        """
        Normalize common StockVersity market-data
        container formats.
        """

        if not isinstance(
            market_data,
            dict,
        ):
            return

        # ---------------------------------------------
        # FORMAT:
        # {"symbols": {...}}
        # ---------------------------------------------

        symbols = market_data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            dict,
        ):

            for key, value in symbols.items():

                if isinstance(
                    value,
                    dict,
                ):

                    instrument_key = str(
                        _get(
                            value,
                            "instrument_key",
                            default=key,
                        )
                    )

                    yield (
                        instrument_key,
                        value,
                    )

            return

        # ---------------------------------------------
        # FORMAT:
        # {"data": {...}}
        # ---------------------------------------------

        data_block = market_data.get(
            "data"
        )

        if isinstance(
            data_block,
            dict,
        ):

            for key, value in data_block.items():

                if isinstance(
                    value,
                    dict,
                ):

                    instrument_key = str(
                        _get(
                            value,
                            "instrument_key",
                            default=key,
                        )
                    )

                    yield (
                        instrument_key,
                        value,
                    )

            return

        # ---------------------------------------------
        # DIRECT FORMAT
        # ---------------------------------------------

        for key, value in market_data.items():

            if not isinstance(
                value,
                dict,
            ):
                continue

            instrument_key = str(
                _get(
                    value,
                    "instrument_key",
                    default=key,
                )
            )

            yield (
                instrument_key,
                value,
            )

    # =====================================================
    # SCAN ONE SYMBOL
    # =====================================================

    def _scan_symbol(
        self,
        instrument_key: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:

        symbol = str(
            _get(
                data,
                "symbol",
                "trading_symbol",
                "tradingsymbol",
                default="",
            )
        ).upper().strip()

        if not symbol:
            return None

        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        last_price = _float(
            _get(
                data,
                "last_price",
                "ltp",
                "close",
                "close_price",
                default=0.0,
            )
        )

        open_price = _float(
            _get(
                data,
                "open_price",
                "open",
                default=0.0,
            )
        )

        high_price = _float(
            _get(
                data,
                "high_price",
                "high",
                default=0.0,
            )
        )

        low_price = _float(
            _get(
                data,
                "low_price",
                "low",
                default=0.0,
            )
        )

        previous_close = _float(
            _get(
                data,
                "previous_close",
                "prev_close",
                "cp",
                default=0.0,
            )
        )

        if last_price <= 0:
            return None

        # -------------------------------------------------
        # USER STOCK FILTER:
        # PRICE ABOVE ₹200
        # -------------------------------------------------

        if last_price < 200:
            return None

        # -------------------------------------------------
        # MARKET CAP FILTER:
        # > ₹1000 CRORE WHEN DATA EXISTS
        # -------------------------------------------------

        market_cap = _float(
            _get(
                data,
                "market_cap",
                "market_cap_cr",
                default=0.0,
            )
        )

        if (
            market_cap > 0
            and market_cap < 1000
        ):
            return None

        # -------------------------------------------------
        # GAP FILTER
        # -------------------------------------------------

        gap_percent = self._gap_percent(
            open_price,
            previous_close,
        )

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            return None

        # -------------------------------------------------
        # OPENING RANGE
        # -------------------------------------------------

        orb_high, orb_low = (
            self._opening_range(
                data
            )
        )

        if (
            orb_high <= 0
            or orb_low <= 0
            or orb_high <= orb_low
        ):
            return None

        orb_width_percent = (
            (
                orb_high
                - orb_low
            )
            / orb_low
            * 100.0
        )

        # Reject extremely wide ORB.
        if (
            orb_width_percent
            > self.maximum_orb_width_percent
        ):
            return None

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        volume = _int(
            _get(
                data,
                "volume",
                "total_volume",
                default=0,
            )
        )

        average_volume = _int(
            _get(
                data,
                "average_volume",
                "avg_volume",
                "volume_average",
                default=0,
            )
        )

        volume_ratio = _float(
            _get(
                data,
                "volume_ratio",
                "rvol",
                "relative_volume",
                default=0.0,
            )
        )

        if (
            volume_ratio <= 0
            and average_volume > 0
        ):

            volume_ratio = (
                volume
                / average_volume
            )

        # -------------------------------------------------
        # INDICATORS
        # -------------------------------------------------

        vwap = _float(
            _get(
                data,
                "vwap",
                default=0.0,
            )
        )

        ema9 = _float(
            _get(
                data,
                "ema9",
                "ema_9",
                default=0.0,
            )
        )

        ema20 = _float(
            _get(
                data,
                "ema20",
                "ema_20",
                default=0.0,
            )
        )

        ema21 = _float(
            _get(
                data,
                "ema21",
                "ema_21",
                default=0.0,
            )
        )

        ema50 = _float(
            _get(
                data,
                "ema50",
                "ema_50",
                default=0.0,
            )
        )

        ema200 = _float(
            _get(
                data,
                "ema200",
                "ema_200",
                default=0.0,
            )
        )

        rsi = _float(
            _get(
                data,
                "rsi",
                default=0.0,
            )
        )

        adx = _float(
            _get(
                data,
                "adx",
                default=0.0,
            )
        )

        plus_di = _float(
            _get(
                data,
                "plus_di",
                "di_plus",
                default=0.0,
            )
        )

        minus_di = _float(
            _get(
                data,
                "minus_di",
                "di_minus",
                default=0.0,
            )
        )

        atr = _float(
            _get(
                data,
                "atr",
                default=0.0,
            )
        )

        # -------------------------------------------------
        # BREAKOUT LEVELS
        # -------------------------------------------------

        bullish_trigger = (
            orb_high
            * (
                1.0
                + (
                    self.breakout_buffer_percent
                    / 100.0
                )
            )
        )

        bearish_trigger = (
            orb_low
            * (
                1.0
                - (
                    self.breakout_buffer_percent
                    / 100.0
                )
            )
        )

        bullish_breakout = (
            last_price
            > bullish_trigger
        )

        bearish_breakout = (
            last_price
            < bearish_trigger
        )

        if (
            not bullish_breakout
            and not bearish_breakout
        ):
            return None

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if (
            bullish_breakout
            and self.allow_buy
        ):

            return self._build_buy_signal(
                instrument_key=instrument_key,
                symbol=symbol,
                data=data,
                last_price=last_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                previous_close=previous_close,
                gap_percent=gap_percent,
                orb_high=orb_high,
                orb_low=orb_low,
                orb_width_percent=(
                    orb_width_percent
                ),
                volume=volume,
                average_volume=average_volume,
                volume_ratio=volume_ratio,
                vwap=vwap,
                ema9=ema9,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                adx=adx,
                plus_di=plus_di,
                minus_di=minus_di,
                atr=atr,
            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        if (
            bearish_breakout
            and self.allow_sell
        ):

            return self._build_sell_signal(
                instrument_key=instrument_key,
                symbol=symbol,
                data=data,
                last_price=last_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                previous_close=previous_close,
                gap_percent=gap_percent,
                orb_high=orb_high,
                orb_low=orb_low,
                orb_width_percent=(
                    orb_width_percent
                ),
                volume=volume,
                average_volume=average_volume,
                volume_ratio=volume_ratio,
                vwap=vwap,
                ema9=ema9,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                adx=adx,
                plus_di=plus_di,
                minus_di=minus_di,
                atr=atr,
            )

        return None

    # =====================================================
    # OPENING RANGE
    # =====================================================

    def _opening_range(
        self,
        data: Dict[str, Any],
    ) -> Tuple[float, float]:
        """
        Resolve ORB high and low.

        First preference:
            pre-calculated orb_high / orb_low.

        Second preference:
            opening_range dictionary.

        Third preference:
            candles.
        """

        orb_high = _float(
            _get(
                data,
                "orb_high",
                "opening_range_high",
                default=0.0,
            )
        )

        orb_low = _float(
            _get(
                data,
                "orb_low",
                "opening_range_low",
                default=0.0,
            )
        )

        if (
            orb_high > 0
            and orb_low > 0
        ):

            return (
                orb_high,
                orb_low,
            )

        opening_range = data.get(
            "opening_range"
        )

        if isinstance(
            opening_range,
            dict,
        ):

            orb_high = _float(
                _get(
                    opening_range,
                    "high",
                    "orb_high",
                    default=0.0,
                )
            )

            orb_low = _float(
                _get(
                    opening_range,
                    "low",
                    "orb_low",
                    default=0.0,
                )
            )

            if (
                orb_high > 0
                and orb_low > 0
            ):

                return (
                    orb_high,
                    orb_low,
                )

        candles = _get(
            data,
            "candles",
            "ohlc",
            default=None,
        )

        if not isinstance(
            candles,
            list,
        ):

            return (
                0.0,
                0.0,
            )

        opening_candles = (
            self._select_opening_candles(
                candles
            )
        )

        if not opening_candles:

            return (
                0.0,
                0.0,
            )

        highs: List[float] = []

        lows: List[float] = []

        for candle in opening_candles:

            high = self._candle_value(
                candle,
                "high",
                2,
            )

            low = self._candle_value(
                candle,
                "low",
                3,
            )

            if high > 0:
                highs.append(
                    high
                )

            if low > 0:
                lows.append(
                    low
                )

        if (
            not highs
            or not lows
        ):

            return (
                0.0,
                0.0,
            )

        return (
            max(highs),
            min(lows),
        )

    # =====================================================
    # SELECT OPENING CANDLES
    # =====================================================

    def _select_opening_candles(
        self,
        candles: List[Any],
    ) -> List[Any]:
        """
        Select candles required for opening range.

        If timestamps can be parsed, candles between
        09:15 and the ORB end time are used.

        Otherwise the first N candles are used.
        """

        selected: List[Any] = []

        for candle in candles:

            timestamp = (
                self._candle_timestamp(
                    candle
                )
            )

            if timestamp is None:
                continue

            minute_of_day = (
                timestamp.hour * 60
                + timestamp.minute
            )

            market_open = (
                9 * 60
                + 15
            )

            orb_end = (
                market_open
                + self.orb_minutes
            )

            if (
                market_open
                <= minute_of_day
                < orb_end
            ):

                selected.append(
                    candle
                )

        if selected:
            return selected

        # ---------------------------------------------
        # FALLBACK:
        # Assume candle order begins at market open.
        # ---------------------------------------------

        candle_minutes = (
            self._timeframe_minutes()
        )

        candle_count = max(
            1,
            self.orb_minutes
            // candle_minutes,
        )

        return candles[
            :candle_count
        ]

    # =====================================================
    # CANDLE TIMESTAMP
    # =====================================================

    def _candle_timestamp(
        self,
        candle: Any,
    ) -> Optional[datetime]:

        value: Any = None

        if isinstance(
            candle,
            dict,
        ):

            value = _get(
                candle,
                "timestamp",
                "time",
                "datetime",
                "candle_time",
                default=None,
            )

        elif isinstance(
            candle,
            (
                list,
                tuple,
            ),
        ):

            if candle:
                value = candle[0]

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value

        try:

            # Epoch milliseconds
            if isinstance(
                value,
                (
                    int,
                    float,
                ),
            ):

                timestamp = float(
                    value
                )

                if timestamp > 10_000_000_000:

                    timestamp /= 1000.0

                return datetime.fromtimestamp(
                    timestamp
                )

            text = str(
                value
            ).strip()

            if not text:
                return None

            text = text.replace(
                "Z",
                "+00:00",
            )

            return datetime.fromisoformat(
                text
            )

        except (
            TypeError,
            ValueError,
            OSError,
        ):

            return None

    # =====================================================
    # CANDLE VALUE
    # =====================================================

    @staticmethod
    def _candle_value(
        candle: Any,
        name: str,
        index: int,
    ) -> float:

        if isinstance(
            candle,
            dict,
        ):

            return _float(
                candle.get(
                    name,
                    0.0,
                )
            )

        if isinstance(
            candle,
            (
                list,
                tuple,
            ),
        ):

            if len(candle) > index:

                return _float(
                    candle[index]
                )

        return 0.0

    # =====================================================
    # TIMEFRAME MINUTES
    # =====================================================

    def _timeframe_minutes(
        self,
    ) -> int:

        timeframe = (
            self.timeframe
            .strip()
            .lower()
        )

        if timeframe.endswith(
            "m"
        ):

            try:

                return max(
                    1,
                    int(
                        timeframe[:-1]
                    ),
                )

            except ValueError:

                pass

        return 5

    # =====================================================
    # GAP
    # =====================================================

    @staticmethod
    def _gap_percent(
        open_price: float,
        previous_close: float,
    ) -> float:

        if (
            open_price <= 0
            or previous_close <= 0
        ):
            return 0.0

        return round(
            (
                (
                    open_price
                    - previous_close
                )
                / previous_close
            )
            * 100.0,
            2,
        )

    # =====================================================
    # BUY SIGNAL
    # =====================================================

    def _build_buy_signal(
        self,
        *,
        instrument_key: str,
        symbol: str,
        data: Dict[str, Any],
        last_price: float,
        open_price: float,
        high_price: float,
        low_price: float,
        previous_close: float,
        gap_percent: float,
        orb_high: float,
        orb_low: float,
        orb_width_percent: float,
        volume: int,
        average_volume: int,
        volume_ratio: float,
        vwap: float,
        ema9: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        atr: float,
    ) -> Optional[Signal]:

        # -------------------------------------------------
        # HARD CONFIRMATION FILTERS
        # -------------------------------------------------

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio
            < self.minimum_rvol
        ):
            return None

        if (
            self.require_vwap
            and vwap > 0
            and last_price <= vwap
        ):
            return None

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            return None

        if (
            plus_di > 0
            and minus_di > 0
            and plus_di <= minus_di
        ):
            return None

        if (
            self.require_ema_alignment
            and not self._bullish_ema_alignment(
                last_price,
                ema20,
                ema21,
                ema50,
                ema200,
            )
        ):
            return None

        # -------------------------------------------------
        # ENTRY
        # -------------------------------------------------

        entry = max(
            last_price,
            orb_high,
        )

        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        stop_loss = self._buy_stop(
            entry=entry,
            orb_high=orb_high,
            orb_low=orb_low,
            vwap=vwap,
            atr=atr,
        )

        risk = (
            entry
            - stop_loss
        )

        if risk <= 0:
            return None

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        target1 = (
            entry
            + (
                risk
                * self.minimum_rr
            )
        )

        target2 = (
            entry
            + (
                risk
                * 3.0
            )
        )

        target3 = (
            entry
            + (
                risk
                * 4.0
            )
        )

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        (
            score,
            confidence,
            breakdown,
        ) = self._score_buy(
            last_price=last_price,
            orb_high=orb_high,
            volume_ratio=volume_ratio,
            vwap=vwap,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            orb_width_percent=(
                orb_width_percent
            ),
        )

        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None

        sector = str(
            _get(
                data,
                "sector",
                default="",
            )
        )

        market_trend = (
            self._resolve_market_trend(
                data
            )
        )

        strength = (
            self._resolve_strength(
                score
            )
        )

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=SignalType.BUY,
            pattern=PatternType.ORB,
            strength=strength,
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name=(
                "Opening Range Breakout"
            ),
            timeframe=self.timeframe,
            market_trend=market_trend,
            sector=sector,
            last_price=last_price,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=last_price,
            previous_close=previous_close,
            gap_percent=gap_percent,
            volume=volume,
            average_volume=average_volume,
            volume_ratio=round(
                volume_ratio,
                2,
            ),
            trigger_price=orb_high,
            entry=round(
                entry,
                2,
            ),
            stop_loss=round(
                stop_loss,
                2,
            ),
            target1=round(
                target1,
                2,
            ),
            target2=round(
                target2,
                2,
            ),
            target3=round(
                target3,
                2,
            ),
            atr=atr,
            ema9=ema9,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            vwap=vwap,
            confidence=confidence,
            score=score,
            score_breakdown=breakdown,
            remarks=(
                "Bullish opening-range breakout"
            ),
            tags=[
                "ORB",
                "INTRADAY",
                "BREAKOUT",
                "BUY",
            ],
            metadata={
                "orb_high": orb_high,
                "orb_low": orb_low,
                "orb_width_percent": round(
                    orb_width_percent,
                    2,
                ),
                "market_cap": _float(
                    _get(
                        data,
                        "market_cap",
                        "market_cap_cr",
                        default=0.0,
                    )
                ),
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # SELL SIGNAL
    # =====================================================

    def _build_sell_signal(
        self,
        *,
        instrument_key: str,
        symbol: str,
        data: Dict[str, Any],
        last_price: float,
        open_price: float,
        high_price: float,
        low_price: float,
        previous_close: float,
        gap_percent: float,
        orb_high: float,
        orb_low: float,
        orb_width_percent: float,
        volume: int,
        average_volume: int,
        volume_ratio: float,
        vwap: float,
        ema9: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        atr: float,
    ) -> Optional[Signal]:

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio
            < self.minimum_rvol
        ):
            return None

        if (
            self.require_vwap
            and vwap > 0
            and last_price >= vwap
        ):
            return None

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            return None

        if (
            plus_di > 0
            and minus_di > 0
            and minus_di <= plus_di
        ):
            return None

        if (
            self.require_ema_alignment
            and not self._bearish_ema_alignment(
                last_price,
                ema20,
                ema21,
                ema50,
                ema200,
            )
        ):
            return None

        entry = min(
            last_price,
            orb_low,
        )

        stop_loss = self._sell_stop(
            entry=entry,
            orb_high=orb_high,
            orb_low=orb_low,
            vwap=vwap,
            atr=atr,
        )

        risk = (
            stop_loss
            - entry
        )

        if risk <= 0:
            return None

        target1 = (
            entry
            - (
                risk
                * self.minimum_rr
            )
        )

        target2 = (
            entry
            - (
                risk
                * 3.0
            )
        )

        target3 = (
            entry
            - (
                risk
                * 4.0
            )
        )

        if target1 <= 0:
            return None

        (
            score,
            confidence,
            breakdown,
        ) = self._score_sell(
            last_price=last_price,
            orb_low=orb_low,
            volume_ratio=volume_ratio,
            vwap=vwap,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            orb_width_percent=(
                orb_width_percent
            ),
        )

        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None

        sector = str(
            _get(
                data,
                "sector",
                default="",
            )
        )

        market_trend = (
            self._resolve_market_trend(
                data
            )
        )

        strength = (
            self._resolve_strength(
                score
            )
        )

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=SignalType.SELL,
            pattern=PatternType.ORB,
            strength=strength,
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name=(
                "Opening Range Breakdown"
            ),
            timeframe=self.timeframe,
            market_trend=market_trend,
            sector=sector,
            last_price=last_price,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=last_price,
            previous_close=previous_close,
            gap_percent=gap_percent,
            volume=volume,
            average_volume=average_volume,
            volume_ratio=round(
                volume_ratio,
                2,
            ),
            trigger_price=orb_low,
            entry=round(
                entry,
                2,
            ),
            stop_loss=round(
                stop_loss,
                2,
            ),
            target1=round(
                target1,
                2,
            ),
            target2=round(
                max(
                    target2,
                    0.01,
                ),
                2,
            ),
            target3=round(
                max(
                    target3,
                    0.01,
                ),
                2,
            ),
            atr=atr,
            ema9=ema9,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            vwap=vwap,
            confidence=confidence,
            score=score,
            score_breakdown=breakdown,
            remarks=(
                "Bearish opening-range breakdown"
            ),
            tags=[
                "ORB",
                "INTRADAY",
                "BREAKDOWN",
                "SELL",
            ],
            metadata={
                "orb_high": orb_high,
                "orb_low": orb_low,
                "orb_width_percent": round(
                    orb_width_percent,
                    2,
                ),
                "market_cap": _float(
                    _get(
                        data,
                        "market_cap",
                        "market_cap_cr",
                        default=0.0,
                    )
                ),
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # BUY STOP
    # =====================================================

    @staticmethod
    def _buy_stop(
        *,
        entry: float,
        orb_high: float,
        orb_low: float,
        vwap: float,
        atr: float,
    ) -> float:

        candidates: List[float] = []

        # ORB breakout retest area.
        if orb_high > 0:
            candidates.append(
                orb_high
            )

        # VWAP can provide tighter structural SL.
        if (
            vwap > 0
            and vwap < entry
        ):
            candidates.append(
                vwap
            )

        # ATR stop.
        if atr > 0:

            atr_stop = (
                entry
                - atr
            )

            if atr_stop > 0:
                candidates.append(
                    atr_stop
                )

        if candidates:

            stop = max(
                value
                for value in candidates
                if value < entry
            ) if any(
                value < entry
                for value in candidates
            ) else 0.0

            if stop > 0:
                return stop

        return orb_low

    # =====================================================
    # SELL STOP
    # =====================================================

    @staticmethod
    def _sell_stop(
        *,
        entry: float,
        orb_high: float,
        orb_low: float,
        vwap: float,
        atr: float,
    ) -> float:

        candidates: List[float] = []

        if orb_low > entry:
            candidates.append(
                orb_low
            )

        if (
            vwap > entry
        ):
            candidates.append(
                vwap
            )

        if atr > 0:

            candidates.append(
                entry + atr
            )

        valid = [
            value
            for value in candidates
            if value > entry
        ]

        if valid:

            return min(
                valid
            )

        return orb_high

    # =====================================================
    # BULLISH EMA ALIGNMENT
    # =====================================================

    @staticmethod
    def _bullish_ema_alignment(
        price: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
    ) -> bool:

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if (
            short_ema > 0
            and price < short_ema
        ):
            return False

        if (
            short_ema > 0
            and ema50 > 0
            and short_ema < ema50
        ):
            return False

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 < ema200
        ):
            return False

        return True

    # =====================================================
    # BEARISH EMA ALIGNMENT
    # =====================================================

    @staticmethod
    def _bearish_ema_alignment(
        price: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
    ) -> bool:

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if (
            short_ema > 0
            and price > short_ema
        ):
            return False

        if (
            short_ema > 0
            and ema50 > 0
            and short_ema > ema50
        ):
            return False

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            return False

        return True

    # =====================================================
    # BUY SCORE
    # =====================================================

    def _score_buy(
        self,
        *,
        last_price: float,
        orb_high: float,
        volume_ratio: float,
        vwap: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        orb_width_percent: float,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        trend = 0.0
        volume = 0.0
        momentum = 0.0
        pattern = 0.0
        sector = 0.0
        relative_strength = 0.0
        market = 0.0

        # ---------------------------------------------
        # PATTERN : 25
        # ---------------------------------------------

        if last_price > orb_high:
            pattern += 18.0

        if (
            0.25
            <= orb_width_percent
            <= 2.5
        ):
            pattern += 7.0

        # ---------------------------------------------
        # VOLUME : 20
        # ---------------------------------------------

        if volume_ratio >= 3.0:
            volume = 20.0

        elif volume_ratio >= 2.0:
            volume = 17.0

        elif volume_ratio >= 1.5:
            volume = 14.0

        elif volume_ratio > 0:
            volume = 7.0

        # ---------------------------------------------
        # TREND : 20
        # ---------------------------------------------

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if (
            short_ema > 0
            and last_price > short_ema
        ):
            trend += 7.0

        if (
            short_ema > 0
            and ema50 > 0
            and short_ema > ema50
        ):
            trend += 6.0

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            trend += 7.0

        # ---------------------------------------------
        # MOMENTUM : 15
        # ---------------------------------------------

        if 55 <= rsi <= 75:
            momentum += 6.0

        elif rsi > 50:
            momentum += 3.0

        if adx >= 30:
            momentum += 5.0

        elif adx >= 20:
            momentum += 3.0

        if (
            plus_di > minus_di
            and plus_di > 0
        ):
            momentum += 4.0

        # ---------------------------------------------
        # VWAP / MARKET : 10
        # ---------------------------------------------

        if (
            vwap > 0
            and last_price > vwap
        ):
            market = 10.0

        # ---------------------------------------------
        # RELATIVE STRENGTH PLACEHOLDER : 5
        # ---------------------------------------------

        relative_strength = 5.0

        # ---------------------------------------------
        # SECTOR PLACEHOLDER : 5
        # ---------------------------------------------

        sector = 5.0

        score = (
            trend
            + volume
            + momentum
            + pattern
            + sector
            + relative_strength
            + market
        )

        score = round(
            min(
                score,
                100.0,
            ),
            2,
        )

        confidence = self._confidence(
            score=score,
            volume_ratio=volume_ratio,
            adx=adx,
            vwap_confirmed=(
                vwap <= 0
                or last_price > vwap
            ),
        )

        breakdown = {
            "trend": round(
                trend,
                2,
            ),
            "volume": round(
                volume,
                2,
            ),
            "momentum": round(
                momentum,
                2,
            ),
            "pattern": round(
                pattern,
                2,
            ),
            "sector": round(
                sector,
                2,
            ),
            "relative_strength": round(
                relative_strength,
                2,
            ),
            "market": round(
                market,
                2,
            ),
        }

        return (
            score,
            confidence,
            breakdown,
        )

    # =====================================================
    # SELL SCORE
    # =====================================================

    def _score_sell(
        self,
        *,
        last_price: float,
        orb_low: float,
        volume_ratio: float,
        vwap: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        orb_width_percent: float,
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        trend = 0.0
        volume = 0.0
        momentum = 0.0
        pattern = 0.0
        sector = 0.0
        relative_strength = 0.0
        market = 0.0

        if last_price < orb_low:
            pattern += 18.0

        if (
            0.25
            <= orb_width_percent
            <= 2.5
        ):
            pattern += 7.0

        if volume_ratio >= 3.0:
            volume = 20.0

        elif volume_ratio >= 2.0:
            volume = 17.0

        elif volume_ratio >= 1.5:
            volume = 14.0

        elif volume_ratio > 0:
            volume = 7.0

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if (
            short_ema > 0
            and last_price < short_ema
        ):
            trend += 7.0

        if (
            short_ema > 0
            and ema50 > 0
            and short_ema < ema50
        ):
            trend += 6.0

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 < ema200
        ):
            trend += 7.0

        if 25 <= rsi <= 45:
            momentum += 6.0

        elif (
            rsi > 0
            and rsi < 50
        ):
            momentum += 3.0

        if adx >= 30:
            momentum += 5.0

        elif adx >= 20:
            momentum += 3.0

        if (
            minus_di > plus_di
            and minus_di > 0
        ):
            momentum += 4.0

        if (
            vwap > 0
            and last_price < vwap
        ):
            market = 10.0

        relative_strength = 5.0

        sector = 5.0

        score = (
            trend
            + volume
            + momentum
            + pattern
            + sector
            + relative_strength
            + market
        )

        score = round(
            min(
                score,
                100.0,
            ),
            2,
        )

        confidence = self._confidence(
            score=score,
            volume_ratio=volume_ratio,
            adx=adx,
            vwap_confirmed=(
                vwap <= 0
                or last_price < vwap
            ),
        )

        breakdown = {
            "trend": round(
                trend,
                2,
            ),
            "volume": round(
                volume,
                2,
            ),
            "momentum": round(
                momentum,
                2,
            ),
            "pattern": round(
                pattern,
                2,
            ),
            "sector": round(
                sector,
                2,
            ),
            "relative_strength": round(
                relative_strength,
                2,
            ),
            "market": round(
                market,
                2,
            ),
        }

        return (
            score,
            confidence,
            breakdown,
        )

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _confidence(
        *,
        score: float,
        volume_ratio: float,
        adx: float,
        vwap_confirmed: bool,
    ) -> float:

        confidence = (
            score * 0.70
        )

        if volume_ratio >= 2.0:
            confidence += 10.0

        elif volume_ratio >= 1.5:
            confidence += 6.0

        if adx >= 30:
            confidence += 10.0

        elif adx >= 20:
            confidence += 6.0

        if vwap_confirmed:
            confidence += 10.0

        return round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

    # =====================================================
    # MARKET TREND
    # =====================================================

    @staticmethod
    def _resolve_market_trend(
        data: Dict[str, Any],
    ) -> MarketTrend:

        value = _get(
            data,
            "market_trend",
            "trend",
            default="SIDEWAYS",
        )

        if isinstance(
            value,
            MarketTrend,
        ):
            return value

        text = str(
            value
        ).upper().strip()

        mapping = {
            "STRONG_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "BULLISH":
                MarketTrend.BULLISH,

            "UP":
                MarketTrend.BULLISH,

            "SIDEWAYS":
                MarketTrend.SIDEWAYS,

            "NEUTRAL":
                MarketTrend.SIDEWAYS,

            "BEARISH":
                MarketTrend.BEARISH,

            "DOWN":
                MarketTrend.BEARISH,

            "STRONG_BEARISH":
                MarketTrend.STRONG_BEARISH,
        }

        return mapping.get(
            text,
            MarketTrend.SIDEWAYS,
        )

    # =====================================================
    # SIGNAL STRENGTH
    # =====================================================

    @staticmethod
    def _resolve_strength(
        score: float,
    ) -> SignalStrength:

        if score >= 90:
            return (
                SignalStrength.VERY_STRONG
            )

        if score >= 80:
            return (
                SignalStrength.STRONG
            )

        if score >= 70:
            return (
                SignalStrength.MODERATE
            )

        if score >= 60:
            return (
                SignalStrength.WEAK
            )

        return (
            SignalStrength.VERY_WEAK
        )

    # =====================================================
    # INFO
    # =====================================================

    def info(
        self,
    ) -> Dict[str, Any]:

        return {
            "scanner": self.name,
            "version": self.version,
            "timeframe": self.timeframe,
            "orb_minutes": self.orb_minutes,
            "minimum_score": (
                self.minimum_score
            ),
            "minimum_confidence": (
                self.minimum_confidence
            ),
            "minimum_rr": (
                self.minimum_rr
            ),
            "minimum_rvol": (
                self.minimum_rvol
            ),
            "minimum_adx": (
                self.minimum_adx
            ),
            "maximum_gap_percent": (
                self.maximum_gap_percent
            ),
            "maximum_orb_width_percent": (
                self.maximum_orb_width_percent
            ),
            "allow_buy": self.allow_buy,
            "allow_sell": self.allow_sell,
        }


# =========================================================
# FACTORY
# =========================================================

def create_orb_scanner(
    **kwargs: Any,
) -> ORBScanner:
    """
    Create configured ORB scanner.
    """

    return ORBScanner(
        **kwargs
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "ORBScanner",
    "create_orb_scanner",
]


# =========================================================
# END OF FILE
# =========================================================
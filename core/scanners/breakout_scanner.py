"""
=========================================================
StockVersity Scanner Pro
Breakout Scanner
Version : 2.1
=========================================================

File:
    core/scanners/breakout_scanner.py

Purpose
-------
Detect high-quality bullish breakouts and bearish
breakdowns for StockVersity Scanner Pro.

Core Filters
------------
• Price >= ₹200
• Market cap >= ₹1000 Cr when available
• Gap <= ±3%
• Breakout / breakdown confirmation
• Relative volume confirmation
• ADX confirmation
• VWAP confirmation
• EMA trend confirmation
• RSI confirmation
• MACD confirmation
• Market trend alignment
• Sector strength
• ATR-based stop loss
• Minimum 1:2 risk/reward
• Institutional-style scoring
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

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

SCANNER_NAME = "BreakoutScanner"

SCANNER_VERSION = "2.1"

DEFAULT_TIMEFRAME = "15m"

DEFAULT_MINIMUM_PRICE = 200.0

DEFAULT_MINIMUM_MARKET_CAP = 1000.0

DEFAULT_MAXIMUM_GAP = 3.0

DEFAULT_MINIMUM_RVOL = 1.5

DEFAULT_MINIMUM_ADX = 20.0

DEFAULT_MINIMUM_SCORE = 70.0

DEFAULT_MINIMUM_CONFIDENCE = 65.0

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_BREAKOUT_BUFFER_PERCENT = 0.10


# =========================================================
# HELPERS
# =========================================================

def _float(
    value: Any,
    default: float = 0.0,
) -> float:

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

    for key in keys:

        if key not in data:
            continue

        value = data.get(key)

        if value is not None:
            return value

    return default


# =========================================================
# BREAKOUT SCANNER
# =========================================================

class BreakoutScanner(BaseScanner):
    """
    Detect bullish breakouts and bearish breakdowns.

    Supported breakout references may include:

        resistance
        resistance_level
        breakout_level
        previous_high
        prev_high
        day_high
        range_high

    Supported breakdown references may include:

        support
        support_level
        breakdown_level
        previous_low
        prev_low
        day_low
        range_low
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        timeframe: str = DEFAULT_TIMEFRAME,
        minimum_price: float = DEFAULT_MINIMUM_PRICE,
        minimum_market_cap: float = (
            DEFAULT_MINIMUM_MARKET_CAP
        ),
        maximum_gap_percent: float = (
            DEFAULT_MAXIMUM_GAP
        ),
        minimum_rvol: float = DEFAULT_MINIMUM_RVOL,
        minimum_adx: float = DEFAULT_MINIMUM_ADX,
        minimum_score: float = DEFAULT_MINIMUM_SCORE,
        minimum_confidence: float = (
            DEFAULT_MINIMUM_CONFIDENCE
        ),
        minimum_rr: float = DEFAULT_MINIMUM_RR,
        breakout_buffer_percent: float = (
            DEFAULT_BREAKOUT_BUFFER_PERCENT
        ),
        require_volume: bool = True,
        require_adx: bool = True,
        require_vwap: bool = True,
        allow_buy: bool = True,
        allow_sell: bool = True,
    ) -> None:

        super().__init__(
            name=SCANNER_NAME,
            version=SCANNER_VERSION,
            timeframe=timeframe,
        )

        self.minimum_price = max(
            0.0,
            float(minimum_price),
        )

        self.minimum_market_cap = max(
            0.0,
            float(minimum_market_cap),
        )

        self.maximum_gap_percent = max(
            0.0,
            float(maximum_gap_percent),
        )

        self.minimum_rvol = max(
            0.0,
            float(minimum_rvol),
        )

        self.minimum_adx = max(
            0.0,
            float(minimum_adx),
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

        self.breakout_buffer_percent = max(
            0.0,
            float(
                breakout_buffer_percent
            ),
        )

        self.require_volume = bool(
            require_volume
        )

        self.require_adx = bool(
            require_adx
        )

        self.require_vwap = bool(
            require_vwap
        )

        self.allow_buy = bool(
            allow_buy
        )

        self.allow_sell = bool(
            allow_sell
        )

        self.max_signals = 25

    # =====================================================
    # SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

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

                if signal is not None:

                    results.append(
                        signal
                    )

            except Exception as exc:

                self.log(
                    "Breakout scan error:",
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

        if not isinstance(
            market_data,
            dict,
        ):
            return

        symbols = market_data.get(
            "symbols"
        )

        if isinstance(
            symbols,
            dict,
        ):

            for key, value in symbols.items():

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

            return

        block = market_data.get(
            "data"
        )

        if isinstance(
            block,
            dict,
        ):

            for key, value in block.items():

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

            return

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
    # SCAN SYMBOL
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

        if not instrument_key:
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
                default=0.0,
            )
        )

        if (
            last_price
            < self.minimum_price
        ):
            return None

        # -------------------------------------------------
        # MARKET CAP
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
            and market_cap
            < self.minimum_market_cap
        ):
            return None

        # -------------------------------------------------
        # GAP
        # -------------------------------------------------

        gap_percent = (
            self._calculate_gap(
                open_price,
                previous_close,
            )
        )

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
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

        macd = _float(
            _get(
                data,
                "macd",
                default=0.0,
            )
        )

        macd_signal = _float(
            _get(
                data,
                "macd_signal",
                default=0.0,
            )
        )

        macd_histogram = _float(
            _get(
                data,
                "macd_histogram",
                "macd_hist",
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

        vwap = _float(
            _get(
                data,
                "vwap",
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
        # LEVELS
        # -------------------------------------------------

        resistance = self._resistance_level(
            data
        )

        support = self._support_level(
            data
        )

        bullish_breakout = (
            self._is_bullish_breakout(
                price=last_price,
                resistance=resistance,
                volume_ratio=volume_ratio,
                adx=adx,
                vwap=vwap,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                macd_histogram=macd_histogram,
                plus_di=plus_di,
                minus_di=minus_di,
            )
        )

        bearish_breakdown = (
            self._is_bearish_breakdown(
                price=last_price,
                support=support,
                volume_ratio=volume_ratio,
                adx=adx,
                vwap=vwap,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                macd_histogram=macd_histogram,
                plus_di=plus_di,
                minus_di=minus_di,
            )
        )

        # -------------------------------------------------
        # BUY
        # -------------------------------------------------

        if (
            bullish_breakout
            and self.allow_buy
        ):

            return self._build_signal(
                instrument_key=instrument_key,
                symbol=symbol,
                data=data,
                signal_type=SignalType.BUY,
                pattern=PatternType.BREAKOUT,
                breakout_level=resistance,
                last_price=last_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                previous_close=previous_close,
                gap_percent=gap_percent,
                volume=volume,
                average_volume=average_volume,
                volume_ratio=volume_ratio,
                ema9=ema9,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                macd_histogram=macd_histogram,
                adx=adx,
                plus_di=plus_di,
                minus_di=minus_di,
                vwap=vwap,
                atr=atr,
                market_cap=market_cap,
            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        if (
            bearish_breakdown
            and self.allow_sell
        ):

            return self._build_signal(
                instrument_key=instrument_key,
                symbol=symbol,
                data=data,
                signal_type=SignalType.SELL,
                pattern=PatternType.BREAKDOWN,
                breakout_level=support,
                last_price=last_price,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                previous_close=previous_close,
                gap_percent=gap_percent,
                volume=volume,
                average_volume=average_volume,
                volume_ratio=volume_ratio,
                ema9=ema9,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                macd=macd,
                macd_signal=macd_signal,
                macd_histogram=macd_histogram,
                adx=adx,
                plus_di=plus_di,
                minus_di=minus_di,
                vwap=vwap,
                atr=atr,
                market_cap=market_cap,
            )

        return None

    # =====================================================
    # RESISTANCE LEVEL
    # =====================================================

    @staticmethod
    def _resistance_level(
        data: Dict[str, Any],
    ) -> float:

        return _float(
            _get(
                data,
                "resistance",
                "resistance_level",
                "breakout_level",
                "previous_high",
                "prev_high",
                "range_high",
                "opening_range_high",
                default=0.0,
            )
        )

    # =====================================================
    # SUPPORT LEVEL
    # =====================================================

    @staticmethod
    def _support_level(
        data: Dict[str, Any],
    ) -> float:

        return _float(
            _get(
                data,
                "support",
                "support_level",
                "breakdown_level",
                "previous_low",
                "prev_low",
                "range_low",
                "opening_range_low",
                default=0.0,
            )
        )

    # =====================================================
    # BULLISH BREAKOUT
    # =====================================================

    def _is_bullish_breakout(
        self,
        *,
        price: float,
        resistance: float,
        volume_ratio: float,
        adx: float,
        vwap: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        plus_di: float,
        minus_di: float,
    ) -> bool:

        if (
            resistance <= 0
            or price <= 0
        ):
            return False

        trigger = (
            resistance
            * (
                1.0
                + self.breakout_buffer_percent
                / 100.0
            )
        )

        if price < trigger:
            return False

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio
            < self.minimum_rvol
        ):
            return False

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            return False

        if (
            self.require_vwap
            and vwap > 0
            and price <= vwap
        ):
            return False

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
            ema50 > 0
            and ema200 > 0
            and ema50 < ema200
        ):
            return False

        if (
            rsi > 0
            and rsi < 55
        ):
            return False

        if rsi > 85:
            return False

        if (
            plus_di > 0
            and minus_di > 0
            and plus_di <= minus_di
        ):
            return False

        if (
            macd != 0
            or macd_signal != 0
        ):

            if macd <= macd_signal:
                return False

        if (
            macd_histogram != 0
            and macd_histogram < 0
        ):
            return False

        return True

    # =====================================================
    # BEARISH BREAKDOWN
    # =====================================================

    def _is_bearish_breakdown(
        self,
        *,
        price: float,
        support: float,
        volume_ratio: float,
        adx: float,
        vwap: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        plus_di: float,
        minus_di: float,
    ) -> bool:

        if (
            support <= 0
            or price <= 0
        ):
            return False

        trigger = (
            support
            * (
                1.0
                - self.breakout_buffer_percent
                / 100.0
            )
        )

        if price > trigger:
            return False

        if (
            self.require_volume
            and volume_ratio > 0
            and volume_ratio
            < self.minimum_rvol
        ):
            return False

        if (
            self.require_adx
            and adx > 0
            and adx < self.minimum_adx
        ):
            return False

        if (
            self.require_vwap
            and vwap > 0
            and price >= vwap
        ):
            return False

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
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            return False

        if (
            rsi > 0
            and rsi > 45
        ):
            return False

        if (
            rsi > 0
            and rsi < 15
        ):
            return False

        if (
            plus_di > 0
            and minus_di > 0
            and minus_di <= plus_di
        ):
            return False

        if (
            macd != 0
            or macd_signal != 0
        ):

            if macd >= macd_signal:
                return False

        if (
            macd_histogram != 0
            and macd_histogram > 0
        ):
            return False

        return True

    # =====================================================
    # BUILD SIGNAL
    # =====================================================

    def _build_signal(
        self,
        *,
        instrument_key: str,
        symbol: str,
        data: Dict[str, Any],
        signal_type: SignalType,
        pattern: PatternType,
        breakout_level: float,
        last_price: float,
        open_price: float,
        high_price: float,
        low_price: float,
        previous_close: float,
        gap_percent: float,
        volume: int,
        average_volume: int,
        volume_ratio: float,
        ema9: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        vwap: float,
        atr: float,
        market_cap: float,
    ) -> Optional[Signal]:

        (
            score,
            confidence,
            score_breakdown,
        ) = self._calculate_score(
            signal_type=signal_type,
            price=last_price,
            breakout_level=breakout_level,
            volume_ratio=volume_ratio,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            vwap=vwap,
            data=data,
        )

        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None

        entry = last_price

        stop_loss = self._calculate_stop_loss(
            signal_type=signal_type,
            entry=entry,
            breakout_level=breakout_level,
            low_price=low_price,
            high_price=high_price,
            ema20=ema20,
            ema21=ema21,
            atr=atr,
        )

        if stop_loss <= 0:
            return None

        if signal_type == SignalType.BUY:

            risk = (
                entry
                - stop_loss
            )

        else:

            risk = (
                stop_loss
                - entry
            )

        if risk <= 0:
            return None

        if signal_type == SignalType.BUY:

            target1 = (
                entry
                + risk * self.minimum_rr
            )

            target2 = (
                entry
                + risk * 3.0
            )

            target3 = (
                entry
                + risk * 4.0
            )

        else:

            target1 = (
                entry
                - risk * self.minimum_rr
            )

            target2 = (
                entry
                - risk * 3.0
            )

            target3 = (
                entry
                - risk * 4.0
            )

            if target1 <= 0:
                return None

            target2 = max(
                target2,
                0.01,
            )

            target3 = max(
                target3,
                0.01,
            )

        market_trend = (
            self._market_trend(
                data
            )
        )

        sector = str(
            _get(
                data,
                "sector",
                default="",
            )
        )

        sector_strength = _float(
            _get(
                data,
                "sector_strength",
                default=0.0,
            )
        )

        relative_strength = _float(
            _get(
                data,
                "relative_strength",
                "rs",
                default=0.0,
            )
        )

        strength = self._strength(
            score
        )

        if signal_type == SignalType.BUY:

            remarks = (
                "Bullish breakout above "
                f"{breakout_level:.2f}"
            )

        else:

            remarks = (
                "Bearish breakdown below "
                f"{breakout_level:.2f}"
            )

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=signal_type,
            pattern=pattern,
            strength=strength,
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name=(
                "Breakout / Breakdown"
            ),
            timeframe=self.timeframe,
            market_trend=market_trend,
            sector=sector,
            sector_strength=sector_strength,
            relative_strength=(
                relative_strength
            ),
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
            trigger_price=round(
                breakout_level,
                2,
            ),
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
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=(
                macd_histogram
            ),
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            vwap=vwap,
            confidence=confidence,
            score=score,
            score_breakdown=(
                score_breakdown
            ),
            remarks=remarks,
            tags=[
                pattern.value,
                "BREAKOUT",
                signal_type.value,
            ],
            metadata={
                "breakout_level":
                    breakout_level,

                "market_cap":
                    market_cap,

                "minimum_rvol":
                    self.minimum_rvol,

                "minimum_adx":
                    self.minimum_adx,
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # STOP LOSS
    # =====================================================

    @staticmethod
    def _calculate_stop_loss(
        *,
        signal_type: SignalType,
        entry: float,
        breakout_level: float,
        low_price: float,
        high_price: float,
        ema20: float,
        ema21: float,
        atr: float,
    ) -> float:

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        candidates: List[float] = []

        if signal_type == SignalType.BUY:

            if (
                breakout_level > 0
                and breakout_level < entry
            ):

                candidates.append(
                    breakout_level
                )

            if (
                low_price > 0
                and low_price < entry
            ):

                candidates.append(
                    low_price
                )

            if (
                short_ema > 0
                and short_ema < entry
            ):

                candidates.append(
                    short_ema
                )

            if atr > 0:

                atr_stop = (
                    entry
                    - atr
                )

                if atr_stop > 0:

                    candidates.append(
                        atr_stop
                    )

            if not candidates:
                return 0.0

            return max(
                candidates
            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        if (
            breakout_level > entry
        ):

            candidates.append(
                breakout_level
            )

        if (
            high_price > entry
        ):

            candidates.append(
                high_price
            )

        if (
            short_ema > entry
        ):

            candidates.append(
                short_ema
            )

        if atr > 0:

            candidates.append(
                entry + atr
            )

        if not candidates:
            return 0.0

        return min(
            candidates
        )

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        *,
        signal_type: SignalType,
        price: float,
        breakout_level: float,
        volume_ratio: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        macd_histogram: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        vwap: float,
        data: Dict[str, Any],
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

        bullish = (
            signal_type
            == SignalType.BUY
        )

        trend = 0.0

        volume_score = 0.0

        momentum = 0.0

        pattern_score = 0.0

        sector_score = 0.0

        relative_strength_score = 0.0

        market_score = 0.0

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        # -------------------------------------------------
        # TREND : 20
        # -------------------------------------------------

        if bullish:

            if (
                short_ema > 0
                and price > short_ema
            ):
                trend += 7

            if (
                ema50 > 0
                and price > ema50
            ):
                trend += 6

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 > ema200
            ):
                trend += 7

        else:

            if (
                short_ema > 0
                and price < short_ema
            ):
                trend += 7

            if (
                ema50 > 0
                and price < ema50
            ):
                trend += 6

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 < ema200
            ):
                trend += 7

        # -------------------------------------------------
        # VOLUME : 20
        # -------------------------------------------------

        if volume_ratio >= 3.0:
            volume_score = 20

        elif volume_ratio >= 2.0:
            volume_score = 17

        elif volume_ratio >= 1.5:
            volume_score = 14

        elif volume_ratio >= 1.2:
            volume_score = 9

        elif volume_ratio > 0:
            volume_score = 5

        # -------------------------------------------------
        # MOMENTUM : 20
        # -------------------------------------------------

        if bullish:

            if 60 <= rsi <= 75:
                momentum += 7

            elif 55 <= rsi < 60:
                momentum += 4

            if macd > macd_signal:
                momentum += 4

            if macd_histogram > 0:
                momentum += 2

            if adx >= 30:
                momentum += 4

            elif adx >= 20:
                momentum += 2

            if (
                plus_di > minus_di
                and plus_di > 0
            ):
                momentum += 3

        else:

            if 25 <= rsi <= 40:
                momentum += 7

            elif 40 < rsi <= 45:
                momentum += 4

            if macd < macd_signal:
                momentum += 4

            if macd_histogram < 0:
                momentum += 2

            if adx >= 30:
                momentum += 4

            elif adx >= 20:
                momentum += 2

            if (
                minus_di > plus_di
                and minus_di > 0
            ):
                momentum += 3

        momentum = min(
            momentum,
            20.0,
        )

        # -------------------------------------------------
        # BREAKOUT QUALITY : 15
        # -------------------------------------------------

        if breakout_level > 0:

            distance = abs(
                (
                    price
                    - breakout_level
                )
                / breakout_level
                * 100
            )

            if (
                self.breakout_buffer_percent
                <= distance
                <= 1.0
            ):
                pattern_score = 15

            elif distance <= 2.0:
                pattern_score = 12

            elif distance <= 3.0:
                pattern_score = 8

            else:
                pattern_score = 5

        # -------------------------------------------------
        # SECTOR : 10
        # -------------------------------------------------

        sector_strength = _float(
            _get(
                data,
                "sector_strength",
                default=0.0,
            )
        )

        if bullish:

            if sector_strength >= 70:
                sector_score = 10

            elif sector_strength >= 55:
                sector_score = 7

            elif sector_strength > 0:
                sector_score = 4

        else:

            if sector_strength <= -70:
                sector_score = 10

            elif sector_strength <= -55:
                sector_score = 7

            elif sector_strength < 0:
                sector_score = 4

        if sector_strength == 0:
            sector_score = 5

        # -------------------------------------------------
        # RELATIVE STRENGTH : 5
        # -------------------------------------------------

        rs = _float(
            _get(
                data,
                "relative_strength",
                "rs",
                default=0.0,
            )
        )

        if bullish:

            if rs >= 70:
                relative_strength_score = 5

            elif rs >= 55:
                relative_strength_score = 3

            elif rs == 0:
                relative_strength_score = 2

        else:

            if (
                rs > 0
                and rs <= 30
            ):
                relative_strength_score = 5

            elif (
                rs > 0
                and rs <= 45
            ):
                relative_strength_score = 3

            elif rs == 0:
                relative_strength_score = 2

        # -------------------------------------------------
        # MARKET : 10
        # -------------------------------------------------

        if bullish:

            if (
                vwap > 0
                and price > vwap
            ):
                market_score += 5

        else:

            if (
                vwap > 0
                and price < vwap
            ):
                market_score += 5

        market_trend = (
            self._market_trend(
                data
            )
        )

        if bullish:

            if market_trend in (
                MarketTrend.BULLISH,
                MarketTrend.STRONG_BULLISH,
            ):

                market_score += 5

        else:

            if market_trend in (
                MarketTrend.BEARISH,
                MarketTrend.STRONG_BEARISH,
            ):

                market_score += 5

        score = (
            trend
            + volume_score
            + momentum
            + pattern_score
            + sector_score
            + relative_strength_score
            + market_score
        )

        score = round(
            min(
                score,
                100.0,
            ),
            2,
        )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        confidence = (
            score * 0.70
        )

        if volume_ratio >= 2.0:
            confidence += 10

        elif volume_ratio >= 1.5:
            confidence += 6

        if adx >= 30:
            confidence += 10

        elif adx >= 20:
            confidence += 6

        if (
            pattern_score >= 12
        ):
            confidence += 10

        confidence = round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

        breakdown = {

            "trend":
                round(
                    trend,
                    2,
                ),

            "volume":
                round(
                    volume_score,
                    2,
                ),

            "momentum":
                round(
                    momentum,
                    2,
                ),

            "pattern":
                round(
                    pattern_score,
                    2,
                ),

            "sector":
                round(
                    sector_score,
                    2,
                ),

            "relative_strength":
                round(
                    relative_strength_score,
                    2,
                ),

            "market":
                round(
                    market_score,
                    2,
                ),
        }

        return (
            score,
            confidence,
            breakdown,
        )

    # =====================================================
    # GAP
    # =====================================================

    @staticmethod
    def _calculate_gap(
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
            * 100,
            2,
        )

    # =====================================================
    # MARKET TREND
    # =====================================================

    @staticmethod
    def _market_trend(
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

        value = str(
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
            value,
            MarketTrend.SIDEWAYS,
        )

    # =====================================================
    # STRENGTH
    # =====================================================

    @staticmethod
    def _strength(
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

            "scanner":
                self.name,

            "version":
                self.version,

            "timeframe":
                self.timeframe,

            "minimum_price":
                self.minimum_price,

            "minimum_market_cap":
                self.minimum_market_cap,

            "maximum_gap_percent":
                self.maximum_gap_percent,

            "minimum_rvol":
                self.minimum_rvol,

            "minimum_adx":
                self.minimum_adx,

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "breakout_buffer_percent":
                self.breakout_buffer_percent,

            "allow_buy":
                self.allow_buy,

            "allow_sell":
                self.allow_sell,
        }


# =========================================================
# FACTORY
# =========================================================

def create_breakout_scanner(
    **kwargs: Any,
) -> BreakoutScanner:

    return BreakoutScanner(
        **kwargs
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "BreakoutScanner",

    "create_breakout_scanner",
]


# =========================================================
# END OF FILE
# =========================================================
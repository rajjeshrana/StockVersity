"""
=========================================================
StockVersity Scanner Pro
VCP Scanner
Version : 2.1
=========================================================

File:
    core/scanners/vcp_scanner.py

Purpose
-------
Detect Volatility Contraction Pattern (VCP) setups.

Core Logic
----------
• Price >= ₹200
• Market cap >= ₹1000 Cr when available
• Price above major moving averages
• Progressive volatility contraction
• Volume contraction during base
• Breakout volume expansion
• ADX / RSI / MACD confirmation
• Relative strength confirmation
• Sector / market alignment
• ATR-based stop loss
• Minimum 1:2 risk/reward
• Institutional-style scoring

VCP Concept
-----------
VCP looks for:

    Wide contraction
        ↓
    Smaller contraction
        ↓
    Tight contraction
        ↓
    Volume dries up
        ↓
    Price approaches pivot
        ↓
    Volume expansion
        ↓
    Breakout
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

SCANNER_NAME = "VCPScanner"

SCANNER_VERSION = "2.1"

DEFAULT_TIMEFRAME = "1h"

DEFAULT_MINIMUM_PRICE = 200.0

DEFAULT_MINIMUM_MARKET_CAP = 1000.0

DEFAULT_MAXIMUM_GAP = 3.0

DEFAULT_MINIMUM_SCORE = 70.0

DEFAULT_MINIMUM_CONFIDENCE = 65.0

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_BREAKOUT_RVOL = 1.5

DEFAULT_MAX_FINAL_CONTRACTION = 8.0

DEFAULT_PIVOT_TOLERANCE = 3.0


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
# VCP SCANNER
# =========================================================

class VCPScanner(BaseScanner):
    """
    StockVersity Volatility Contraction Pattern scanner.

    The scanner supports either pre-calculated contraction
    values from the market-data layer or high/low ranges
    representing successive contractions.

    Preferred market-data keys
    --------------------------

    contraction1
    contraction2
    contraction3

    OR

    contraction_1_high
    contraction_1_low

    contraction_2_high
    contraction_2_low

    contraction_3_high
    contraction_3_low

    Optional:

    pivot
    pivot_price
    resistance
    base_volume_ratio
    volume_contraction_ratio
    relative_strength
    sector_strength
    market_trend
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
        minimum_score: float = (
            DEFAULT_MINIMUM_SCORE
        ),
        minimum_confidence: float = (
            DEFAULT_MINIMUM_CONFIDENCE
        ),
        minimum_rr: float = DEFAULT_MINIMUM_RR,
        breakout_rvol: float = DEFAULT_BREAKOUT_RVOL,
        maximum_final_contraction: float = (
            DEFAULT_MAX_FINAL_CONTRACTION
        ),
        pivot_tolerance_percent: float = (
            DEFAULT_PIVOT_TOLERANCE
        ),
        require_trend: bool = True,
        require_contraction: bool = True,
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

        self.minimum_score = float(
            minimum_score
        )

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.minimum_rr = max(
            1.0,
            float(minimum_rr),
        )

        self.breakout_rvol = max(
            0.0,
            float(breakout_rvol),
        )

        self.maximum_final_contraction = max(
            0.0,
            float(maximum_final_contraction),
        )

        self.pivot_tolerance_percent = max(
            0.0,
            float(pivot_tolerance_percent),
        )

        self.require_trend = bool(
            require_trend
        )

        self.require_contraction = bool(
            require_contraction
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
                    "VCP scan error:",
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

        data_block = market_data.get(
            "data"
        )

        if isinstance(
            data_block,
            dict,
        ):

            for key, value in data_block.items():

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

        if last_price < self.minimum_price:
            return None

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

        # -------------------------------------------------
        # GAP FILTER
        # -------------------------------------------------

        gap_percent = self._calculate_gap(
            open_price,
            previous_close,
        )

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
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
        # VOLUME
        # -------------------------------------------------

        volume = _int(
            _get(
                data,
                "volume",
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

        base_volume_ratio = _float(
            _get(
                data,
                "base_volume_ratio",
                "volume_contraction_ratio",
                "dry_volume_ratio",
                default=0.0,
            )
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
        # TREND FILTER
        # -------------------------------------------------

        if self.require_trend:

            if not self._trend_valid(
                price=last_price,
                ema20=ema20,
                ema21=ema21,
                ema50=ema50,
                ema200=ema200,
            ):

                return None

        # -------------------------------------------------
        # CONTRACTIONS
        # -------------------------------------------------

        contractions = (
            self._extract_contractions(
                data
            )
        )

        contraction_valid = (
            self._valid_contractions(
                contractions
            )
        )

        if (
            self.require_contraction
            and not contraction_valid
        ):
            return None

        # -------------------------------------------------
        # PIVOT
        # -------------------------------------------------

        pivot = self._pivot(
            data
        )

        if pivot <= 0:
            return None

        distance_to_pivot = (
            (
                pivot
                - last_price
            )
            / pivot
            * 100
        )

        # Too far below pivot.
        if (
            distance_to_pivot
            > self.pivot_tolerance_percent
        ):
            return None

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        breakout = (
            last_price > pivot
        )

        near_breakout = (
            not breakout
            and distance_to_pivot >= 0
        )

        # VCP should either be close to the pivot
        # or already breaking through it.

        if (
            not breakout
            and not near_breakout
        ):
            return None

        # -------------------------------------------------
        # BREAKOUT VOLUME
        # -------------------------------------------------

        if (
            breakout
            and volume_ratio > 0
            and volume_ratio
            < self.breakout_rvol
        ):
            return None

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        (
            score,
            confidence,
            score_breakdown,
        ) = self._calculate_score(
            data=data,
            price=last_price,
            pivot=pivot,
            contractions=contractions,
            breakout=breakout,
            volume_ratio=volume_ratio,
            base_volume_ratio=(
                base_volume_ratio
            ),
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
        )

        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None

        # -------------------------------------------------
        # ENTRY
        # -------------------------------------------------

        if breakout:

            signal_type = SignalType.BUY

            entry = last_price

            remarks = (
                "VCP breakout confirmed "
                f"above pivot ₹{pivot:.2f}"
            )

        else:

            signal_type = SignalType.WATCH

            entry = pivot

            remarks = (
                "VCP setup approaching "
                f"pivot ₹{pivot:.2f}"
            )

        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        stop_loss = (
            self._stop_loss(
                entry=entry,
                pivot=pivot,
                low_price=low_price,
                ema20=ema20,
                ema21=ema21,
                atr=atr,
                contractions=contractions,
            )
        )

        if (
            stop_loss <= 0
            or stop_loss >= entry
        ):
            return None

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
            + risk
            * self.minimum_rr
        )

        target2 = (
            entry
            + risk * 3.0
        )

        target3 = (
            entry
            + risk * 4.0
        )

        # -------------------------------------------------
        # MARKET INFORMATION
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=signal_type,
            pattern=PatternType.VCP,
            strength=strength,
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name="VCP",
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
                pivot,
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
                "VCP",
                (
                    "BREAKOUT"
                    if breakout
                    else "WATCH"
                ),
            ],
            metadata={
                "pivot":
                    pivot,

                "contractions":
                    list(contractions),

                "contraction_count":
                    len(contractions),

                "base_volume_ratio":
                    base_volume_ratio,

                "market_cap":
                    market_cap,

                "distance_to_pivot_percent":
                    round(
                        distance_to_pivot,
                        2,
                    ),

                "breakout":
                    breakout,
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # EXTRACT CONTRACTIONS
    # =====================================================

    def _extract_contractions(
        self,
        data: Dict[str, Any],
    ) -> List[float]:

        contractions: List[float] = []

        # -------------------------------------------------
        # PRE-CALCULATED VALUES
        # -------------------------------------------------

        for index in range(
            1,
            6,
        ):

            value = _float(
                _get(
                    data,
                    f"contraction{index}",
                    f"contraction_{index}",
                    default=0.0,
                )
            )

            if value > 0:

                contractions.append(
                    value
                )

        if contractions:
            return contractions

        # -------------------------------------------------
        # HIGH / LOW RANGES
        # -------------------------------------------------

        for index in range(
            1,
            6,
        ):

            high = _float(
                _get(
                    data,
                    f"contraction_{index}_high",
                    f"contraction{index}_high",
                    default=0.0,
                )
            )

            low = _float(
                _get(
                    data,
                    f"contraction_{index}_low",
                    f"contraction{index}_low",
                    default=0.0,
                )
            )

            if (
                high <= 0
                or low <= 0
                or high <= low
            ):
                continue

            contraction = (
                (
                    high
                    - low
                )
                / high
                * 100
            )

            contractions.append(
                round(
                    contraction,
                    2,
                )
            )

        return contractions

    # =====================================================
    # VALID CONTRACTIONS
    # =====================================================

    def _valid_contractions(
        self,
        contractions: List[float],
    ) -> bool:

        if len(contractions) < 2:
            return False

        # Each contraction should become smaller.

        for previous, current in zip(
            contractions,
            contractions[1:],
        ):

            if current >= previous:
                return False

        final_contraction = (
            contractions[-1]
        )

        if (
            final_contraction
            > self.maximum_final_contraction
        ):
            return False

        return True

    # =====================================================
    # PIVOT
    # =====================================================

    @staticmethod
    def _pivot(
        data: Dict[str, Any],
    ) -> float:

        return _float(
            _get(
                data,
                "pivot",
                "pivot_price",
                "vcp_pivot",
                "resistance",
                "resistance_level",
                "breakout_level",
                "base_high",
                default=0.0,
            )
        )

    # =====================================================
    # TREND VALIDATION
    # =====================================================

    @staticmethod
    def _trend_valid(
        *,
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
            ema50 > 0
            and price < ema50
        ):
            return False

        if (
            ema200 > 0
            and price < ema200
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
    # STOP LOSS
    # =====================================================

    @staticmethod
    def _stop_loss(
        *,
        entry: float,
        pivot: float,
        low_price: float,
        ema20: float,
        ema21: float,
        atr: float,
        contractions: List[float],
    ) -> float:

        candidates: List[float] = []

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        # Pivot buffer.

        if pivot > 0:

            pivot_stop = (
                pivot * 0.97
            )

            if (
                pivot_stop > 0
                and pivot_stop < entry
            ):

                candidates.append(
                    pivot_stop
                )

        # Current candle low.

        if (
            low_price > 0
            and low_price < entry
        ):

            candidates.append(
                low_price
            )

        # Short EMA.

        if (
            short_ema > 0
            and short_ema < entry
        ):

            candidates.append(
                short_ema
            )

        # ATR stop.

        if atr > 0:

            atr_stop = (
                entry
                - atr * 1.5
            )

            if atr_stop > 0:

                candidates.append(
                    atr_stop
                )

        if not candidates:
            return 0.0

        # Closest technically valid stop.

        return max(
            candidates
        )

    # =====================================================
    # SCORE
    # =====================================================

    def _calculate_score(
        self,
        *,
        data: Dict[str, Any],
        price: float,
        pivot: float,
        contractions: List[float],
        breakout: bool,
        volume_ratio: float,
        base_volume_ratio: float,
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
    ) -> Tuple[
        float,
        float,
        Dict[str, float],
    ]:

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

        if (
            short_ema > 0
            and price > short_ema
        ):
            trend += 5

        if (
            ema50 > 0
            and price > ema50
        ):
            trend += 5

        if (
            ema200 > 0
            and price > ema200
        ):
            trend += 5

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            trend += 5

        # Missing EMA data should not destroy an otherwise
        # valid setup completely.

        if (
            ema50 <= 0
            and ema200 <= 0
        ):
            trend = max(
                trend,
                8.0,
            )

        # -------------------------------------------------
        # VOLUME : 15
        # -------------------------------------------------

        if breakout:

            if volume_ratio >= 3.0:
                volume_score = 15

            elif volume_ratio >= 2.0:
                volume_score = 13

            elif volume_ratio >= 1.5:
                volume_score = 11

            elif volume_ratio > 0:
                volume_score = 5

        else:

            # Before breakout, low volume is desirable.

            if (
                0 < base_volume_ratio <= 0.50
            ):
                volume_score = 15

            elif (
                0 < base_volume_ratio <= 0.70
            ):
                volume_score = 12

            elif (
                0 < base_volume_ratio <= 1.0
            ):
                volume_score = 8

            elif base_volume_ratio == 0:
                volume_score = 6

        # -------------------------------------------------
        # MOMENTUM : 15
        # -------------------------------------------------

        if 55 <= rsi <= 75:
            momentum += 5

        elif 50 <= rsi < 55:
            momentum += 3

        if macd > macd_signal:
            momentum += 3

        if macd_histogram > 0:
            momentum += 2

        if adx >= 25:
            momentum += 3

        elif adx >= 20:
            momentum += 2

        if (
            plus_di > minus_di
            and plus_di > 0
        ):
            momentum += 2

        momentum = min(
            momentum,
            15.0,
        )

        # -------------------------------------------------
        # PATTERN : 25
        # -------------------------------------------------

        if len(contractions) >= 4:

            pattern_score += 8

        elif len(contractions) >= 3:

            pattern_score += 7

        elif len(contractions) >= 2:

            pattern_score += 5

        if contractions:

            final = contractions[-1]

            if final <= 4:
                pattern_score += 8

            elif final <= 6:
                pattern_score += 6

            elif (
                final
                <= self.maximum_final_contraction
            ):
                pattern_score += 4

        if breakout:

            pattern_score += 9

        else:

            distance = (
                (
                    pivot
                    - price
                )
                / pivot
                * 100
                if pivot > 0
                else 100
            )

            if distance <= 1:
                pattern_score += 9

            elif distance <= 2:
                pattern_score += 7

            elif (
                distance
                <= self.pivot_tolerance_percent
            ):
                pattern_score += 5

        pattern_score = min(
            pattern_score,
            25.0,
        )

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

        if sector_strength >= 70:
            sector_score = 10

        elif sector_strength >= 55:
            sector_score = 7

        elif sector_strength > 0:
            sector_score = 4

        else:
            sector_score = 3

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

        if rs >= 80:
            relative_strength_score = 5

        elif rs >= 70:
            relative_strength_score = 4

        elif rs >= 55:
            relative_strength_score = 3

        elif rs == 0:
            relative_strength_score = 2

        # -------------------------------------------------
        # MARKET : 10
        # -------------------------------------------------

        if (
            vwap > 0
            and price > vwap
        ):
            market_score += 4

        market_trend = (
            self._market_trend(
                data
            )
        )

        if (
            market_trend
            == MarketTrend.STRONG_BULLISH
        ):
            market_score += 6

        elif (
            market_trend
            == MarketTrend.BULLISH
        ):
            market_score += 5

        elif (
            market_trend
            == MarketTrend.SIDEWAYS
        ):
            market_score += 2

        market_score = min(
            market_score,
            10.0,
        )

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

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

        if len(contractions) >= 3:
            confidence += 8

        elif len(contractions) >= 2:
            confidence += 5

        if (
            contractions
            and contractions[-1] <= 6
        ):
            confidence += 7

        if breakout:

            if volume_ratio >= 2.0:
                confidence += 10

            elif (
                volume_ratio
                >= self.breakout_rvol
            ):
                confidence += 6

        else:

            if (
                0 < base_volume_ratio <= 0.70
            ):
                confidence += 8

        if (
            rs >= 70
        ):
            confidence += 5

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
            return SignalStrength.VERY_STRONG

        if score >= 80:
            return SignalStrength.STRONG

        if score >= 70:
            return SignalStrength.MODERATE

        if score >= 60:
            return SignalStrength.WEAK

        return SignalStrength.VERY_WEAK

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

            "minimum_score":
                self.minimum_score,

            "minimum_confidence":
                self.minimum_confidence,

            "minimum_rr":
                self.minimum_rr,

            "breakout_rvol":
                self.breakout_rvol,

            "maximum_final_contraction":
                self.maximum_final_contraction,

            "pivot_tolerance_percent":
                self.pivot_tolerance_percent,

            "require_trend":
                self.require_trend,

            "require_contraction":
                self.require_contraction,
        }


# =========================================================
# FACTORY
# =========================================================

def create_vcp_scanner(
    **kwargs: Any,
) -> VCPScanner:

    return VCPScanner(
        **kwargs
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "VCPScanner",
    "create_vcp_scanner",
]


# =========================================================
# END OF FILE
# =========================================================
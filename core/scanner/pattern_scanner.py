"""
=========================================================
StockVersity Scanner Pro
Pattern Scanner
Version : 2.0
=========================================================

Multi-pattern scanner for:

• Bull Flag
• Bear Flag
• Falling Wedge
• Rising Wedge
• Cup & Handle
• Double Bottom
• Double Top
• Ascending Triangle
• Descending Triangle
• Symmetrical Triangle
• Range Breakout

Default universe:
• Price >= ₹200
• Market Cap >= ₹1,000 Cr
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import Signal
from core.scanner.signal import SignalType
from core.scanner.signal import SignalStrength
from core.scanner.signal import PatternType
from core.scanner.signal import MarketTrend


# =========================================================
# PATTERN SCANNER
# =========================================================

class PatternScanner(BaseScanner):

    def __init__(
        self,
        timeframe: str = "1h",
    ) -> None:

        super().__init__(
            name="Pattern Scanner",
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # GENERAL FILTERS
        # -------------------------------------------------

        self.minimum_price = 200.0

        self.minimum_market_cap = 1000.0

        self.minimum_score = 60.0

        self.minimum_rr = 2.0

        self.max_signals = 40

        # -------------------------------------------------
        # QUALITY FILTERS
        # -------------------------------------------------

        self.minimum_adx = 18.0

        self.minimum_relative_strength = 45.0

        self.maximum_gap_percent = 3.0

        self.minimum_breakout_volume_ratio = 1.20

        # -------------------------------------------------
        # TRADE SETTINGS
        # -------------------------------------------------

        self.entry_buffer_percent = 0.05

        self.stop_atr_multiple = 1.5

        self.target_rr_1 = 2.0

        self.target_rr_2 = 3.0

        self.target_rr_3 = 4.0

    # =====================================================
    # MAIN SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:

        generated: List[Signal] = []

        if not market_data:
            return generated

        for key, data in market_data.items():

            if not isinstance(data, dict):
                continue

            try:

                signal = self._scan_symbol(
                    key,
                    data,
                )

                if signal is not None:

                    generated.append(signal)

            except Exception as exc:

                self.log(
                    "Pattern scan error:",
                    key,
                    exc,
                )

        return generated

    # =====================================================
    # SCAN ONE SYMBOL
    # =====================================================

    def _scan_symbol(
        self,
        key: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:

        symbol = str(
            data.get(
                "symbol",
                key,
            )
        ).upper().strip()

        instrument_key = str(
            data.get(
                "instrument_key",
                key,
            )
        ).strip()

        if not symbol:
            return None

        # -------------------------------------------------
        # PRICE DATA
        # -------------------------------------------------

        open_price = self._float(
            data.get("open")
        )

        high = self._float(
            data.get("high")
        )

        low = self._float(
            data.get("low")
        )

        close = self._float(
            data.get(
                "close",
                data.get(
                    "last_price",
                    0.0,
                ),
            )
        )

        previous_close = self._float(
            data.get("previous_close")
        )

        if close <= 0:
            return None

        # -------------------------------------------------
        # MARKET CAP
        # -------------------------------------------------

        market_cap = self._float(
            data.get("market_cap")
        )

        if close < self.minimum_price:
            return None

        if market_cap < self.minimum_market_cap:
            return None

        # -------------------------------------------------
        # GAP
        # -------------------------------------------------

        gap_percent = 0.0

        if (
            previous_close > 0
            and open_price > 0
        ):

            gap_percent = (
                (
                    open_price
                    - previous_close
                )
                / previous_close
            ) * 100.0

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):
            return None

        # -------------------------------------------------
        # VOLUME
        # -------------------------------------------------

        volume = self._int(
            data.get("volume")
        )

        average_volume = self._int(
            data.get("average_volume")
        )

        volume_ratio = 0.0

        if average_volume > 0:

            volume_ratio = (
                volume
                / average_volume
            )

        # -------------------------------------------------
        # INDICATORS
        # -------------------------------------------------

        ema9 = self._float(
            data.get("ema9")
        )

        ema20 = self._float(
            data.get("ema20")
        )

        ema21 = self._float(
            data.get("ema21")
        )

        ema50 = self._float(
            data.get("ema50")
        )

        ema100 = self._float(
            data.get("ema100")
        )

        ema200 = self._float(
            data.get("ema200")
        )

        rsi = self._float(
            data.get("rsi")
        )

        adx = self._float(
            data.get("adx")
        )

        plus_di = self._float(
            data.get("plus_di")
        )

        minus_di = self._float(
            data.get("minus_di")
        )

        atr = self._float(
            data.get("atr")
        )

        vwap = self._float(
            data.get("vwap")
        )

        # -------------------------------------------------
        # MARKET INFORMATION
        # -------------------------------------------------

        sector = str(
            data.get(
                "sector",
                "",
            )
        )

        sector_strength = self._float(
            data.get("sector_strength")
        )

        market_strength = self._float(
            data.get("market_strength")
        )

        relative_strength = self._float(
            data.get("relative_strength")
        )

        beta = self._float(
            data.get("beta")
        )

        # -------------------------------------------------
        # BASIC QUALITY FILTER
        # -------------------------------------------------

        if (
            adx > 0
            and adx < self.minimum_adx
        ):
            return None

        # -------------------------------------------------
        # DETECT PATTERN
        # -------------------------------------------------

        detected = self._detect_pattern(
            data=data,
            close=close,
        )

        if detected is None:
            return None

        (
            pattern,
            signal_type,
            breakout_level,
            pattern_quality,
            pattern_name,
        ) = detected

        # -------------------------------------------------
        # DIRECTION
        # -------------------------------------------------

        bullish = (
            signal_type == SignalType.BUY
        )

        # -------------------------------------------------
        # RELATIVE STRENGTH
        # -------------------------------------------------

        if bullish:

            if (
                relative_strength > 0
                and relative_strength
                < self.minimum_relative_strength
            ):
                return None

        # -------------------------------------------------
        # ENTRY
        # -------------------------------------------------

        buffer = (
            breakout_level
            * self.entry_buffer_percent
            / 100.0
        )

        if bullish:

            entry = max(
                close,
                breakout_level + buffer,
            )

        else:

            entry = min(
                close,
                breakout_level - buffer,
            )

        # -------------------------------------------------
        # TRADE LEVELS
        # -------------------------------------------------

        levels = self._trade_levels(
            signal_type=signal_type,
            entry=entry,
            atr=atr,
            high=high,
            low=low,
            data=data,
        )

        if levels is None:
            return None

        (
            entry,
            stop_loss,
            target1,
            target2,
            target3,
        ) = levels

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        score_breakdown = (
            self._score_breakdown(
                signal_type=signal_type,
                pattern=pattern,
                pattern_quality=pattern_quality,
                close=close,
                ema20=ema20,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                adx=adx,
                plus_di=plus_di,
                minus_di=minus_di,
                volume_ratio=volume_ratio,
                sector_strength=sector_strength,
                relative_strength=relative_strength,
                market_strength=market_strength,
            )
        )

        score = round(
            min(
                sum(
                    score_breakdown.values()
                ),
                100.0,
            ),
            2,
        )

        confidence = (
            self._confidence(
                score=score,
                pattern_quality=pattern_quality,
                volume_ratio=volume_ratio,
                relative_strength=relative_strength,
            )
        )

        strength = self._strength(
            score
        )

        market_trend = self._market_trend(
            data
        )

        # -------------------------------------------------
        # CREATE SIGNAL
        # -------------------------------------------------

        signal = Signal(
            instrument_key=instrument_key,

            symbol=symbol,

            exchange=str(
                data.get(
                    "exchange",
                    "NSE",
                )
            ),

            signal_type=signal_type,

            pattern=pattern,

            strength=strength,

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity Pattern Engine"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

            sector=sector,

            sector_strength=sector_strength,

            market_strength=market_strength,

            relative_strength=relative_strength,

            beta=beta,

            last_price=close,

            open_price=open_price,

            high_price=high,

            low_price=low,

            close_price=close,

            previous_close=previous_close,

            gap_percent=round(
                gap_percent,
                2,
            ),

            volume=volume,

            average_volume=average_volume,

            volume_ratio=round(
                volume_ratio,
                2,
            ),

            trigger_price=breakout_level,

            entry=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=target2,

            target3=target3,

            atr=atr,

            ema9=ema9,

            ema20=ema20,

            ema21=ema21,

            ema50=ema50,

            ema100=ema100,

            ema200=ema200,

            rsi=rsi,

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

            confidence=confidence,

            score=score,

            score_breakdown=score_breakdown,

            remarks=(
                f"{pattern_name} | "
                f"Breakout ₹{breakout_level:.2f} | "
                f"Quality {pattern_quality:.1f} | "
                f"RVOL {volume_ratio:.2f}x"
            ),

            tags=[
                "PATTERN",
                pattern.value,
                signal_type.value,
            ],

            metadata={
                "market_cap": market_cap,

                "pattern_name": pattern_name,

                "pattern_quality": pattern_quality,

                "breakout_level": breakout_level,

                "is_fno": bool(
                    data.get(
                        "is_fno",
                        False,
                    )
                ),
            },
        )

        return signal

    # =====================================================
    # PATTERN DETECTOR
    # =====================================================

    def _detect_pattern(
        self,
        *,
        data: Dict[str, Any],
        close: float,
    ) -> Optional[
        Tuple[
            PatternType,
            SignalType,
            float,
            float,
            str,
        ]
    ]:

        candidates: List[
            Tuple[
                PatternType,
                SignalType,
                float,
                float,
                str,
            ]
        ] = []

        # -------------------------------------------------
        # BULL FLAG
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "bull_flag",
                "bull_flag_detected",
            ),
            level_keys=(
                "bull_flag_breakout",
                "flag_high",
            ),
            quality_keys=(
                "bull_flag_quality",
                "pattern_quality",
            ),
            pattern=PatternType.BULL_FLAG,
            signal_type=SignalType.BUY,
            name="BULL FLAG",
            close=close,
        )

        # -------------------------------------------------
        # BEAR FLAG
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "bear_flag",
                "bear_flag_detected",
            ),
            level_keys=(
                "bear_flag_breakdown",
                "flag_low",
            ),
            quality_keys=(
                "bear_flag_quality",
                "pattern_quality",
            ),
            pattern=PatternType.BEAR_FLAG,
            signal_type=SignalType.SELL,
            name="BEAR FLAG",
            close=close,
        )

        # -------------------------------------------------
        # FALLING WEDGE
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "falling_wedge",
                "falling_wedge_detected",
            ),
            level_keys=(
                "falling_wedge_breakout",
                "wedge_resistance",
            ),
            quality_keys=(
                "falling_wedge_quality",
                "pattern_quality",
            ),
            pattern=PatternType.FALLING_WEDGE,
            signal_type=SignalType.BUY,
            name="FALLING WEDGE",
            close=close,
        )

        # -------------------------------------------------
        # RISING WEDGE
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "rising_wedge",
                "rising_wedge_detected",
            ),
            level_keys=(
                "rising_wedge_breakdown",
                "wedge_support",
            ),
            quality_keys=(
                "rising_wedge_quality",
                "pattern_quality",
            ),
            pattern=PatternType.RISING_WEDGE,
            signal_type=SignalType.SELL,
            name="RISING WEDGE",
            close=close,
        )

        # -------------------------------------------------
        # CUP AND HANDLE
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "cup_handle",
                "cup_handle_detected",
            ),
            level_keys=(
                "cup_handle_breakout",
                "cup_rim",
            ),
            quality_keys=(
                "cup_handle_quality",
                "pattern_quality",
            ),
            pattern=PatternType.CUP_HANDLE,
            signal_type=SignalType.BUY,
            name="CUP & HANDLE",
            close=close,
        )

        # -------------------------------------------------
        # DOUBLE BOTTOM
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "double_bottom",
                "double_bottom_detected",
            ),
            level_keys=(
                "double_bottom_breakout",
                "neckline",
            ),
            quality_keys=(
                "double_bottom_quality",
                "pattern_quality",
            ),
            pattern=PatternType.DOUBLE_BOTTOM,
            signal_type=SignalType.BUY,
            name="DOUBLE BOTTOM",
            close=close,
        )

        # -------------------------------------------------
        # DOUBLE TOP
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "double_top",
                "double_top_detected",
            ),
            level_keys=(
                "double_top_breakdown",
                "neckline",
            ),
            quality_keys=(
                "double_top_quality",
                "pattern_quality",
            ),
            pattern=PatternType.DOUBLE_TOP,
            signal_type=SignalType.SELL,
            name="DOUBLE TOP",
            close=close,
        )

        # -------------------------------------------------
        # ASCENDING TRIANGLE
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "ascending_triangle",
                "ascending_triangle_detected",
            ),
            level_keys=(
                "ascending_triangle_breakout",
                "triangle_resistance",
            ),
            quality_keys=(
                "ascending_triangle_quality",
                "pattern_quality",
            ),
            pattern=PatternType.ASCENDING_TRIANGLE,
            signal_type=SignalType.BUY,
            name="ASCENDING TRIANGLE",
            close=close,
        )

        # -------------------------------------------------
        # DESCENDING TRIANGLE
        # -------------------------------------------------

        self._add_candidate(
            candidates,
            data,
            flag_keys=(
                "descending_triangle",
                "descending_triangle_detected",
            ),
            level_keys=(
                "descending_triangle_breakdown",
                "triangle_support",
            ),
            quality_keys=(
                "descending_triangle_quality",
                "pattern_quality",
            ),
            pattern=PatternType.DESCENDING_TRIANGLE,
            signal_type=SignalType.SELL,
            name="DESCENDING TRIANGLE",
            close=close,
        )

        # -------------------------------------------------
        # SYMMETRICAL TRIANGLE
        # -------------------------------------------------

        symmetrical = self._bool_any(
            data,
            (
                "symmetrical_triangle",
                "symmetrical_triangle_detected",
            ),
        )

        if symmetrical:

            resistance = self._first_float(
                data,
                (
                    "symmetrical_triangle_resistance",
                    "triangle_resistance",
                ),
            )

            support = self._first_float(
                data,
                (
                    "symmetrical_triangle_support",
                    "triangle_support",
                ),
            )

            quality = self._first_float(
                data,
                (
                    "symmetrical_triangle_quality",
                    "pattern_quality",
                ),
                default=70.0,
            )

            if (
                resistance > 0
                and close >= resistance
            ):

                candidates.append(
                    (
                        PatternType.SYMMETRICAL_TRIANGLE,
                        SignalType.BUY,
                        resistance,
                        quality,
                        "SYMMETRICAL TRIANGLE",
                    )
                )

            elif (
                support > 0
                and close <= support
            ):

                candidates.append(
                    (
                        PatternType.SYMMETRICAL_TRIANGLE,
                        SignalType.SELL,
                        support,
                        quality,
                        "SYMMETRICAL TRIANGLE",
                    )
                )

        # -------------------------------------------------
        # RANGE BREAKOUT
        # -------------------------------------------------

        range_high = self._first_float(
            data,
            (
                "range_high",
                "resistance",
            ),
        )

        range_low = self._first_float(
            data,
            (
                "range_low",
                "support",
            ),
        )

        if (
            self._bool_any(
                data,
                (
                    "range_breakout",
                    "range_breakout_detected",
                ),
            )
            and range_high > 0
            and close >= range_high
        ):

            candidates.append(
                (
                    PatternType.RANGE_BREAKOUT,
                    SignalType.BUY,
                    range_high,
                    self._float(
                        data.get(
                            "range_quality",
                            65.0,
                        )
                    ),
                    "RANGE BREAKOUT",
                )
            )

        if not candidates:
            return None

        # -------------------------------------------------
        # BEST PATTERN
        # -------------------------------------------------

        candidates.sort(
            key=lambda item: item[3],
            reverse=True,
        )

        return candidates[0]

    # =====================================================
    # ADD PATTERN CANDIDATE
    # =====================================================

    def _add_candidate(
        self,
        candidates: List,
        data: Dict[str, Any],
        *,
        flag_keys: Tuple[str, ...],
        level_keys: Tuple[str, ...],
        quality_keys: Tuple[str, ...],
        pattern: PatternType,
        signal_type: SignalType,
        name: str,
        close: float,
    ) -> None:

        detected = self._bool_any(
            data,
            flag_keys,
        )

        if not detected:
            return

        level = self._first_float(
            data,
            level_keys,
        )

        if level <= 0:
            return

        quality = self._first_float(
            data,
            quality_keys,
            default=70.0,
        )

        # BUY pattern requires breakout.

        if signal_type == SignalType.BUY:

            if close < level:
                return

        # SELL pattern requires breakdown.

        elif signal_type == SignalType.SELL:

            if close > level:
                return

        candidates.append(
            (
                pattern,
                signal_type,
                level,
                quality,
                name,
            )
        )

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _trade_levels(
        self,
        *,
        signal_type: SignalType,
        entry: float,
        atr: float,
        high: float,
        low: float,
        data: Dict[str, Any],
    ) -> Optional[
        Tuple[
            float,
            float,
            float,
            float,
            float,
        ]
    ]:

        if entry <= 0:
            return None

        if atr <= 0:

            atr = (
                entry * 0.015
            )

        if signal_type == SignalType.BUY:

            swing_low = self._first_float(
                data,
                (
                    "previous_swing_low",
                    "pattern_low",
                    "support",
                ),
            )

            atr_stop = (
                entry
                - atr
                * self.stop_atr_multiple
            )

            if (
                swing_low > 0
                and swing_low < entry
            ):

                stop_loss = max(
                    swing_low,
                    atr_stop,
                )

            elif (
                low > 0
                and low < entry
            ):

                stop_loss = max(
                    low,
                    atr_stop,
                )

            else:

                stop_loss = atr_stop

            risk = (
                entry - stop_loss
            )

            if risk <= 0:
                return None

            target1 = (
                entry
                + risk
                * self.target_rr_1
            )

            target2 = (
                entry
                + risk
                * self.target_rr_2
            )

            target3 = (
                entry
                + risk
                * self.target_rr_3
            )

        else:

            swing_high = self._first_float(
                data,
                (
                    "previous_swing_high",
                    "pattern_high",
                    "resistance",
                ),
            )

            atr_stop = (
                entry
                + atr
                * self.stop_atr_multiple
            )

            if (
                swing_high > entry
            ):

                stop_loss = min(
                    swing_high,
                    atr_stop,
                )

            elif (
                high > entry
            ):

                stop_loss = min(
                    high,
                    atr_stop,
                )

            else:

                stop_loss = atr_stop

            risk = (
                stop_loss - entry
            )

            if risk <= 0:
                return None

            target1 = (
                entry
                - risk
                * self.target_rr_1
            )

            target2 = (
                entry
                - risk
                * self.target_rr_2
            )

            target3 = (
                entry
                - risk
                * self.target_rr_3
            )

            if target1 <= 0:
                return None

        return (
            round(entry, 2),
            round(stop_loss, 2),
            round(target1, 2),
            round(target2, 2),
            round(target3, 2),
        )

    # =====================================================
    # SCORE
    # =====================================================

    @staticmethod
    def _score_breakdown(
        *,
        signal_type: SignalType,
        pattern: PatternType,
        pattern_quality: float,
        close: float,
        ema20: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        volume_ratio: float,
        sector_strength: float,
        relative_strength: float,
        market_strength: float,
    ) -> Dict[str, float]:

        scores = {
            "trend": 0.0,
            "volume": 0.0,
            "momentum": 0.0,
            "pattern": 0.0,
            "sector": 0.0,
            "relative_strength": 0.0,
            "market": 0.0,
        }

        bullish = (
            signal_type == SignalType.BUY
        )

        # -------------------------------------------------
        # TREND : 20
        # -------------------------------------------------

        if bullish:

            if (
                ema20 > 0
                and close > ema20
            ):
                scores["trend"] += 6

            if (
                ema50 > 0
                and close > ema50
            ):
                scores["trend"] += 6

            if (
                ema200 > 0
                and close > ema200
            ):
                scores["trend"] += 4

            if (
                ema20 > 0
                and ema50 > 0
                and ema20 > ema50
            ):
                scores["trend"] += 4

        else:

            if (
                ema20 > 0
                and close < ema20
            ):
                scores["trend"] += 6

            if (
                ema50 > 0
                and close < ema50
            ):
                scores["trend"] += 6

            if (
                ema200 > 0
                and close < ema200
            ):
                scores["trend"] += 4

            if (
                ema20 > 0
                and ema50 > 0
                and ema20 < ema50
            ):
                scores["trend"] += 4

        # -------------------------------------------------
        # VOLUME : 15
        # -------------------------------------------------

        if volume_ratio >= 2.0:

            scores["volume"] = 15

        elif volume_ratio >= 1.5:

            scores["volume"] = 12

        elif volume_ratio >= 1.2:

            scores["volume"] = 9

        elif volume_ratio >= 1.0:

            scores["volume"] = 5

        # -------------------------------------------------
        # MOMENTUM : 15
        # -------------------------------------------------

        if bullish:

            if 55 <= rsi <= 75:
                scores["momentum"] += 7

            elif rsi > 50:
                scores["momentum"] += 4

            if (
                plus_di > 0
                and minus_di > 0
                and plus_di > minus_di
            ):
                scores["momentum"] += 3

        else:

            if 25 <= rsi <= 45:
                scores["momentum"] += 7

            elif (
                rsi > 0
                and rsi < 50
            ):
                scores["momentum"] += 4

            if (
                plus_di > 0
                and minus_di > 0
                and minus_di > plus_di
            ):
                scores["momentum"] += 3

        if adx >= 30:
            scores["momentum"] += 5

        elif adx >= 25:
            scores["momentum"] += 4

        elif adx >= 18:
            scores["momentum"] += 2

        scores["momentum"] = min(
            scores["momentum"],
            15.0,
        )

        # -------------------------------------------------
        # PATTERN : 25
        # -------------------------------------------------

        if pattern_quality >= 90:

            scores["pattern"] = 25

        elif pattern_quality >= 80:

            scores["pattern"] = 22

        elif pattern_quality >= 70:

            scores["pattern"] = 19

        elif pattern_quality >= 60:

            scores["pattern"] = 16

        else:

            scores["pattern"] = 12

        # Bonus for preferred continuation patterns.

        if pattern in (
            PatternType.BULL_FLAG,
            PatternType.FALLING_WEDGE,
            PatternType.CUP_HANDLE,
            PatternType.ASCENDING_TRIANGLE,
        ):

            scores["pattern"] = min(
                scores["pattern"] + 2,
                25.0,
            )

        # -------------------------------------------------
        # SECTOR : 10
        # -------------------------------------------------

        if sector_strength >= 80:

            scores["sector"] = 10

        elif sector_strength >= 70:

            scores["sector"] = 8

        elif sector_strength >= 60:

            scores["sector"] = 6

        elif sector_strength >= 50:

            scores["sector"] = 4

        # -------------------------------------------------
        # RELATIVE STRENGTH : 10
        # -------------------------------------------------

        if relative_strength >= 85:

            scores[
                "relative_strength"
            ] = 10

        elif relative_strength >= 75:

            scores[
                "relative_strength"
            ] = 8

        elif relative_strength >= 65:

            scores[
                "relative_strength"
            ] = 6

        elif relative_strength >= 50:

            scores[
                "relative_strength"
            ] = 4

        # -------------------------------------------------
        # MARKET : 5
        # -------------------------------------------------

        if market_strength >= 80:

            scores["market"] = 5

        elif market_strength >= 65:

            scores["market"] = 4

        elif market_strength >= 50:

            scores["market"] = 3

        return scores

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _confidence(
        *,
        score: float,
        pattern_quality: float,
        volume_ratio: float,
        relative_strength: float,
    ) -> float:

        confidence = (
            score * 0.65
            + pattern_quality * 0.20
        )

        if volume_ratio >= 2.0:
            confidence += 8

        elif volume_ratio >= 1.5:
            confidence += 6

        elif volume_ratio >= 1.2:
            confidence += 3

        if relative_strength >= 75:
            confidence += 5

        elif relative_strength >= 60:
            confidence += 3

        return round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

    # =====================================================
    # SIGNAL STRENGTH
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
    # MARKET TREND
    # =====================================================

    @staticmethod
    def _market_trend(
        data: Dict[str, Any],
    ) -> MarketTrend:

        raw = str(
            data.get(
                "market_trend",
                "SIDEWAYS",
            )
        ).upper()

        mapping = {
            "STRONG_BULLISH":
                MarketTrend.STRONG_BULLISH,

            "BULLISH":
                MarketTrend.BULLISH,

            "SIDEWAYS":
                MarketTrend.SIDEWAYS,

            "NEUTRAL":
                MarketTrend.SIDEWAYS,

            "BEARISH":
                MarketTrend.BEARISH,

            "STRONG_BEARISH":
                MarketTrend.STRONG_BEARISH,
        }

        return mapping.get(
            raw,
            MarketTrend.SIDEWAYS,
        )

    # =====================================================
    # BOOL ANY
    # =====================================================

    @staticmethod
    def _bool_any(
        data: Dict[str, Any],
        keys: Tuple[str, ...],
    ) -> bool:

        for key in keys:

            value = data.get(key)

            if isinstance(value, bool):

                if value:
                    return True

            elif isinstance(
                value,
                (int, float),
            ):

                if value != 0:
                    return True

            elif isinstance(
                value,
                str,
            ):

                if value.upper() in (
                    "TRUE",
                    "YES",
                    "1",
                    "DETECTED",
                ):
                    return True

        return False

    # =====================================================
    # FIRST FLOAT
    # =====================================================

    @classmethod
    def _first_float(
        cls,
        data: Dict[str, Any],
        keys: Tuple[str, ...],
        default: float = 0.0,
    ) -> float:

        for key in keys:

            if key not in data:
                continue

            value = cls._float(
                data.get(key)
            )

            if value != 0:
                return value

        return default

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
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

    # =====================================================
    # SAFE INTEGER
    # =====================================================

    @staticmethod
    def _int(
        value: Any,
        default: int = 0,
    ) -> int:

        try:

            if value is None:
                return default

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError,
        ):

            return default


# =========================================================
# FACTORY
# =========================================================

def create_pattern_scanner(
    timeframe: str = "1h",
) -> PatternScanner:

    return PatternScanner(
        timeframe=timeframe
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "PatternScanner",
    "create_pattern_scanner",
]


# ==========================
# END OF FILE
# ==========================
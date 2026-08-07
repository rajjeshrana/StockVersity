"""
=========================================================
StockVersity Scanner Pro
VCP Scanner
Version : 2.0
=========================================================

Volatility Contraction Pattern Scanner

Detects:
• Volatility contraction
• Tight price structure
• Volume dry-up
• Breakout preparation
• Breakout confirmation
• Trend alignment
• Relative strength
• Institutional-quality VCP setups

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
# VCP SCANNER
# =========================================================

class VCPScanner(BaseScanner):
    """
    Volatility Contraction Pattern scanner.

    The scanner can work with pre-calculated contraction
    information supplied by the market-data layer.

    Expected market_data example
    ----------------------------

    {
        "RELIANCE": {

            "instrument_key": "NSE_EQ|...",
            "symbol": "RELIANCE",
            "exchange": "NSE",

            "open": 1500,
            "high": 1535,
            "low": 1495,
            "close": 1530,
            "previous_close": 1500,

            "volume": 4000000,
            "average_volume": 3000000,

            "ema20": 1490,
            "ema50": 1450,
            "ema200": 1300,

            "rsi": 62,
            "adx": 28,
            "atr": 20,

            "market_cap": 1800000,

            "sector": "ENERGY",

            "sector_strength": 75,
            "relative_strength": 82,
            "market_strength": 70,

            "market_trend": "BULLISH",

            "vcp_pivot": 1525,

            "contraction1": 18,
            "contraction2": 11,
            "contraction3": 6,

            "volume_dryup_ratio": 0.55,

            "base_high": 1525,
            "base_low": 1450,

            "previous_swing_low": 1480
        }
    }
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        timeframe: str = "1h",
    ) -> None:

        super().__init__(
            name="VCP Scanner",
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # GENERAL FILTERS
        # -------------------------------------------------

        self.minimum_price = 200.0

        self.minimum_market_cap = 1000.0

        self.minimum_score = 65.0

        self.minimum_rr = 2.0

        self.max_signals = 30

        # -------------------------------------------------
        # VCP SETTINGS
        # -------------------------------------------------

        self.minimum_contractions = 2

        self.maximum_final_contraction = 10.0

        self.maximum_volume_dryup_ratio = 0.80

        self.minimum_relative_strength = 50.0

        self.minimum_adx = 18.0

        self.maximum_gap_percent = 3.0

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
                    "VCP scan error:",
                    key,
                    exc,
                )

        return generated

    # =====================================================
    # SCAN SYMBOL
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
        # UNIVERSE FILTER
        # -------------------------------------------------

        market_cap = self._float(
            data.get("market_cap")
        )

        if close < self.minimum_price:
            return None

        if market_cap < self.minimum_market_cap:
            return None

        # -------------------------------------------------
        # GAP FILTER
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

        volume_dryup_ratio = self._float(
            data.get(
                "volume_dryup_ratio",
                volume_ratio,
            )
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
        # TREND FILTER
        # -------------------------------------------------

        if not self._trend_valid(
            close=close,
            ema20=ema20,
            ema50=ema50,
            ema200=ema200,
        ):
            return None

        # -------------------------------------------------
        # ADX
        # -------------------------------------------------

        if (
            adx > 0
            and adx < self.minimum_adx
        ):
            return None

        # -------------------------------------------------
        # RELATIVE STRENGTH
        # -------------------------------------------------

        if (
            relative_strength > 0
            and relative_strength
            < self.minimum_relative_strength
        ):
            return None

        # -------------------------------------------------
        # CONTRACTIONS
        # -------------------------------------------------

        contractions = (
            self._get_contractions(data)
        )

        if (
            len(contractions)
            < self.minimum_contractions
        ):
            return None

        if not self._valid_contractions(
            contractions
        ):
            return None

        final_contraction = (
            contractions[-1]
        )

        if (
            final_contraction
            > self.maximum_final_contraction
        ):
            return None

        # -------------------------------------------------
        # PIVOT
        # -------------------------------------------------

        pivot = self._float(
            data.get(
                "vcp_pivot",
                data.get(
                    "base_high",
                    0.0,
                ),
            )
        )

        if pivot <= 0:
            return None

        # -------------------------------------------------
        # VOLUME DRY-UP
        # -------------------------------------------------

        volume_dryup = (
            volume_dryup_ratio
            <= self.maximum_volume_dryup_ratio
        )

        # -------------------------------------------------
        # SETUP STATE
        # -------------------------------------------------

        breakout_buffer = (
            pivot
            * self.entry_buffer_percent
            / 100.0
        )

        breakout_price = (
            pivot + breakout_buffer
        )

        if close >= breakout_price:

            signal_type = SignalType.BUY

            setup_state = "VCP_BREAKOUT"

        elif close >= pivot * 0.97:

            signal_type = SignalType.WATCH

            setup_state = "VCP_NEAR_PIVOT"

        else:

            return None

        # -------------------------------------------------
        # WATCH signals cannot pass BaseScanner RR validation
        # unless valid trade levels are supplied.
        # Therefore both WATCH and BUY receive projected levels.
        # -------------------------------------------------

        levels = self._trade_levels(
            entry=max(
                close,
                breakout_price,
            ),
            pivot=pivot,
            atr=atr,
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
                close=close,
                pivot=pivot,
                contractions=contractions,
                volume_dryup=volume_dryup,
                volume_dryup_ratio=(
                    volume_dryup_ratio
                ),
                volume_ratio=volume_ratio,
                ema20=ema20,
                ema50=ema50,
                ema200=ema200,
                rsi=rsi,
                adx=adx,
                relative_strength=(
                    relative_strength
                ),
                sector_strength=(
                    sector_strength
                ),
                setup_state=setup_state,
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

        confidence = self._confidence(
            score=score,
            contractions=contractions,
            volume_dryup=volume_dryup,
            relative_strength=(
                relative_strength
            ),
            setup_state=setup_state,
        )

        strength = self._strength(
            score
        )

        market_trend = self._market_trend(
            data
        )

        # -------------------------------------------------
        # SIGNAL
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

            pattern=PatternType.VCP,

            strength=strength,

            scanner_name=self.name,

            scanner_version=self.version,

            strategy_name=(
                "StockVersity VCP"
            ),

            timeframe=self.timeframe,

            market_trend=market_trend,

            sector=sector,

            sector_strength=(
                sector_strength
            ),

            market_strength=(
                market_strength
            ),

            relative_strength=(
                relative_strength
            ),

            beta=beta,

            last_price=close,

            open_price=open_price,

            high_price=high,

            low_price=low,

            close_price=close,

            previous_close=(
                previous_close
            ),

            gap_percent=round(
                gap_percent,
                2,
            ),

            volume=volume,

            average_volume=(
                average_volume
            ),

            volume_ratio=round(
                volume_ratio,
                2,
            ),

            trigger_price=pivot,

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

            score_breakdown=(
                score_breakdown
            ),

            remarks=(
                f"{setup_state} | "
                f"Pivot ₹{pivot:.2f} | "
                f"Contractions "
                f"{self._contraction_text(contractions)} | "
                f"Dry-up {volume_dryup_ratio:.2f}x | "
                f"RS {relative_strength:.1f}"
            ),

            tags=[
                "VCP",
                setup_state,
                "CONTRACTION",
            ],

            metadata={
                "market_cap": market_cap,

                "vcp_pivot": pivot,

                "contractions": (
                    list(contractions)
                ),

                "final_contraction": (
                    final_contraction
                ),

                "volume_dryup": (
                    volume_dryup
                ),

                "volume_dryup_ratio": (
                    volume_dryup_ratio
                ),

                "setup_state": (
                    setup_state
                ),

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
    # GET CONTRACTIONS
    # =====================================================

    def _get_contractions(
        self,
        data: Dict[str, Any],
    ) -> List[float]:

        contractions: List[float] = []

        # Preferred format:
        #
        # "contractions": [20, 12, 7, 4]

        raw = data.get(
            "contractions"
        )

        if isinstance(raw, (list, tuple)):

            for value in raw:

                number = self._float(
                    value
                )

                if number > 0:

                    contractions.append(
                        number
                    )

        if contractions:
            return contractions

        # Alternative format:
        #
        # contraction1
        # contraction2
        # contraction3
        # contraction4

        for index in range(
            1,
            7,
        ):

            value = self._float(
                data.get(
                    f"contraction{index}"
                )
            )

            if value > 0:

                contractions.append(
                    value
                )

        return contractions

    # =====================================================
    # VALID CONTRACTIONS
    # =====================================================

    @staticmethod
    def _valid_contractions(
        contractions: List[float],
    ) -> bool:
        """
        Each contraction should generally be smaller
        than the previous contraction.
        """

        if len(contractions) < 2:
            return False

        improvements = 0

        comparisons = 0

        for previous, current in zip(
            contractions,
            contractions[1:],
        ):

            comparisons += 1

            if current < previous:

                improvements += 1

        if comparisons == 0:
            return False

        contraction_quality = (
            improvements
            / comparisons
        )

        return contraction_quality >= 0.75

    # =====================================================
    # TREND VALIDATION
    # =====================================================

    @staticmethod
    def _trend_valid(
        *,
        close: float,
        ema20: float,
        ema50: float,
        ema200: float,
    ) -> bool:

        points = 0

        if (
            ema20 > 0
            and close > ema20
        ):
            points += 1

        if (
            ema50 > 0
            and close > ema50
        ):
            points += 1

        if (
            ema200 > 0
            and close > ema200
        ):
            points += 1

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 > ema50
        ):
            points += 1

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            points += 1

        return points >= 2

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def _trade_levels(
        self,
        *,
        entry: float,
        pivot: float,
        atr: float,
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

        previous_swing_low = self._float(
            data.get(
                "previous_swing_low"
            )
        )

        base_low = self._float(
            data.get(
                "base_low"
            )
        )

        atr_stop = (
            entry
            - (
                atr
                * self.stop_atr_multiple
            )
        )

        candidates = [
            value
            for value in (
                previous_swing_low,
                base_low,
                low,
            )
            if (
                value > 0
                and value < entry
            )
        ]

        if candidates:

            structural_stop = max(
                candidates
            )

            stop_loss = max(
                structural_stop,
                atr_stop,
            )

        else:

            stop_loss = atr_stop

        # Stop must remain below pivot where possible.

        if (
            pivot > 0
            and stop_loss >= entry
        ):

            stop_loss = (
                pivot
                - atr
            )

        risk = (
            entry
            - stop_loss
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
        close: float,
        pivot: float,
        contractions: List[float],
        volume_dryup: bool,
        volume_dryup_ratio: float,
        volume_ratio: float,
        ema20: float,
        ema50: float,
        ema200: float,
        rsi: float,
        adx: float,
        relative_strength: float,
        sector_strength: float,
        setup_state: str,
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

        # -------------------------------------------------
        # TREND : MAX 20
        # -------------------------------------------------

        if (
            ema20 > 0
            and close > ema20
        ):
            scores["trend"] += 5

        if (
            ema50 > 0
            and close > ema50
        ):
            scores["trend"] += 5

        if (
            ema200 > 0
            and close > ema200
        ):
            scores["trend"] += 5

        if (
            ema20 > 0
            and ema50 > 0
            and ema20 > ema50
        ):
            scores["trend"] += 3

        if (
            ema50 > 0
            and ema200 > 0
            and ema50 > ema200
        ):
            scores["trend"] += 2

        # -------------------------------------------------
        # VOLUME : MAX 15
        # -------------------------------------------------

        if volume_dryup:

            if volume_dryup_ratio <= 0.40:

                scores["volume"] += 10

            elif volume_dryup_ratio <= 0.60:

                scores["volume"] += 8

            elif volume_dryup_ratio <= 0.80:

                scores["volume"] += 6

        if (
            setup_state == "VCP_BREAKOUT"
        ):

            if volume_ratio >= 2.0:

                scores["volume"] += 5

            elif volume_ratio >= 1.5:

                scores["volume"] += 4

            elif volume_ratio >= 1.2:

                scores["volume"] += 3

        scores["volume"] = min(
            scores["volume"],
            15.0,
        )

        # -------------------------------------------------
        # MOMENTUM : MAX 15
        # -------------------------------------------------

        if 55 <= rsi <= 70:

            scores["momentum"] += 7

        elif rsi > 50:

            scores["momentum"] += 4

        if adx >= 30:

            scores["momentum"] += 8

        elif adx >= 25:

            scores["momentum"] += 6

        elif adx >= 18:

            scores["momentum"] += 4

        # -------------------------------------------------
        # PATTERN : MAX 25
        # -------------------------------------------------

        contraction_count = len(
            contractions
        )

        if contraction_count >= 4:

            scores["pattern"] += 10

        elif contraction_count >= 3:

            scores["pattern"] += 8

        else:

            scores["pattern"] += 5

        final_contraction = (
            contractions[-1]
        )

        if final_contraction <= 5:

            scores["pattern"] += 8

        elif final_contraction <= 8:

            scores["pattern"] += 6

        elif final_contraction <= 10:

            scores["pattern"] += 4

        if setup_state == "VCP_BREAKOUT":

            scores["pattern"] += 7

        elif (
            pivot > 0
            and close >= pivot * 0.97
        ):

            scores["pattern"] += 4

        scores["pattern"] = min(
            scores["pattern"],
            25.0,
        )

        # -------------------------------------------------
        # SECTOR : MAX 10
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
        # RELATIVE STRENGTH : MAX 10
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
        # MARKET / SETUP : MAX 5
        # -------------------------------------------------

        if (
            setup_state == "VCP_BREAKOUT"
            and volume_ratio >= 1.5
        ):

            scores["market"] = 5

        elif (
            setup_state
            == "VCP_NEAR_PIVOT"
        ):

            scores["market"] = 3

        return scores

    # =====================================================
    # CONFIDENCE
    # =====================================================

    @staticmethod
    def _confidence(
        *,
        score: float,
        contractions: List[float],
        volume_dryup: bool,
        relative_strength: float,
        setup_state: str,
    ) -> float:

        confidence = (
            score * 0.70
        )

        if len(contractions) >= 3:
            confidence += 7

        if len(contractions) >= 4:
            confidence += 3

        if volume_dryup:
            confidence += 7

        if relative_strength >= 75:
            confidence += 7

        elif relative_strength >= 60:
            confidence += 4

        if setup_state == "VCP_BREAKOUT":
            confidence += 8

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
    # CONTRACTION TEXT
    # =====================================================

    @staticmethod
    def _contraction_text(
        contractions: List[float],
    ) -> str:

        return " → ".join(
            f"{value:.1f}%"
            for value in contractions
        )

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

def create_vcp_scanner(
    timeframe: str = "1h",
) -> VCPScanner:

    return VCPScanner(
        timeframe=timeframe
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "VCPScanner",
    "create_vcp_scanner",
]


# ==========================
# END OF FILE
# ==========================
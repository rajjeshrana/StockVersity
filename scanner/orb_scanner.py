"""
=========================================================
StockVersity Scanner Pro
ORB Scanner
Version : 2.0
=========================================================

Opening Range Breakout Scanner

Features
--------
• Bullish ORB breakout
• Bearish ORB breakdown
• Opening range calculation
• Gap filter
• VWAP confirmation
• EMA200 trend confirmation
• ADX strength filter
• Relative volume confirmation
• ORB width filter
• ATR-based stop loss
• Multi-target generation
• Risk / Reward validation
• False breakout protection
• Institutional scoring
• BUY / SELL signals

Designed for:
    NSE Intraday Scanner
    5m / 15m candles
=========================================================
"""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from core.scanner.base_scanner import BaseScanner

from core.scanner.signal import PatternType
from core.scanner.signal import Signal
from core.scanner.signal import SignalStrength
from core.scanner.signal import SignalType

from core.scanner.indicator_engine import IndicatorEngine


# =========================================================
# ORB SCANNER
# =========================================================

class ORBScanner(BaseScanner):
    """
    Opening Range Breakout Scanner.

    Default configuration
    ---------------------
    Timeframe              : 5m
    Opening Range          : 15 minutes
    Maximum Gap            : 3%
    Minimum ADX            : 20
    Minimum RVOL           : 1.5
    Maximum ORB Width      : 3%
    Minimum Risk Reward    : 2
    Minimum Score          : 60
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        name: str = "ORB Scanner",
        timeframe: str = "5m",
    ) -> None:

        super().__init__(
            name=name,
            version="2.0",
            timeframe=timeframe,
        )

        # -------------------------------------------------
        # Opening Range
        # -------------------------------------------------

        self.opening_range_minutes = 15

        self.opening_range_candles = 3

        # -------------------------------------------------
        # Core Filters
        # -------------------------------------------------

        self.maximum_gap_percent = 3.0

        self.minimum_adx = 20.0

        self.minimum_volume_ratio = 1.5

        self.maximum_orb_width_percent = 3.0

        self.minimum_orb_width_percent = 0.15

        # -------------------------------------------------
        # Trend Filters
        # -------------------------------------------------

        self.require_vwap = True

        self.require_ema200 = True

        self.require_macd_confirmation = False

        self.require_supertrend = False

        # -------------------------------------------------
        # Breakout Confirmation
        # -------------------------------------------------

        self.breakout_buffer_percent = 0.05

        self.minimum_body_percent = 35.0

        self.require_breakout_close = True

        # -------------------------------------------------
        # Risk Management
        # -------------------------------------------------

        self.minimum_rr = 2.0

        self.minimum_score = 60.0

        self.max_signals = 20

        self.atr_stop_multiplier = 1.0

        self.target1_rr = 2.0

        self.target2_rr = 3.0

        self.target3_rr = 4.0

        # -------------------------------------------------
        # Indicator Engine
        # -------------------------------------------------

        self.indicator_engine = (
            IndicatorEngine()
        )

    # =====================================================
    # SCAN
    # =====================================================

    def scan(
        self,
        market_data: Dict[str, Any],
    ) -> List[Signal]:
        """
        Scan complete market universe.

        Expected market_data:

        {
            "RELIANCE": {
                "instrument_key": "...",
                "symbol": "RELIANCE",
                "sector": "ENERGY",
                "candles": [...]
            },

            "TCS": {
                ...
            }
        }
        """

        signals: List[Signal] = []

        if not isinstance(
            market_data,
            dict,
        ):
            return signals

        for symbol, data in (
            market_data.items()
        ):

            if not isinstance(
                data,
                dict,
            ):
                continue

            try:

                signal = (
                    self.scan_symbol(
                        symbol,
                        data,
                    )
                )

                if signal is not None:

                    signals.append(
                        signal
                    )

            except Exception as exc:

                self.log(
                    "ORB scan failed:",
                    symbol,
                    exc,
                )

        return signals

    # =====================================================
    # SCAN ONE SYMBOL
    # =====================================================

    def scan_symbol(
        self,
        symbol: str,
        data: Dict[str, Any],
    ) -> Optional[Signal]:

        candles = data.get(
            "candles",
            [],
        )

        if not isinstance(
            candles,
            (list, tuple),
        ):

            return None

        minimum_candles = max(
            self.opening_range_candles + 1,
            20,
        )

        if len(candles) < minimum_candles:

            return None

        # -------------------------------------------------
        # Indicators
        # -------------------------------------------------

        indicators = (
            self.indicator_engine.calculate(
                candles
            )
        )

        if not indicators:

            return None

        # -------------------------------------------------
        # Current Candle
        # -------------------------------------------------

        current = candles[-1]

        current_open = self._number(
            current.get(
                "open",
                current.get(
                    "open_price",
                    0.0,
                ),
            )
        )

        current_high = self._number(
            current.get(
                "high",
                current.get(
                    "high_price",
                    0.0,
                ),
            )
        )

        current_low = self._number(
            current.get(
                "low",
                current.get(
                    "low_price",
                    0.0,
                ),
            )
        )

        current_close = self._number(
            current.get(
                "close",
                current.get(
                    "close_price",
                    0.0,
                ),
            )
        )

        current_volume = int(
            self._number(
                current.get(
                    "volume",
                    0,
                )
            )
        )

        if current_close <= 0:

            return None

        # -------------------------------------------------
        # Previous Close
        # -------------------------------------------------

        previous_close = self._number(
            data.get(
                "previous_close",
                indicators.get(
                    "previous_close",
                    0.0,
                ),
            )
        )

        # -------------------------------------------------
        # Gap Filter
        # -------------------------------------------------

        day_open = self._number(
            candles[0].get(
                "open",
                candles[0].get(
                    "open_price",
                    0.0,
                ),
            )
        )

        gap_percent = (
            self.calculate_gap_percent(
                day_open,
                previous_close,
            )
        )

        if (
            abs(gap_percent)
            > self.maximum_gap_percent
        ):

            return None

        # -------------------------------------------------
        # Opening Range
        # -------------------------------------------------

        opening_range = (
            self.calculate_opening_range(
                candles
            )
        )

        if opening_range is None:

            return None

        orb_high = (
            opening_range["high"]
        )

        orb_low = (
            opening_range["low"]
        )

        orb_width = (
            opening_range["width"]
        )

        orb_width_percent = (
            opening_range[
                "width_percent"
            ]
        )

        # -------------------------------------------------
        # ORB Width Filter
        # -------------------------------------------------

        if (
            orb_width_percent
            > self.maximum_orb_width_percent
        ):

            return None

        if (
            orb_width_percent
            < self.minimum_orb_width_percent
        ):

            return None

        # -------------------------------------------------
        # Indicator Values
        # -------------------------------------------------

        vwap = self._number(
            indicators.get(
                "vwap",
                0.0,
            )
        )

        ema20 = self._number(
            indicators.get(
                "ema20",
                0.0,
            )
        )

        ema50 = self._number(
            indicators.get(
                "ema50",
                0.0,
            )
        )

        ema200 = self._number(
            indicators.get(
                "ema200",
                0.0,
            )
        )

        rsi = self._number(
            indicators.get(
                "rsi",
                0.0,
            )
        )

        macd = self._number(
            indicators.get(
                "macd",
                0.0,
            )
        )

        macd_signal = self._number(
            indicators.get(
                "macd_signal",
                0.0,
            )
        )

        macd_histogram = self._number(
            indicators.get(
                "macd_histogram",
                0.0,
            )
        )

        adx = self._number(
            indicators.get(
                "adx",
                0.0,
            )
        )

        plus_di = self._number(
            indicators.get(
                "plus_di",
                0.0,
            )
        )

        minus_di = self._number(
            indicators.get(
                "minus_di",
                0.0,
            )
        )

        atr = self._number(
            indicators.get(
                "atr",
                0.0,
            )
        )

        volume_ratio = self._number(
            indicators.get(
                "volume_ratio",
                0.0,
            )
        )

        average_volume = int(
            self._number(
                indicators.get(
                    "average_volume",
                    0,
                )
            )
        )

        supertrend = self._number(
            indicators.get(
                "supertrend",
                0.0,
            )
        )

        supertrend_direction = int(
            self._number(
                indicators.get(
                    "supertrend_direction",
                    0,
                )
            )
        )

        # -------------------------------------------------
        # ADX Filter
        # -------------------------------------------------

        if adx < self.minimum_adx:

            return None

        # -------------------------------------------------
        # Volume Confirmation
        # -------------------------------------------------

        if (
            volume_ratio
            < self.minimum_volume_ratio
        ):

            return None

        # -------------------------------------------------
        # Candle Body Quality
        # -------------------------------------------------

        body_percent = (
            self.candle_body_percent(
                current_open,
                current_high,
                current_low,
                current_close,
            )
        )

        if (
            body_percent
            < self.minimum_body_percent
        ):

            return None

        # -------------------------------------------------
        # Breakout Levels
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

        # -------------------------------------------------
        # Detect Direction
        # -------------------------------------------------

        bullish_breakout = (
            current_close
            > bullish_trigger
        )

        bearish_breakout = (
            current_close
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

        if bullish_breakout:

            return self._create_buy_signal(

                symbol=symbol,

                data=data,

                current_open=current_open,

                current_high=current_high,

                current_low=current_low,

                current_close=current_close,

                current_volume=current_volume,

                previous_close=previous_close,

                gap_percent=gap_percent,

                orb_high=orb_high,

                orb_low=orb_low,

                orb_width=orb_width,

                orb_width_percent=(
                    orb_width_percent
                ),

                vwap=vwap,

                ema20=ema20,

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

                atr=atr,

                volume_ratio=volume_ratio,

                average_volume=(
                    average_volume
                ),

                supertrend=supertrend,

                supertrend_direction=(
                    supertrend_direction
                ),

                body_percent=body_percent,

            )

        # -------------------------------------------------
        # SELL
        # -------------------------------------------------

        return self._create_sell_signal(

            symbol=symbol,

            data=data,

            current_open=current_open,

            current_high=current_high,

            current_low=current_low,

            current_close=current_close,

            current_volume=current_volume,

            previous_close=previous_close,

            gap_percent=gap_percent,

            orb_high=orb_high,

            orb_low=orb_low,

            orb_width=orb_width,

            orb_width_percent=(
                orb_width_percent
            ),

            vwap=vwap,

            ema20=ema20,

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

            atr=atr,

            volume_ratio=volume_ratio,

            average_volume=average_volume,

            supertrend=supertrend,

            supertrend_direction=(
                supertrend_direction
            ),

            body_percent=body_percent,

        )

    # =====================================================
    # CREATE BUY SIGNAL
    # =====================================================

    def _create_buy_signal(
        self,
        **values: Any,
    ) -> Optional[Signal]:

        close = values[
            "current_close"
        ]

        orb_high = values[
            "orb_high"
        ]

        orb_low = values[
            "orb_low"
        ]

        atr = values[
            "atr"
        ]

        vwap = values[
            "vwap"
        ]

        ema200 = values[
            "ema200"
        ]

        adx = values[
            "adx"
        ]

        plus_di = values[
            "plus_di"
        ]

        minus_di = values[
            "minus_di"
        ]

        volume_ratio = values[
            "volume_ratio"
        ]

        rsi = values[
            "rsi"
        ]

        macd = values[
            "macd"
        ]

        macd_signal = values[
            "macd_signal"
        ]

        supertrend_direction = values[
            "supertrend_direction"
        ]

        # -------------------------------------------------
        # VWAP Filter
        # -------------------------------------------------

        if (
            self.require_vwap
            and vwap > 0
            and close <= vwap
        ):

            return None

        # -------------------------------------------------
        # EMA200 Filter
        # -------------------------------------------------

        if (
            self.require_ema200
            and ema200 > 0
            and close <= ema200
        ):

            return None

        # -------------------------------------------------
        # Directional Strength
        # -------------------------------------------------

        if (
            plus_di > 0
            and minus_di > 0
            and plus_di <= minus_di
        ):

            return None

        # -------------------------------------------------
        # MACD Confirmation
        # -------------------------------------------------

        if (
            self.require_macd_confirmation
            and macd <= macd_signal
        ):

            return None

        # -------------------------------------------------
        # Supertrend Confirmation
        # -------------------------------------------------

        if (
            self.require_supertrend
            and supertrend_direction < 1
        ):

            return None

        # -------------------------------------------------
        # Entry
        # -------------------------------------------------

        entry = max(
            close,
            orb_high,
        )

        # -------------------------------------------------
        # Stop Loss
        # -------------------------------------------------

        atr_stop = 0.0

        if atr > 0:

            atr_stop = (

                entry

                - (
                    atr
                    * self.atr_stop_multiplier
                )

            )

        structure_stop = (
            orb_low
        )

        if atr_stop > 0:

            stop_loss = max(
                structure_stop,
                atr_stop,
            )

        else:

            stop_loss = (
                structure_stop
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

        target1 = (

            entry

            + risk
            * self.target1_rr

        )

        target2 = (

            entry

            + risk
            * self.target2_rr

        )

        target3 = (

            entry

            + risk
            * self.target3_rr

        )

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        scoring = self.calculate_score(

            direction="BUY",

            price=close,

            vwap=vwap,

            ema200=ema200,

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            volume_ratio=volume_ratio,

            rsi=rsi,

            macd=macd,

            macd_signal=macd_signal,

            body_percent=values[
                "body_percent"
            ],

            orb_width_percent=values[
                "orb_width_percent"
            ],

            supertrend_direction=(
                supertrend_direction
            ),

        )

        score = scoring[
            "score"
        ]

        confidence = scoring[
            "confidence"
        ]

        if score < self.minimum_score:

            return None

        strength = (
            self.determine_strength(
                score
            )
        )

        # -------------------------------------------------
        # Signal
        # -------------------------------------------------

        signal = Signal(

            instrument_key=str(
                values[
                    "data"
                ].get(
                    "instrument_key",
                    values["symbol"],
                )
            ),

            symbol=values[
                "symbol"
            ],

            exchange=str(
                values[
                    "data"
                ].get(
                    "exchange",
                    "NSE",
                )
            ),

            signal_type=SignalType.BUY,

            pattern=PatternType.ORB,

            strength=strength,

            scanner_name=self.name,

            scanner_version=(
                self.version
            ),

            strategy_name=(
                "Opening Range Breakout"
            ),

            timeframe=self.timeframe,

            sector=str(
                values[
                    "data"
                ].get(
                    "sector",
                    "",
                )
            ),

            last_price=close,

            open_price=values[
                "current_open"
            ],

            high_price=values[
                "current_high"
            ],

            low_price=values[
                "current_low"
            ],

            close_price=close,

            previous_close=values[
                "previous_close"
            ],

            gap_percent=values[
                "gap_percent"
            ],

            volume=values[
                "current_volume"
            ],

            average_volume=values[
                "average_volume"
            ],

            volume_ratio=volume_ratio,

            trigger_price=(
                orb_high
            ),

            entry=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=target2,

            target3=target3,

            atr=atr,

            atr_stop=atr_stop,

            ema20=values[
                "ema20"
            ],

            ema50=values[
                "ema50"
            ],

            ema200=ema200,

            rsi=rsi,

            macd=macd,

            macd_signal=(
                macd_signal
            ),

            macd_histogram=values[
                "macd_histogram"
            ],

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

            supertrend=values[
                "supertrend"
            ],

            supertrend_direction=(
                supertrend_direction
            ),

            confidence=confidence,

            score=score,

            score_breakdown=(
                scoring[
                    "breakdown"
                ]
            ),

            remarks=(
                "Bullish opening range "
                "breakout with volume "
                "confirmation."
            ),

            tags=[

                "ORB",

                "BREAKOUT",

                "INTRADAY",

                "VOLUME",

            ],

            metadata={

                "orb_high": (
                    orb_high
                ),

                "orb_low": (
                    orb_low
                ),

                "orb_width": values[
                    "orb_width"
                ],

                "orb_width_percent": (
                    values[
                        "orb_width_percent"
                    ]
                ),

                "body_percent": (
                    values[
                        "body_percent"
                    ]
                ),

                "market_cap": (
                    values[
                        "data"
                    ].get(
                        "market_cap",
                        0.0,
                    )
                ),

            },

        )

        return signal

    # =====================================================
    # CREATE SELL SIGNAL
    # =====================================================

    def _create_sell_signal(
        self,
        **values: Any,
    ) -> Optional[Signal]:

        close = values[
            "current_close"
        ]

        orb_high = values[
            "orb_high"
        ]

        orb_low = values[
            "orb_low"
        ]

        atr = values[
            "atr"
        ]

        vwap = values[
            "vwap"
        ]

        ema200 = values[
            "ema200"
        ]

        adx = values[
            "adx"
        ]

        plus_di = values[
            "plus_di"
        ]

        minus_di = values[
            "minus_di"
        ]

        volume_ratio = values[
            "volume_ratio"
        ]

        rsi = values[
            "rsi"
        ]

        macd = values[
            "macd"
        ]

        macd_signal = values[
            "macd_signal"
        ]

        supertrend_direction = values[
            "supertrend_direction"
        ]

        # -------------------------------------------------
        # VWAP Filter
        # -------------------------------------------------

        if (
            self.require_vwap
            and vwap > 0
            and close >= vwap
        ):

            return None

        # -------------------------------------------------
        # EMA200 Filter
        # -------------------------------------------------

        if (
            self.require_ema200
            and ema200 > 0
            and close >= ema200
        ):

            return None

        # -------------------------------------------------
        # Directional Strength
        # -------------------------------------------------

        if (
            plus_di > 0
            and minus_di > 0
            and minus_di <= plus_di
        ):

            return None

        # -------------------------------------------------
        # MACD Confirmation
        # -------------------------------------------------

        if (
            self.require_macd_confirmation
            and macd >= macd_signal
        ):

            return None

        # -------------------------------------------------
        # Supertrend Confirmation
        # -------------------------------------------------

        if (
            self.require_supertrend
            and supertrend_direction > -1
        ):

            return None

        # -------------------------------------------------
        # Entry
        # -------------------------------------------------

        entry = min(
            close,
            orb_low,
        )

        # -------------------------------------------------
        # Stop Loss
        # -------------------------------------------------

        atr_stop = 0.0

        if atr > 0:

            atr_stop = (

                entry

                + (
                    atr
                    * self.atr_stop_multiplier
                )

            )

        structure_stop = (
            orb_high
        )

        if atr_stop > 0:

            stop_loss = min(
                structure_stop,
                atr_stop,
            )

        else:

            stop_loss = (
                structure_stop
            )

        if (
            stop_loss <= entry
        ):

            return None

        risk = (
            stop_loss
            - entry
        )

        if risk <= 0:

            return None

        target1 = (

            entry

            - risk
            * self.target1_rr

        )

        target2 = (

            entry

            - risk
            * self.target2_rr

        )

        target3 = (

            entry

            - risk
            * self.target3_rr

        )

        if target1 <= 0:

            return None

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        scoring = self.calculate_score(

            direction="SELL",

            price=close,

            vwap=vwap,

            ema200=ema200,

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            volume_ratio=volume_ratio,

            rsi=rsi,

            macd=macd,

            macd_signal=macd_signal,

            body_percent=values[
                "body_percent"
            ],

            orb_width_percent=values[
                "orb_width_percent"
            ],

            supertrend_direction=(
                supertrend_direction
            ),

        )

        score = scoring[
            "score"
        ]

        confidence = scoring[
            "confidence"
        ]

        if score < self.minimum_score:

            return None

        strength = (
            self.determine_strength(
                score
            )
        )

        # -------------------------------------------------
        # Signal
        # -------------------------------------------------

        signal = Signal(

            instrument_key=str(
                values[
                    "data"
                ].get(
                    "instrument_key",
                    values["symbol"],
                )
            ),

            symbol=values[
                "symbol"
            ],

            exchange=str(
                values[
                    "data"
                ].get(
                    "exchange",
                    "NSE",
                )
            ),

            signal_type=SignalType.SELL,

            pattern=PatternType.ORB,

            strength=strength,

            scanner_name=self.name,

            scanner_version=(
                self.version
            ),

            strategy_name=(
                "Opening Range Breakdown"
            ),

            timeframe=self.timeframe,

            sector=str(
                values[
                    "data"
                ].get(
                    "sector",
                    "",
                )
            ),

            last_price=close,

            open_price=values[
                "current_open"
            ],

            high_price=values[
                "current_high"
            ],

            low_price=values[
                "current_low"
            ],

            close_price=close,

            previous_close=values[
                "previous_close"
            ],

            gap_percent=values[
                "gap_percent"
            ],

            volume=values[
                "current_volume"
            ],

            average_volume=values[
                "average_volume"
            ],

            volume_ratio=volume_ratio,

            trigger_price=(
                orb_low
            ),

            entry=entry,

            stop_loss=stop_loss,

            target1=target1,

            target2=max(
                target2,
                0.01,
            ),

            target3=max(
                target3,
                0.01,
            ),

            atr=atr,

            atr_stop=atr_stop,

            ema20=values[
                "ema20"
            ],

            ema50=values[
                "ema50"
            ],

            ema200=ema200,

            rsi=rsi,

            macd=macd,

            macd_signal=(
                macd_signal
            ),

            macd_histogram=values[
                "macd_histogram"
            ],

            adx=adx,

            plus_di=plus_di,

            minus_di=minus_di,

            vwap=vwap,

            supertrend=values[
                "supertrend"
            ],

            supertrend_direction=(
                supertrend_direction
            ),

            confidence=confidence,

            score=score,

            score_breakdown=(
                scoring[
                    "breakdown"
                ]
            ),

            remarks=(
                "Bearish opening range "
                "breakdown with volume "
                "confirmation."
            ),

            tags=[

                "ORB",

                "BREAKDOWN",

                "INTRADAY",

                "VOLUME",

            ],

            metadata={

                "orb_high": (
                    orb_high
                ),

                "orb_low": (
                    orb_low
                ),

                "orb_width": values[
                    "orb_width"
                ],

                "orb_width_percent": (
                    values[
                        "orb_width_percent"
                    ]
                ),

                "body_percent": (
                    values[
                        "body_percent"
                    ]
                ),

                "market_cap": (
                    values[
                        "data"
                    ].get(
                        "market_cap",
                        0.0,
                    )
                ),

            },

        )

        return signal

    # =====================================================
    # OPENING RANGE
    # =====================================================

    def calculate_opening_range(
        self,
        candles: Sequence[
            Dict[str, Any]
        ],
    ) -> Optional[
        Dict[str, float]
    ]:
        """
        Calculate ORB from first N candles.

        Default:
            3 x 5-minute candles = 15-minute ORB.
        """

        if (
            len(candles)
            < self.opening_range_candles
        ):

            return None

        opening = candles[
            :self.opening_range_candles
        ]

        highs = [

            self._number(
                candle.get(
                    "high",
                    candle.get(
                        "high_price",
                        0.0,
                    ),
                )
            )

            for candle in opening

        ]

        lows = [

            self._number(
                candle.get(
                    "low",
                    candle.get(
                        "low_price",
                        0.0,
                    ),
                )
            )

            for candle in opening

        ]

        highs = [

            value

            for value in highs

            if value > 0

        ]

        lows = [

            value

            for value in lows

            if value > 0

        ]

        if not highs or not lows:

            return None

        orb_high = max(
            highs
        )

        orb_low = min(
            lows
        )

        if (
            orb_high <= 0
            or orb_low <= 0
            or orb_high <= orb_low
        ):

            return None

        width = (
            orb_high
            - orb_low
        )

        midpoint = (

            orb_high
            + orb_low

        ) / 2.0

        if midpoint <= 0:

            return None

        width_percent = (

            width
            / midpoint

        ) * 100.0

        return {

            "high": round(
                orb_high,
                4,
            ),

            "low": round(
                orb_low,
                4,
            ),

            "width": round(
                width,
                4,
            ),

            "width_percent": round(
                width_percent,
                4,
            ),

        }

    # =====================================================
    # GAP
    # =====================================================

    @staticmethod
    def calculate_gap_percent(
        day_open: float,
        previous_close: float,
    ) -> float:

        if previous_close <= 0:

            return 0.0

        return round(

            (

                (
                    day_open
                    - previous_close
                )

                / previous_close

            )

            * 100.0,

            4,

        )

    # =====================================================
    # CANDLE BODY
    # =====================================================

    @staticmethod
    def candle_body_percent(
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> float:

        candle_range = (

            high_price
            - low_price

        )

        if candle_range <= 0:

            return 0.0

        body = abs(

            close_price
            - open_price

        )

        return round(

            (
                body
                / candle_range
            )
            * 100.0,

            2,

        )

    # =====================================================
    # SCORING
    # =====================================================

    def calculate_score(
        self,
        *,
        direction: str,
        price: float,
        vwap: float,
        ema200: float,
        adx: float,
        plus_di: float,
        minus_di: float,
        volume_ratio: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        body_percent: float,
        orb_width_percent: float,
        supertrend_direction: int,
    ) -> Dict[str, Any]:
        """
        Institutional-style ORB scoring.

        Maximum score = 100.
        """

        direction = (
            direction
            .upper()
            .strip()
        )

        # -------------------------------------------------
        # Trend = 20
        # -------------------------------------------------

        trend_score = 0.0

        if direction == "BUY":

            if (
                ema200 > 0
                and price > ema200
            ):

                trend_score += 10.0

            if (
                vwap > 0
                and price > vwap
            ):

                trend_score += 10.0

        else:

            if (
                ema200 > 0
                and price < ema200
            ):

                trend_score += 10.0

            if (
                vwap > 0
                and price < vwap
            ):

                trend_score += 10.0

        # -------------------------------------------------
        # Volume = 20
        # -------------------------------------------------

        if volume_ratio >= 3.0:

            volume_score = 20.0

        elif volume_ratio >= 2.0:

            volume_score = 17.0

        elif volume_ratio >= 1.5:

            volume_score = 14.0

        elif volume_ratio >= 1.2:

            volume_score = 8.0

        else:

            volume_score = 0.0

        # -------------------------------------------------
        # Momentum = 20
        # -------------------------------------------------

        momentum_score = 0.0

        if adx >= 35:

            momentum_score += 10.0

        elif adx >= 25:

            momentum_score += 8.0

        elif adx >= 20:

            momentum_score += 5.0

        if direction == "BUY":

            if (
                plus_di > minus_di
            ):

                momentum_score += 5.0

            if 55 <= rsi <= 75:

                momentum_score += 5.0

        else:

            if (
                minus_di > plus_di
            ):

                momentum_score += 5.0

            if 25 <= rsi <= 45:

                momentum_score += 5.0

        # -------------------------------------------------
        # Pattern = 20
        # -------------------------------------------------

        pattern_score = 0.0

        if body_percent >= 70:

            pattern_score += 10.0

        elif body_percent >= 50:

            pattern_score += 8.0

        elif body_percent >= 35:

            pattern_score += 5.0

        if (
            0.30
            <= orb_width_percent
            <= 2.0
        ):

            pattern_score += 10.0

        elif (
            orb_width_percent
            <= 2.5
        ):

            pattern_score += 7.0

        elif (
            orb_width_percent
            <= 3.0
        ):

            pattern_score += 4.0

        # -------------------------------------------------
        # Confirmation = 20
        # -------------------------------------------------

        confirmation_score = 0.0

        if direction == "BUY":

            if macd > macd_signal:

                confirmation_score += 10.0

            if supertrend_direction == 1:

                confirmation_score += 10.0

        else:

            if macd < macd_signal:

                confirmation_score += 10.0

            if supertrend_direction == -1:

                confirmation_score += 10.0

        # -------------------------------------------------
        # Final Score
        # -------------------------------------------------

        score = (

            trend_score

            + volume_score

            + momentum_score

            + pattern_score

            + confirmation_score

        )

        score = round(

            min(
                score,
                100.0,
            ),

            2,

        )

        # -------------------------------------------------
        # Confidence
        # -------------------------------------------------

        confidence = (

            score * 0.75

            + min(
                volume_ratio,
                4.0,
            )
            * 5.0

            + min(
                adx,
                50.0,
            )
            * 0.10

        )

        confidence = round(

            min(
                confidence,
                100.0,
            ),

            2,

        )

        return {

            "score": score,

            "confidence": (
                confidence
            ),

            "breakdown": {

                "trend": (
                    trend_score
                ),

                "volume": (
                    volume_score
                ),

                "momentum": (
                    momentum_score
                ),

                "pattern": (
                    pattern_score
                ),

                "sector": 0.0,

                "relative_strength": (
                    confirmation_score
                ),

                "market": 0.0,

            },

        }

    # =====================================================
    # SIGNAL STRENGTH
    # =====================================================

    @staticmethod
    def determine_strength(
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
    # SAFE NUMBER
    # =====================================================

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:

                return default

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # =====================================================
    # CONFIGURATION PRESETS
    # =====================================================

    def conservative(
        self,
    ) -> "ORBScanner":
        """
        Higher-quality / fewer signals.
        """

        self.minimum_score = 75.0

        self.minimum_rr = 2.0

        self.minimum_adx = 25.0

        self.minimum_volume_ratio = 2.0

        self.maximum_gap_percent = 2.5

        self.maximum_orb_width_percent = 2.5

        self.minimum_body_percent = 50.0

        self.require_vwap = True

        self.require_ema200 = True

        self.require_macd_confirmation = True

        return self

    def balanced(
        self,
    ) -> "ORBScanner":
        """
        Recommended normal intraday mode.
        """

        self.minimum_score = 60.0

        self.minimum_rr = 2.0

        self.minimum_adx = 20.0

        self.minimum_volume_ratio = 1.5

        self.maximum_gap_percent = 3.0

        self.maximum_orb_width_percent = 3.0

        self.minimum_body_percent = 35.0

        self.require_vwap = True

        self.require_ema200 = True

        self.require_macd_confirmation = False

        return self

    def aggressive(
        self,
    ) -> "ORBScanner":
        """
        More signals / looser filtering.
        """

        self.minimum_score = 50.0

        self.minimum_rr = 1.5

        self.minimum_adx = 18.0

        self.minimum_volume_ratio = 1.2

        self.maximum_gap_percent = 3.0

        self.maximum_orb_width_percent = 3.0

        self.minimum_body_percent = 25.0

        self.require_vwap = True

        self.require_ema200 = False

        self.require_macd_confirmation = False

        return self

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

            "opening_range_minutes": (
                self.opening_range_minutes
            ),

            "opening_range_candles": (
                self.opening_range_candles
            ),

            "maximum_gap_percent": (
                self.maximum_gap_percent
            ),

            "minimum_adx": (
                self.minimum_adx
            ),

            "minimum_volume_ratio": (
                self.minimum_volume_ratio
            ),

            "maximum_orb_width_percent": (
                self.maximum_orb_width_percent
            ),

            "minimum_score": (
                self.minimum_score
            ),

            "minimum_rr": (
                self.minimum_rr
            ),

            "require_vwap": (
                self.require_vwap
            ),

            "require_ema200": (
                self.require_ema200
            ),

        }


# =========================================================
# FACTORY
# =========================================================

def create_orb_scanner(
    *,
    timeframe: str = "5m",
    mode: str = "balanced",
) -> ORBScanner:
    """
    Factory for ORB Scanner.

    Modes
    -----
    conservative
    balanced
    aggressive
    """

    scanner = ORBScanner(
        timeframe=timeframe
    )

    mode = (
        mode
        .lower()
        .strip()
    )

    if mode == "conservative":

        scanner.conservative()

    elif mode == "aggressive":

        scanner.aggressive()

    else:

        scanner.balanced()

    return scanner


# =========================================================
# MODULE EXPORTS
# =========================================================

__all__ = [

    "ORBScanner",

    "create_orb_scanner",

]


# ==========================
# END OF FILE
# ==========================
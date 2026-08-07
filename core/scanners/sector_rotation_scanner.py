"""
=========================================================
StockVersity Scanner Pro
Sector Rotation Scanner
Version : 2.1
=========================================================

File:
    core/scanners/sector_rotation_scanner.py

Purpose
-------
Find high-quality stocks aligned with sector rotation.

BUY:
    Strong stock inside strong/outperforming sector.

SELL:
    Weak stock inside weak/underperforming sector.

Main Filters
------------
• Price >= ₹200
• Market cap >= ₹1000 Cr when available
• Gap <= 3%
• Sector strength
• Relative strength
• Market trend
• EMA structure
• RSI
• MACD
• ADX / DI
• Relative volume
• Minimum 1:2 risk/reward
=========================================================
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)

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

SCANNER_NAME = "SectorRotationScanner"

SCANNER_VERSION = "2.1"

DEFAULT_TIMEFRAME = "15m"

DEFAULT_MINIMUM_PRICE = 200.0

DEFAULT_MINIMUM_MARKET_CAP = 1000.0

DEFAULT_MAXIMUM_GAP_PERCENT = 3.0

DEFAULT_MINIMUM_SCORE = 68.0

DEFAULT_MINIMUM_CONFIDENCE = 65.0

DEFAULT_MINIMUM_RR = 2.0

DEFAULT_MINIMUM_ADX = 20.0

DEFAULT_MINIMUM_VOLUME_RATIO = 1.10

DEFAULT_STRONG_SECTOR_SCORE = 60.0

DEFAULT_WEAK_SECTOR_SCORE = 40.0


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

    except (TypeError, ValueError):

        return default


def _int(
    value: Any,
    default: int = 0,
) -> int:

    try:

        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):

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
# SECTOR ROTATION SCANNER
# =========================================================

class SectorRotationScanner(BaseScanner):
    """
    Scanner for sector-aligned opportunities.

    A BUY setup normally requires:

        Strong sector
        Strong stock relative strength
        Bullish trend
        Momentum confirmation

    A SELL setup normally requires:

        Weak sector
        Weak stock relative strength
        Bearish trend
        Momentum confirmation
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
            DEFAULT_MAXIMUM_GAP_PERCENT
        ),
        minimum_score: float = DEFAULT_MINIMUM_SCORE,
        minimum_confidence: float = (
            DEFAULT_MINIMUM_CONFIDENCE
        ),
        minimum_rr: float = DEFAULT_MINIMUM_RR,
        minimum_adx: float = DEFAULT_MINIMUM_ADX,
        minimum_volume_ratio: float = (
            DEFAULT_MINIMUM_VOLUME_RATIO
        ),
        strong_sector_score: float = (
            DEFAULT_STRONG_SECTOR_SCORE
        ),
        weak_sector_score: float = (
            DEFAULT_WEAK_SECTOR_SCORE
        ),
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

        self.minimum_score = max(
            0.0,
            float(minimum_score),
        )

        self.minimum_confidence = max(
            0.0,
            float(minimum_confidence),
        )

        self.minimum_rr = max(
            1.0,
            float(minimum_rr),
        )

        self.minimum_adx = max(
            0.0,
            float(minimum_adx),
        )

        self.minimum_volume_ratio = max(
            0.0,
            float(minimum_volume_ratio),
        )

        self.strong_sector_score = float(
            strong_sector_score
        )

        self.weak_sector_score = float(
            weak_sector_score
        )

        self.max_signals = 30

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
                    "Sector rotation scan error:",
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
        # GAP
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
        # SECTOR
        # -------------------------------------------------

        sector = str(
            _get(
                data,
                "sector",
                "sector_name",
                default="",
            )
        ).strip()

        sector_strength = _float(
            _get(
                data,
                "sector_strength",
                "sector_score",
                default=0.0,
            )
        )

        sector_change = _float(
            _get(
                data,
                "sector_change",
                "sector_change_percent",
                default=0.0,
            )
        )

        sector_rank = _int(
            _get(
                data,
                "sector_rank",
                default=0,
            )
        )

        # Sector data is mandatory for this scanner.

        if (
            sector_strength <= 0
            and sector_change == 0
        ):
            return None

        # -------------------------------------------------
        # STOCK RELATIVE STRENGTH
        # -------------------------------------------------

        relative_strength = _float(
            _get(
                data,
                "relative_strength",
                "rs",
                "relative_strength_score",
                default=0.0,
            )
        )

        stock_change = _float(
            _get(
                data,
                "change_percent",
                "stock_change",
                "percent_change",
                default=0.0,
            )
        )

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
                "relative_volume",
                "rvol",
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

        atr = _float(
            _get(
                data,
                "atr",
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

        # -------------------------------------------------
        # MARKET TREND
        # -------------------------------------------------

        market_trend = self._market_trend(
            data
        )

        # -------------------------------------------------
        # DIRECTION
        # -------------------------------------------------

        direction = self._direction(
            price=last_price,
            sector_strength=sector_strength,
            sector_change=sector_change,
            relative_strength=relative_strength,
            stock_change=stock_change,
            ema20=ema20,
            ema21=ema21,
            ema50=ema50,
            ema200=ema200,
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            plus_di=plus_di,
            minus_di=minus_di,
        )

        if direction is None:
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
        # VOLUME
        # -------------------------------------------------

        if (
            volume_ratio > 0
            and volume_ratio
            < self.minimum_volume_ratio
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
            direction=direction,
            price=last_price,
            sector_strength=sector_strength,
            sector_change=sector_change,
            sector_rank=sector_rank,
            relative_strength=relative_strength,
            stock_change=stock_change,
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
            market_trend=market_trend,
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

        entry = last_price

        # -------------------------------------------------
        # STOP LOSS
        # -------------------------------------------------

        swing_low = _float(
            _get(
                data,
                "swing_low",
                "previous_swing_low",
                default=0.0,
            )
        )

        swing_high = _float(
            _get(
                data,
                "swing_high",
                "previous_swing_high",
                default=0.0,
            )
        )

        stop_loss = self._stop_loss(
            direction=direction,
            entry=entry,
            atr=atr,
            ema20=ema20,
            ema21=ema21,
            swing_low=swing_low,
            swing_high=swing_high,
        )

        if stop_loss <= 0:
            return None

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        (
            target1,
            target2,
            target3,
        ) = self._targets(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
        )

        if target1 <= 0:
            return None

        # -------------------------------------------------
        # SIGNAL
        # -------------------------------------------------

        signal = Signal(
            instrument_key=instrument_key,
            symbol=symbol,
            signal_type=direction,
            pattern=PatternType.MOMENTUM,
            strength=self._strength(
                score
            ),
            scanner_name=self.name,
            scanner_version=self.version,
            strategy_name=(
                "StockVersity Sector Rotation"
            ),
            timeframe=self.timeframe,
            market_trend=market_trend,
            sector=sector,
            sector_strength=sector_strength,
            relative_strength=relative_strength,
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
            trigger_price=entry,
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
            macd_histogram=macd_histogram,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            vwap=vwap,
            confidence=confidence,
            score=score,
            score_breakdown=score_breakdown,
            remarks=(
                f"{direction.value} sector rotation | "
                f"{sector} | "
                f"Sector strength "
                f"{sector_strength:.1f}"
            ),
            tags=[
                "SECTOR_ROTATION",
                direction.value,
                sector.upper(),
            ],
            metadata={
                "market_cap":
                    market_cap,

                "sector_rank":
                    sector_rank,

                "sector_change":
                    sector_change,

                "stock_change":
                    stock_change,

                "sector_strength":
                    sector_strength,

                "relative_strength":
                    relative_strength,

                "rotation_direction":
                    direction.value,
            },
        )

        if (
            signal.risk_reward
            < self.minimum_rr
        ):
            return None

        return signal

    # =====================================================
    # DIRECTION
    # =====================================================

    def _direction(
        self,
        *,
        price: float,
        sector_strength: float,
        sector_change: float,
        relative_strength: float,
        stock_change: float,
        ema20: float,
        ema21: float,
        ema50: float,
        ema200: float,
        rsi: float,
        macd: float,
        macd_signal: float,
        plus_di: float,
        minus_di: float,
    ) -> Optional[SignalType]:

        bullish = 0

        bearish = 0

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        # Sector direction

        if (
            sector_strength
            >= self.strong_sector_score
        ):
            bullish += 3

        if (
            sector_strength > 0
            and sector_strength
            <= self.weak_sector_score
        ):
            bearish += 3

        if sector_change > 0:
            bullish += 1

        elif sector_change < 0:
            bearish += 1

        # Relative strength

        if relative_strength >= 60:
            bullish += 2

        elif (
            relative_strength > 0
            and relative_strength <= 40
        ):
            bearish += 2

        # Stock performance

        if stock_change > sector_change:
            bullish += 1

        elif stock_change < sector_change:
            bearish += 1

        # EMA structure

        if short_ema > 0:

            if price > short_ema:
                bullish += 1

            elif price < short_ema:
                bearish += 1

        if ema50 > 0:

            if price > ema50:
                bullish += 1

            elif price < ema50:
                bearish += 1

        if ema200 > 0:

            if price > ema200:
                bullish += 2

            elif price < ema200:
                bearish += 2

        # RSI

        if rsi >= 55:
            bullish += 1

        elif (
            rsi > 0
            and rsi <= 45
        ):
            bearish += 1

        # MACD

        if (
            macd != 0
            or macd_signal != 0
        ):

            if macd > macd_signal:
                bullish += 1

            elif macd < macd_signal:
                bearish += 1

        # DI

        if (
            plus_di > 0
            or minus_di > 0
        ):

            if plus_di > minus_di:
                bullish += 1

            elif minus_di > plus_di:
                bearish += 1

        if (
            bullish >= 7
            and bullish > bearish
        ):
            return SignalType.BUY

        if (
            bearish >= 7
            and bearish > bullish
        ):
            return SignalType.SELL

        return None

    # =====================================================
    # SCORE
    # =====================================================

    @staticmethod
    def _calculate_score(
        *,
        direction: SignalType,
        price: float,
        sector_strength: float,
        sector_change: float,
        sector_rank: int,
        relative_strength: float,
        stock_change: float,
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
        market_trend: MarketTrend,
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

        relative = 0.0

        market = 0.0

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        # -------------------------------------------------
        # TREND : 20
        # -------------------------------------------------

        if direction == SignalType.BUY:

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
                trend += 6

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 > ema200
            ):
                trend += 4

        else:

            if (
                short_ema > 0
                and price < short_ema
            ):
                trend += 5

            if (
                ema50 > 0
                and price < ema50
            ):
                trend += 5

            if (
                ema200 > 0
                and price < ema200
            ):
                trend += 6

            if (
                ema50 > 0
                and ema200 > 0
                and ema50 < ema200
            ):
                trend += 4

        trend = min(
            trend,
            20.0,
        )

        # -------------------------------------------------
        # VOLUME : 12
        # -------------------------------------------------

        if volume_ratio >= 2.0:
            volume = 12

        elif volume_ratio >= 1.5:
            volume = 10

        elif volume_ratio >= 1.2:
            volume = 8

        elif volume_ratio >= 1.0:
            volume = 6

        elif volume_ratio > 0:
            volume = 3

        else:
            volume = 2

        # -------------------------------------------------
        # MOMENTUM : 18
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if 55 <= rsi <= 70:
                momentum += 5

            elif rsi > 50:
                momentum += 3

            if macd > macd_signal:
                momentum += 4

            if macd_histogram > 0:
                momentum += 2

            if plus_di > minus_di:
                momentum += 3

            if (
                vwap > 0
                and price > vwap
            ):
                momentum += 2

        else:

            if 30 <= rsi <= 45:
                momentum += 5

            elif (
                rsi > 0
                and rsi < 50
            ):
                momentum += 3

            if macd < macd_signal:
                momentum += 4

            if macd_histogram < 0:
                momentum += 2

            if minus_di > plus_di:
                momentum += 3

            if (
                vwap > 0
                and price < vwap
            ):
                momentum += 2

        if adx >= 30:
            momentum += 2

        elif adx >= 20:
            momentum += 1

        momentum = min(
            momentum,
            18.0,
        )

        # -------------------------------------------------
        # ROTATION PATTERN : 10
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if stock_change > sector_change:
                pattern += 5

            if sector_change > 0:
                pattern += 3

        else:

            if stock_change < sector_change:
                pattern += 5

            if sector_change < 0:
                pattern += 3

        if (
            sector_rank > 0
            and sector_rank <= 3
            and direction == SignalType.BUY
        ):
            pattern += 2

        pattern = min(
            pattern,
            10.0,
        )

        # -------------------------------------------------
        # SECTOR : 20
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if sector_strength >= 80:
                sector = 20

            elif sector_strength >= 70:
                sector = 17

            elif sector_strength >= 60:
                sector = 14

            elif sector_strength >= 50:
                sector = 8

        else:

            if (
                sector_strength > 0
                and sector_strength <= 20
            ):
                sector = 20

            elif sector_strength <= 30:
                sector = 17

            elif sector_strength <= 40:
                sector = 14

            elif sector_strength <= 50:
                sector = 8

        # -------------------------------------------------
        # RELATIVE STRENGTH : 12
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if relative_strength >= 80:
                relative = 12

            elif relative_strength >= 70:
                relative = 10

            elif relative_strength >= 60:
                relative = 8

            elif relative_strength >= 50:
                relative = 5

        else:

            if (
                relative_strength > 0
                and relative_strength <= 20
            ):
                relative = 12

            elif relative_strength <= 30:
                relative = 10

            elif relative_strength <= 40:
                relative = 8

            elif relative_strength <= 50:
                relative = 5

        # -------------------------------------------------
        # MARKET : 8
        # -------------------------------------------------

        if direction == SignalType.BUY:

            if (
                market_trend
                == MarketTrend.STRONG_BULLISH
            ):
                market = 8

            elif (
                market_trend
                == MarketTrend.BULLISH
            ):
                market = 7

            elif (
                market_trend
                == MarketTrend.SIDEWAYS
            ):
                market = 4

            else:
                market = 1

        else:

            if (
                market_trend
                == MarketTrend.STRONG_BEARISH
            ):
                market = 8

            elif (
                market_trend
                == MarketTrend.BEARISH
            ):
                market = 7

            elif (
                market_trend
                == MarketTrend.SIDEWAYS
            ):
                market = 4

            else:
                market = 1

        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        score = (
            trend
            + volume
            + momentum
            + pattern
            + sector
            + relative
            + market
        )

        score = round(
            min(
                score,
                100.0,
            ),
            2,
        )

        confidence = (
            score * 0.80
        )

        if adx >= 25:
            confidence += 4

        if volume_ratio >= 1.5:
            confidence += 4

        if direction == SignalType.BUY:

            if (
                sector_strength >= 70
                and relative_strength >= 70
            ):
                confidence += 7

        else:

            if (
                0 < sector_strength <= 30
                and 0 < relative_strength <= 30
            ):
                confidence += 7

        confidence = round(
            min(
                confidence,
                100.0,
            ),
            2,
        )

        score_breakdown = {

            "trend":
                round(
                    trend,
                    2,
                ),

            "volume":
                round(
                    volume,
                    2,
                ),

            "momentum":
                round(
                    momentum,
                    2,
                ),

            "pattern":
                round(
                    pattern,
                    2,
                ),

            "sector":
                round(
                    sector,
                    2,
                ),

            "relative_strength":
                round(
                    relative,
                    2,
                ),

            "market":
                round(
                    market,
                    2,
                ),
        }

        return (
            score,
            confidence,
            score_breakdown,
        )

    # =====================================================
    # STOP LOSS
    # =====================================================

    @staticmethod
    def _stop_loss(
        *,
        direction: SignalType,
        entry: float,
        atr: float,
        ema20: float,
        ema21: float,
        swing_low: float,
        swing_high: float,
    ) -> float:

        short_ema = (
            ema20
            if ema20 > 0
            else ema21
        )

        if direction == SignalType.BUY:

            candidates: List[float] = []

            if (
                swing_low > 0
                and swing_low < entry
            ):
                candidates.append(
                    swing_low
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
                    - atr * 1.5
                )

                if atr_stop > 0:

                    candidates.append(
                        atr_stop
                    )

            if not candidates:

                return (
                    entry * 0.98
                )

            return max(
                candidates
            )

        candidates = []

        if swing_high > entry:

            candidates.append(
                swing_high
            )

        if short_ema > entry:

            candidates.append(
                short_ema
            )

        if atr > 0:

            candidates.append(
                entry
                + atr * 1.5
            )

        if not candidates:

            return (
                entry * 1.02
            )

        return min(
            candidates
        )

    # =====================================================
    # TARGETS
    # =====================================================

    def _targets(
        self,
        *,
        direction: SignalType,
        entry: float,
        stop_loss: float,
    ) -> Tuple[
        float,
        float,
        float,
    ]:

        if direction == SignalType.BUY:

            risk = (
                entry
                - stop_loss
            )

            if risk <= 0:

                return (
                    0.0,
                    0.0,
                    0.0,
                )

            return (
                entry
                + risk * self.minimum_rr,

                entry
                + risk * 3.0,

                entry
                + risk * 4.0,
            )

        risk = (
            stop_loss
            - entry
        )

        if risk <= 0:

            return (
                0.0,
                0.0,
                0.0,
            )

        return (
            max(
                entry
                - risk * self.minimum_rr,
                0.01,
            ),

            max(
                entry
                - risk * 3.0,
                0.01,
            ),

            max(
                entry
                - risk * 4.0,
                0.01,
            ),
        )

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

            "minimum_adx":
                self.minimum_adx,

            "minimum_volume_ratio":
                self.minimum_volume_ratio,

            "strong_sector_score":
                self.strong_sector_score,

            "weak_sector_score":
                self.weak_sector_score,
        }


# =========================================================
# FACTORY
# =========================================================

def create_sector_rotation_scanner(
    **kwargs: Any,
) -> SectorRotationScanner:

    return SectorRotationScanner(
        **kwargs
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "SectorRotationScanner",
    "create_sector_rotation_scanner",
]


# =========================================================
# END OF FILE
# =========================================================
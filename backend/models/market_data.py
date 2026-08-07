from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class MarketData:

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    symbol: str

    exchange: str = "NSE"

    company_name: str = ""

    sector: str = ""

    industry: str = ""

    isin: str = ""

    market_cap: float = 0.0

    # =====================================================
    # LIVE PRICE
    # =====================================================

    ltp: float = 0.0

    open: float = 0.0

    high: float = 0.0

    low: float = 0.0

    close: float = 0.0

    previous_close: float = 0.0

    average_price: float = 0.0

    vwap: float = 0.0

    # =====================================================
    # VOLUME
    # =====================================================

    volume: int = 0

    average_volume: int = 0

    relative_volume: float = 0.0

    delivery_volume: int = 0

    delivery_percent: float = 0.0

    # =====================================================
    # PRICE CHANGE
    # =====================================================

    change: float = 0.0

    change_percent: float = 0.0

    gap_percent: float = 0.0

    day_range_percent: float = 0.0

    # =====================================================
    # MOVING AVERAGES
    # =====================================================

    ema9: float = 0.0

    ema20: float = 0.0

    ema21: float = 0.0

    ema34: float = 0.0

    ema50: float = 0.0

    ema100: float = 0.0

    ema200: float = 0.0

    sma20: float = 0.0

    sma50: float = 0.0

    sma100: float = 0.0

    sma200: float = 0.0

    # =====================================================
    # MOMENTUM INDICATORS
    # =====================================================

    rsi: float = 0.0

    macd: float = 0.0

    macd_signal: float = 0.0

    macd_histogram: float = 0.0

    adx: float = 0.0

    plus_di: float = 0.0

    minus_di: float = 0.0

    atr: float = 0.0

    supertrend: float = 0.0

    supertrend_direction: str = ""

    # =====================================================
    # VOLATILITY
    # =====================================================

    bollinger_upper: float = 0.0

    bollinger_middle: float = 0.0

    bollinger_lower: float = 0.0

    volatility: float = 0.0

    beta: float = 0.0

    # =====================================================
    # MARKET STRUCTURE
    # =====================================================

    support: float = 0.0

    resistance: float = 0.0

    pivot: float = 0.0

    pivot_r1: float = 0.0

    pivot_r2: float = 0.0

    pivot_s1: float = 0.0

    pivot_s2: float = 0.0

    # =====================================================
    # F&O
    # =====================================================

    futures_available: bool = False

    option_available: bool = False

    oi: int = 0

    oi_change: float = 0.0

    pcr: float = 0.0

    # =====================================================
    # AI SCORES
    # =====================================================

    ai_score: float = 0.0

    confidence: float = 0.0

    probability: float = 0.0

    trend_score: float = 0.0

    momentum_score: float = 0.0

    volume_score: float = 0.0

    quality_score: float = 0.0

    # =====================================================
    # SIGNALS
    # =====================================================

    signal: str = ""

    recommendation: str = ""

    pattern: str = ""

    timeframe: str = ""

    scanner_name: str = ""

    strategy: str = ""

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    # =====================================================
    # LIVE PROPERTIES
    # =====================================================

    @property
    def bullish(self):

        return self.signal.upper() == "BUY"

    # -----------------------------------------------------

    @property
    def bearish(self):

        return self.signal.upper() == "SELL"

    # -----------------------------------------------------

    @property
    def candle_range(self):

        return round(

            self.high - self.low,

            2,

        )

    # -----------------------------------------------------

    @property
    def body_size(self):

        return round(

            abs(self.close - self.open),

            2,

        )

    # -----------------------------------------------------

    @property
    def upper_wick(self):

        return round(

            self.high -

            max(

                self.open,

                self.close,

            ),

            2,

        )

    # -----------------------------------------------------

    @property
    def lower_wick(self):

        return round(

            min(

                self.open,

                self.close,

            )

            - self.low,

            2,

        )

    # -----------------------------------------------------

    @property
    def green_candle(self):

        return self.close > self.open

    # -----------------------------------------------------

    @property
    def red_candle(self):

        return self.close < self.open
        # =====================================================
    # PRICE CALCULATIONS
    # =====================================================

    def update_price(
        self,
        ltp,
    ):

        self.ltp = float(ltp)

        if self.previous_close:

            self.change = round(
                self.ltp - self.previous_close,
                2,
            )

            self.change_percent = round(
                (self.change / self.previous_close) * 100,
                2,
            )

        self.updated_at = datetime.now()

    # -----------------------------------------------------

    def calculate_gap(self):

        if self.previous_close == 0:
            return 0

        self.gap_percent = round(
            ((self.open - self.previous_close)
             / self.previous_close) * 100,
            2,
        )

        return self.gap_percent

    # -----------------------------------------------------

    def calculate_day_range(self):

        if self.low == 0:
            return 0

        self.day_range_percent = round(
            ((self.high - self.low) / self.low) * 100,
            2,
        )

        return self.day_range_percent

    # =====================================================
    # TREND
    # =====================================================

    def trend(self):

        if self.ema20 > self.ema50 > self.ema200:

            return "STRONG_UPTREND"

        if self.ema20 > self.ema50:

            return "UPTREND"

        if self.ema20 < self.ema50 < self.ema200:

            return "STRONG_DOWNTREND"

        if self.ema20 < self.ema50:

            return "DOWNTREND"

        return "SIDEWAYS"

    # -----------------------------------------------------

    def trend_strength(self):

        score = 0

        if self.ltp > self.ema20:
            score += 20

        if self.ltp > self.ema50:
            score += 20

        if self.ltp > self.ema200:
            score += 20

        if self.rsi > 60:
            score += 20

        if self.adx > 25:
            score += 20

        self.trend_score = score

        return score

    # =====================================================
    # EMA ALIGNMENT
    # =====================================================

    def ema_alignment(self):

        return (

            self.ema9 >
            self.ema20 >
            self.ema50 >
            self.ema200

        )

    # -----------------------------------------------------

    def sma_alignment(self):

        return (

            self.sma20 >
            self.sma50 >
            self.sma200

        )

    # =====================================================
    # BREAKOUTS
    # =====================================================

    def breakout(self):

        return (

            self.ltp >

            self.resistance

        )

    # -----------------------------------------------------

    def breakdown(self):

        return (

            self.ltp <

            self.support

        )

    # -----------------------------------------------------

    def above_vwap(self):

        return self.ltp > self.vwap

    # -----------------------------------------------------

    def below_vwap(self):

        return self.ltp < self.vwap

    # =====================================================
    # RSI
    # =====================================================

    def rsi_signal(self):

        if self.rsi >= 70:

            return "OVERBOUGHT"

        if self.rsi <= 30:

            return "OVERSOLD"

        if self.rsi >= 60:

            return "BULLISH"

        if self.rsi <= 40:

            return "BEARISH"

        return "NEUTRAL"

    # =====================================================
    # MACD
    # =====================================================

    def macd_bullish(self):

        return self.macd > self.macd_signal

    # -----------------------------------------------------

    def macd_bearish(self):

        return self.macd < self.macd_signal

    # =====================================================
    # ADX
    # =====================================================

    def strong_trend(self):

        return self.adx >= 25

    # -----------------------------------------------------

    def weak_trend(self):

        return self.adx < 20

    # =====================================================
    # VOLUME
    # =====================================================

    def high_volume(self):

        return self.relative_volume >= 2.0

    # -----------------------------------------------------

    def unusual_volume(self):

        return self.relative_volume >= 3.0

    # -----------------------------------------------------

    def delivery_strength(self):

        if self.delivery_percent >= 75:

            return "VERY_HIGH"

        if self.delivery_percent >= 60:

            return "HIGH"

        if self.delivery_percent >= 45:

            return "NORMAL"

        return "LOW"

    # -----------------------------------------------------

    def volume_strength(self):

        score = 0

        if self.relative_volume >= 2:
            score += 40

        if self.delivery_percent >= 60:
            score += 30

        if self.volume > self.average_volume:
            score += 30

        self.volume_score = score

        return score

    # =====================================================
    # RISK
    # =====================================================

    def volatility_level(self):

        if self.volatility >= 4:

            return "VERY_HIGH"

        if self.volatility >= 3:

            return "HIGH"

        if self.volatility >= 2:

            return "MEDIUM"

        return "LOW"

    # -----------------------------------------------------

    def atr_percent(self):

        if self.ltp == 0:

            return 0

        return round(

            (self.atr / self.ltp) * 100,

            2,

        )

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    def outperforming_market(self):

        return self.relative_strength > 1

    # -----------------------------------------------------

    def underperforming_market(self):

        return self.relative_strength < 1
        # =====================================================
    # AI SCORING
    # =====================================================

    def calculate_ai_score(self):

        score = 0.0

        # Trend (30%)
        score += self.trend_strength() * 0.30

        # Volume (20%)
        score += self.volume_strength() * 0.20

        # Momentum (20%)
        score += self.momentum_score * 0.20

        # RSI (15%)
        if 55 <= self.rsi <= 70:
            score += 15
        elif 45 <= self.rsi < 55:
            score += 8

        # ADX (15%)
        if self.adx >= 25:
            score += 15
        elif self.adx >= 20:
            score += 8

        self.ai_score = round(
            min(score, 100),
            2,
        )

        return self.ai_score

    # -----------------------------------------------------

    def calculate_confidence(self):

        confidence = 0

        if self.ema_alignment():
            confidence += 25

        if self.macd_bullish():
            confidence += 20

        if self.above_vwap():
            confidence += 15

        if self.high_volume():
            confidence += 20

        if self.strong_trend():
            confidence += 20

        self.confidence = min(
            confidence,
            100,
        )

        return self.confidence

    # -----------------------------------------------------

    def calculate_probability(self):

        self.probability = round(

            (
                self.ai_score * 0.6
                + self.confidence * 0.4
            ),

            2,

        )

        return self.probability

    # =====================================================
    # SIGNAL GENERATION
    # =====================================================

    def generate_signal(self):

        if (

            self.ema_alignment()

            and self.macd_bullish()

            and self.rsi > 55

            and self.above_vwap()

        ):

            self.signal = "BUY"

        elif (

            self.macd_bearish()

            and self.rsi < 45

            and self.below_vwap()

        ):

            self.signal = "SELL"

        else:

            self.signal = "WAIT"

        return self.signal

    # =====================================================
    # TRADE SETUP
    # =====================================================

    def suggested_entry(self):

        return round(
            self.ltp,
            2,
        )

    # -----------------------------------------------------

    def suggested_stop_loss(self):

        sl = max(

            self.support,

            self.ltp - (self.atr * 1.5),

        )

        return round(
            sl,
            2,
        )

    # -----------------------------------------------------

    def suggested_target(

        self,

        rr=2,

    ):

        risk = (

            self.suggested_entry()

            -

            self.suggested_stop_loss()

        )

        target = (

            self.suggested_entry()

            +

            risk * rr

        )

        return round(
            target,
            2,
        )

    # -----------------------------------------------------

    def risk_reward(

        self,

        rr=2,

    ):

        risk = (

            self.suggested_entry()

            -

            self.suggested_stop_loss()

        )

        reward = (

            self.suggested_target(rr)

            -

            self.suggested_entry()

        )

        if risk <= 0:

            return 0

        return round(

            reward / risk,

            2,

        )

    # =====================================================
    # POSITION SIZE
    # =====================================================

    def quantity(

        self,

        capital,

        risk_percent=1,

    ):

        risk_amount = (

            capital * risk_percent

        ) / 100

        risk_per_share = (

            self.suggested_entry()

            -

            self.suggested_stop_loss()

        )

        if risk_per_share <= 0:

            return 0

        return int(

            risk_amount

            / risk_per_share

        )

    # =====================================================
    # SCANNER SCORE
    # =====================================================

    def scanner_score(self):

        score = (

            self.ai_score * 0.4

            + self.confidence * 0.3

            + self.probability * 0.3

        )

        return round(
            score,
            2,
        )

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_row(self):

        return [

            self.symbol,

            self.signal,

            round(self.ltp, 2),

            round(self.change_percent, 2),

            round(self.relative_volume, 2),

            round(self.ai_score, 2),

            round(self.confidence, 2),

            round(self.probability, 2),

            self.pattern,

        ]

    # -----------------------------------------------------

    def compact_summary(self):

        return {

            "symbol": self.symbol,

            "price": self.ltp,

            "signal": self.signal,

            "score": self.scanner_score(),

            "pattern": self.pattern,

            "confidence": self.confidence,

        }

    # =====================================================
    # UPDATE AI
    # =====================================================

    def refresh_ai(self):

        self.calculate_ai_score()

        self.calculate_confidence()

        self.calculate_probability()

        self.generate_signal()

        self.updated_at = datetime.now()

        return self.ai_score
        # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        if not self.symbol:
            return False

        if self.ltp < 0:
            return False

        if self.high < self.low:
            return False

        if self.volume < 0:
            return False

        return True

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self):

        return {

            key: (
                value.isoformat()
                if isinstance(value, datetime)
                else value
            )

            for key, value in self.__dict__.items()

        }

    # -----------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data,
    ):

        data = dict(data)

        for field_name in (
            "created_at",
            "updated_at",
        ):

            value = data.get(field_name)

            if isinstance(value, str):

                data[field_name] = datetime.fromisoformat(
                    value
                )

        return cls(**data)

    # -----------------------------------------------------

    def to_json(self):

        import json

        return json.dumps(
            self.to_dict(),
            indent=4,
            default=str,
        )

    # -----------------------------------------------------

    @classmethod
    def from_json(
        cls,
        json_string,
    ):

        import json

        return cls.from_dict(
            json.loads(json_string)
        )

    # =====================================================
    # COPY
    # =====================================================

    def clone(self):

        return MarketData.from_dict(
            self.to_dict()
        )

    # -----------------------------------------------------

    def update_from(
        self,
        other,
    ):

        if not isinstance(other, MarketData):
            return

        for key, value in other.to_dict().items():

            if key in (
                "created_at",
                "updated_at",
            ):
                continue

            setattr(
                self,
                key,
                value,
            )

        self.updated_at = datetime.now()

    # =====================================================
    # FACTORY METHODS
    # =====================================================

    @staticmethod
    def empty():

        return MarketData(
            symbol="",
        )

    # -----------------------------------------------------

    @staticmethod
    def from_symbol(
        symbol,
    ):

        return MarketData(
            symbol=symbol.upper(),
        )

    # =====================================================
    # COMPARISON
    # =====================================================

    def sort_key(self):

        return (

            self.scanner_score(),

            self.ai_score,

            self.confidence,

            self.relative_volume,

            self.change_percent,

        )

    # -----------------------------------------------------

    def __lt__(
        self,
        other,
    ):

        if not isinstance(other, MarketData):
            return NotImplemented

        return self.sort_key() < other.sort_key()

    # -----------------------------------------------------

    def __eq__(
        self,
        other,
    ):

        if not isinstance(other, MarketData):
            return False

        return self.symbol == other.symbol

    # -----------------------------------------------------

    def __hash__(self):

        return hash(self.symbol)

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================

    def short_summary(self):

        return (
            f"{self.symbol} | "
            f"{self.signal} | "
            f"{self.ltp:.2f}"
        )

    # -----------------------------------------------------

    def full_summary(self):

        return (
            f"{self.symbol}\n"
            f"Price : {self.ltp:.2f}\n"
            f"Change : {self.change_percent:.2f}%\n"
            f"Signal : {self.signal}\n"
            f"Pattern : {self.pattern}\n"
            f"AI Score : {self.ai_score:.2f}\n"
            f"Confidence : {self.confidence:.2f}%\n"
            f"Probability : {self.probability:.2f}%"
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            "MarketData("
            f"symbol='{self.symbol}', "
            f"price={self.ltp:.2f}, "
            f"signal='{self.signal}', "
            f"score={self.ai_score:.2f})"
        )

    # -----------------------------------------------------

    def __str__(self):

        return self.full_summary()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "MarketData",

]
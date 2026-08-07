from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# MARKET REGIME
# ==========================================================

class MarketRegime(Enum):

    STRONG_BULL = "STRONG_BULL"

    BULL = "BULL"

    SIDEWAYS = "SIDEWAYS"

    BEAR = "BEAR"

    STRONG_BEAR = "STRONG_BEAR"

    HIGH_VOLATILITY = "HIGH_VOLATILITY"

    LOW_VOLATILITY = "LOW_VOLATILITY"


# ==========================================================
# TREND STRENGTH
# ==========================================================

class TrendStrength(Enum):

    VERY_WEAK = "VERY_WEAK"

    WEAK = "WEAK"

    MODERATE = "MODERATE"

    STRONG = "STRONG"

    VERY_STRONG = "VERY_STRONG"


# ==========================================================
# VOLATILITY REGIME
# ==========================================================

class VolatilityRegime(Enum):

    VERY_LOW = "VERY_LOW"

    LOW = "LOW"

    NORMAL = "NORMAL"

    HIGH = "HIGH"

    EXTREME = "EXTREME"


# ==========================================================
# DETECTOR CONFIG
# ==========================================================

@dataclass(slots=True)
class RegimeConfig:

    ema_fast: int = 20

    ema_slow: int = 50

    ema_long: int = 200

    adx_period: int = 14

    atr_period: int = 14

    rsi_period: int = 14

    volatility_period: int = 20

    trend_threshold: float = 25.0

    high_vix: float = 20.0

    low_vix: float = 13.0


# ==========================================================
# REGIME RESULT
# ==========================================================

@dataclass(slots=True)
class RegimeResult:

    regime: MarketRegime

    trend_strength: TrendStrength

    volatility: VolatilityRegime

    score: float

    confidence: float

    details: Dict

    timestamp: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# MARKET REGIME DETECTOR
# ==========================================================

class MarketRegimeDetector:

    VERSION = "4.0"

    def __init__(self):

        self.lock = threading.RLock()

        self.config = RegimeConfig()

        self.data: Optional[pd.DataFrame] = None

        self.symbol = ""

        self.vix = None

        self.result: Optional[
            RegimeResult
        ] = None

        self.history: List[
            RegimeResult
        ] = []

        self.running = False
            # ==========================================================
    # CONFIGURE
    # ==========================================================

    def configure(

        self,

        config: RegimeConfig,

    ) -> None:

        self.config = config

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_data(

        self,

        symbol: str,

        dataframe: pd.DataFrame,

    ) -> None:

        self.symbol = symbol

        self.data = dataframe.copy()

    # ==========================================================
    # LOAD VIX
    # ==========================================================

    def load_vix(

        self,

        vix_value: float,

    ) -> None:

        self.vix = float(

            vix_value

        )

    # ==========================================================
    # HAS DATA
    # ==========================================================

    def has_data(

        self,

    ) -> bool:

        return (

            self.data is not None

            and

            not self.data.empty

        )

    # ==========================================================
    # VALIDATE
    # ==========================================================

    def validate(

        self,

    ) -> None:

        if not self.has_data():

            raise ValueError(

                "Market data not loaded."

            )

        required = [

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

        ]

        for column in required:

            if column not in self.data.columns:

                raise ValueError(

                    f"Missing required column: {column}"

                )

    # ==========================================================
    # EMA
    # ==========================================================

    def ema(

        self,

        period: int,

    ) -> pd.Series:

        return self.data["Close"].ewm(

            span=period,

            adjust=False,

        ).mean()

    # ==========================================================
    # ATR
    # ==========================================================

    def atr(

        self,

        period: Optional[int] = None,

    ) -> pd.Series:

        if period is None:

            period = self.config.atr_period

        high = self.data["High"]

        low = self.data["Low"]

        close = self.data["Close"]

        tr = pd.concat(

            [

                high - low,

                (high - close.shift()).abs(),

                (low - close.shift()).abs(),

            ],

            axis=1,

        ).max(

            axis=1

        )

        return tr.rolling(

            period

        ).mean()

    # ==========================================================
    # RSI
    # ==========================================================

    def rsi(

        self,

        period: Optional[int] = None,

    ) -> pd.Series:

        if period is None:

            period = self.config.rsi_period

        delta = self.data["Close"].diff()

        gain = delta.clip(

            lower=0

        )

        loss = -delta.clip(

            upper=0

        )

        avg_gain = gain.rolling(

            period

        ).mean()

        avg_loss = loss.rolling(

            period

        ).mean()

        rs = avg_gain / avg_loss.replace(

            0,

            np.nan,

        )

        return 100 - (

            100

            /

            (

                1 + rs

            )

        )

    # ==========================================================
    # ADX
    # ==========================================================

    def adx(

        self,

        period: Optional[int] = None,

    ) -> pd.Series:

        if period is None:

            period = self.config.adx_period

        high = self.data["High"]

        low = self.data["Low"]

        plus_dm = high.diff()

        minus_dm = -low.diff()

        plus_dm = plus_dm.where(

            (

                plus_dm > minus_dm

            )

            &

            (

                plus_dm > 0

            ),

            0.0,

        )

        minus_dm = minus_dm.where(

            (

                minus_dm > plus_dm

            )

            &

            (

                minus_dm > 0

            ),

            0.0,

        )

        atr = self.atr(

            period

        )

        plus_di = (

            100

            *

            plus_dm.rolling(

                period

            ).sum()

            /

            atr

        )

        minus_di = (

            100

            *

            minus_dm.rolling(

                period

            ).sum()

            /

            atr

        )

        dx = (

            (

                plus_di

                -

                minus_di

            ).abs()

            /

            (

                plus_di

                +

                minus_di

            )

        ) * 100

        return dx.rolling(

            period

        ).mean()

    # ==========================================================
    # VOLATILITY
    # ==========================================================

    def volatility(

        self,

        period: Optional[int] = None,

    ) -> pd.Series:

        if period is None:

            period = self.config.volatility_period

        returns = self.data[

            "Close"

        ].pct_change()

        return (

            returns.rolling(

                period

            ).std()

            *

            np.sqrt(

                252

            )

        )

    # ==========================================================
    # LAST VALUE
    # ==========================================================

    def latest(

        self,

        series: pd.Series,

    ) -> float:

        return float(

            series.dropna().iloc[-1]

        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ) -> None:

        self.result = None

        self.history.clear()

        self.running = False
            # ==========================================================
    # TREND DIRECTION
    # ==========================================================

    def trend_direction(

        self,

    ) -> str:

        ema20 = self.latest(

            self.ema(

                self.config.ema_fast

            )

        )

        ema50 = self.latest(

            self.ema(

                self.config.ema_slow

            )

        )

        ema200 = self.latest(

            self.ema(

                self.config.ema_long

            )

        )

        close = float(

            self.data["Close"].iloc[-1]

        )

        if (

            close > ema20 > ema50 > ema200

        ):

            return "UP"

        if (

            close < ema20 < ema50 < ema200

        ):

            return "DOWN"

        return "SIDEWAYS"

    # ==========================================================
    # EMA ALIGNMENT SCORE
    # ==========================================================

    def ema_alignment_score(

        self,

    ) -> float:

        ema20 = self.latest(

            self.ema(

                self.config.ema_fast

            )

        )

        ema50 = self.latest(

            self.ema(

                self.config.ema_slow

            )

        )

        ema200 = self.latest(

            self.ema(

                self.config.ema_long

            )

        )

        close = float(

            self.data["Close"].iloc[-1]

        )

        score = 0

        if close > ema20:

            score += 25

        if ema20 > ema50:

            score += 25

        if ema50 > ema200:

            score += 25

        if close > ema200:

            score += 25

        return float(score)

    # ==========================================================
    # TREND STRENGTH
    # ==========================================================

    def trend_strength(

        self,

    ) -> TrendStrength:

        adx = self.latest(

            self.adx()

        )

        if adx < 15:

            return TrendStrength.VERY_WEAK

        if adx < 20:

            return TrendStrength.WEAK

        if adx < 30:

            return TrendStrength.MODERATE

        if adx < 40:

            return TrendStrength.STRONG

        return TrendStrength.VERY_STRONG

    # ==========================================================
    # MOMENTUM SCORE
    # ==========================================================

    def momentum_score(

        self,

    ) -> float:

        rsi = self.latest(

            self.rsi()

        )

        score = 50.0

        if rsi >= 70:

            score = 100

        elif rsi >= 60:

            score = 80

        elif rsi >= 50:

            score = 60

        elif rsi >= 40:

            score = 40

        elif rsi >= 30:

            score = 20

        else:

            score = 0

        return float(score)

    # ==========================================================
    # VOLATILITY REGIME
    # ==========================================================

    def volatility_regime(

        self,

    ) -> VolatilityRegime:

        vol = self.latest(

            self.volatility()

        )

        if vol < 0.10:

            return VolatilityRegime.VERY_LOW

        if vol < 0.20:

            return VolatilityRegime.LOW

        if vol < 0.30:

            return VolatilityRegime.NORMAL

        if vol < 0.45:

            return VolatilityRegime.HIGH

        return VolatilityRegime.EXTREME

    # ==========================================================
    # VIX REGIME
    # ==========================================================

    def vix_regime(

        self,

    ) -> str:

        if self.vix is None:

            return "UNKNOWN"

        if self.vix < self.config.low_vix:

            return "LOW"

        if self.vix > self.config.high_vix:

            return "HIGH"

        return "NORMAL"

    # ==========================================================
    # MARKET BREADTH SCORE
    # ==========================================================

    def market_breadth_score(

        self,

    ) -> float:

        closes = self.data["Close"]

        ema50 = self.ema(

            self.config.ema_slow

        )

        above = (

            closes > ema50

        ).sum()

        total = len(

            closes

        )

        if total == 0:

            return 0.0

        return round(

            (

                above

                /

                total

            )

            * 100,

            2,

        )

    # ==========================================================
    # TREND SCORE
    # ==========================================================

    def trend_score(

        self,

    ) -> float:

        score = 0.0

        score += self.ema_alignment_score() * 0.50

        score += self.momentum_score() * 0.30

        adx = self.latest(

            self.adx()

        )

        score += min(

            adx,

            50,

        ) * 0.40

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # INITIAL REGIME SCORE
    # ==========================================================

    def regime_score(

        self,

    ) -> float:

        trend = self.trend_score()

        breadth = self.market_breadth_score()

        return round(

            (

                trend * 0.70

                +

                breadth * 0.30

            ),

            2,

        )

    # ==========================================================
    # CONFIDENCE SCORE
    # ==========================================================

    def confidence_score(

        self,

    ) -> float:

        score = self.regime_score()

        strength = self.trend_strength()

        bonus = {

            TrendStrength.VERY_WEAK: 0,

            TrendStrength.WEAK: 5,

            TrendStrength.MODERATE: 10,

            TrendStrength.STRONG: 15,

            TrendStrength.VERY_STRONG: 20,

        }

        confidence = min(

            score + bonus[strength],

            100,

        )

        return round(

            confidence,

            2,

        )
        # ==========================================================
    # MARKET REGIME CLASSIFICATION
    # ==========================================================

    def classify_regime(

        self,

    ) -> MarketRegime:

        direction = self.trend_direction()

        score = self.regime_score()

        volatility = self.volatility_regime()

        if volatility == VolatilityRegime.EXTREME:

            return MarketRegime.HIGH_VOLATILITY

        if direction == "UP":

            if score >= 80:

                return MarketRegime.STRONG_BULL

            return MarketRegime.BULL

        if direction == "DOWN":

            if score >= 80:

                return MarketRegime.STRONG_BEAR

            return MarketRegime.BEAR

        return MarketRegime.SIDEWAYS

    # ==========================================================
    # TREND TRANSITION
    # ==========================================================

    def trend_transition(

        self,

    ) -> str:

        ema20 = self.ema(

            self.config.ema_fast

        )

        ema50 = self.ema(

            self.config.ema_slow

        )

        if len(ema20) < 2:

            return "UNKNOWN"

        previous_fast = ema20.iloc[-2]

        previous_slow = ema50.iloc[-2]

        current_fast = ema20.iloc[-1]

        current_slow = ema50.iloc[-1]

        if (

            previous_fast < previous_slow

            and

            current_fast > current_slow

        ):

            return "BULLISH_CROSSOVER"

        if (

            previous_fast > previous_slow

            and

            current_fast < current_slow

        ):

            return "BEARISH_CROSSOVER"

        return "NO_CHANGE"

    # ==========================================================
    # VOLATILITY SHOCK
    # ==========================================================

    def volatility_shock(

        self,

    ) -> bool:

        vol = self.volatility()

        if len(vol.dropna()) < 10:

            return False

        latest = float(

            vol.iloc[-1]

        )

        average = float(

            vol.iloc[-10:-1].mean()

        )

        if average == 0:

            return False

        return latest > average * 1.50

    # ==========================================================
    # BREAKOUT / MEAN REVERSION
    # ==========================================================

    def market_behavior(

        self,

    ) -> str:

        score = self.regime_score()

        adx = self.latest(

            self.adx()

        )

        if score >= 70 and adx >= 25:

            return "BREAKOUT"

        if score <= 45 and adx < 20:

            return "MEAN_REVERSION"

        return "NEUTRAL"

    # ==========================================================
    # SECTOR STRENGTH
    # ==========================================================

    def sector_strength(

        self,

        sector_score: Optional[float] = None,

    ) -> float:

        if sector_score is None:

            return 50.0

        return max(

            0.0,

            min(

                float(sector_score),

                100.0,

            ),

        )

    # ==========================================================
    # BUILD MARKET STATE
    # ==========================================================

    def build_state(

        self,

        sector_score: Optional[float] = None,

    ) -> Dict:

        return {

            "symbol":

                self.symbol,

            "regime":

                self.classify_regime().value,

            "direction":

                self.trend_direction(),

            "trend_strength":

                self.trend_strength().value,

            "trend_score":

                self.trend_score(),

            "regime_score":

                self.regime_score(),

            "confidence":

                self.confidence_score(),

            "volatility":

                self.volatility_regime().value,

            "vix":

                self.vix_regime(),

            "behavior":

                self.market_behavior(),

            "transition":

                self.trend_transition(),

            "volatility_shock":

                self.volatility_shock(),

            "sector_strength":

                self.sector_strength(

                    sector_score

                ),

        }

    # ==========================================================
    # SAVE RESULT
    # ==========================================================

    def record_result(

        self,

        sector_score: Optional[float] = None,

    ) -> RegimeResult:

        state = self.build_state(

            sector_score

        )

        result = RegimeResult(

            regime=self.classify_regime(),

            trend_strength=self.trend_strength(),

            volatility=self.volatility_regime(),

            score=state["regime_score"],

            confidence=state["confidence"],

            details=state,

        )

        self.result = result

        self.history.append(

            result

        )

        return result

    # ==========================================================
    # LAST RESULT
    # ==========================================================

    def latest_result(

        self,

    ) -> Optional[RegimeResult]:

        return self.result

    # ==========================================================
    # HISTORY
    # ==========================================================

    def detection_history(

        self,

    ) -> List[RegimeResult]:

        return list(

            self.history

        )

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    def clear_history(

        self,

    ) -> None:

        self.history.clear()
            # ==========================================================
    # NIFTY REGIME SCORE
    # ==========================================================

    def nifty_score(

        self,

    ) -> float:

        score = self.regime_score()

        if self.vix is not None:

            if self.vix > self.config.high_vix:

                score -= 10

            elif self.vix < self.config.low_vix:

                score += 5

        return round(

            max(

                0.0,

                min(

                    score,

                    100.0,

                ),

            ),

            2,

        )

    # ==========================================================
    # BANK NIFTY SCORE
    # ==========================================================

    def banknifty_score(

        self,

        bank_strength: float = 50.0,

    ) -> float:

        score = (

            self.nifty_score() * 0.70

            +

            bank_strength * 0.30

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # MULTI-TIMEFRAME CONFIRMATION
    # ==========================================================

    def multi_timeframe_confirmation(

        self,

        timeframe_states: Dict[str, str],

    ) -> Dict:

        bullish = 0

        bearish = 0

        sideways = 0

        total = len(

            timeframe_states

        )

        for regime in timeframe_states.values():

            if regime in (

                "BULL",

                "STRONG_BULL",

            ):

                bullish += 1

            elif regime in (

                "BEAR",

                "STRONG_BEAR",

            ):

                bearish += 1

            else:

                sideways += 1

        if bullish >= max(

            bearish,

            sideways,

        ):

            dominant = "BULL"

        elif bearish >= sideways:

            dominant = "BEAR"

        else:

            dominant = "SIDEWAYS"

        confidence = (

            max(

                bullish,

                bearish,

                sideways,

            )

            /

            max(

                total,

                1,

            )

        ) * 100

        return {

            "dominant": dominant,

            "bullish": bullish,

            "bearish": bearish,

            "sideways": sideways,

            "confidence": round(

                confidence,

                2,

            ),

        }

    # ==========================================================
    # RELATIVE STRENGTH
    # ==========================================================

    def relative_strength(

        self,

        benchmark_close: pd.Series,

    ) -> float:

        asset_return = (

            self.data["Close"].iloc[-1]

            /

            self.data["Close"].iloc[0]

        ) - 1

        benchmark_return = (

            benchmark_close.iloc[-1]

            /

            benchmark_close.iloc[0]

        ) - 1

        rs = (

            asset_return

            -

            benchmark_return

        ) * 100

        return round(

            rs,

            2,

        )

    # ==========================================================
    # INSTITUTIONAL FLOW SCORE
    # ==========================================================

    def institutional_flow_score(

        self,

        fii_net: float = 0.0,

        dii_net: float = 0.0,

    ) -> float:

        total = fii_net + dii_net

        if total >= 5000:

            return 100.0

        if total >= 2000:

            return 80.0

        if total >= 0:

            return 60.0

        if total >= -2000:

            return 40.0

        return 20.0

    # ==========================================================
    # FII/DII SENTIMENT
    # ==========================================================

    def fii_dii_sentiment(

        self,

        fii_net: float,

        dii_net: float,

    ) -> str:

        total = fii_net + dii_net

        if total > 5000:

            return "STRONGLY_BULLISH"

        if total > 1000:

            return "BULLISH"

        if total > -1000:

            return "NEUTRAL"

        if total > -5000:

            return "BEARISH"

        return "STRONGLY_BEARISH"

    # ==========================================================
    # MARKET HEALTH SCORE
    # ==========================================================

    def market_health_score(

        self,

        fii_net: float = 0,

        dii_net: float = 0,

        sector_strength: float = 50,

    ) -> float:

        regime = self.regime_score()

        trend = self.trend_score()

        flow = self.institutional_flow_score(

            fii_net,

            dii_net,

        )

        health = (

            regime * 0.35

            +

            trend * 0.30

            +

            flow * 0.20

            +

            sector_strength * 0.15

        )

        return round(

            min(

                health,

                100,

            ),

            2,

        )

    # ==========================================================
    # REFINED CONFIDENCE
    # ==========================================================

    def refined_confidence(

        self,

        fii_net: float = 0,

        dii_net: float = 0,

        sector_strength: float = 50,

    ) -> float:

        confidence = self.confidence_score()

        health = self.market_health_score(

            fii_net,

            dii_net,

            sector_strength,

        )

        return round(

            (

                confidence * 0.60

                +

                health * 0.40

            ),

            2,

        )

    # ==========================================================
    # COMPOSITE MARKET REPORT
    # ==========================================================

    def composite_market_report(

        self,

        fii_net: float = 0,

        dii_net: float = 0,

        sector_strength: float = 50,

    ) -> Dict:

        return {

            "regime":

                self.classify_regime().value,

            "trend":

                self.trend_direction(),

            "trend_strength":

                self.trend_strength().value,

            "nifty_score":

                self.nifty_score(),

            "market_health":

                self.market_health_score(

                    fii_net,

                    dii_net,

                    sector_strength,

                ),

            "confidence":

                self.refined_confidence(

                    fii_net,

                    dii_net,

                    sector_strength,

                ),

            "institutional_sentiment":

                self.fii_dii_sentiment(

                    fii_net,

                    dii_net,

                ),

            "institutional_flow_score":

                self.institutional_flow_score(

                    fii_net,

                    dii_net,

                ),

            "behavior":

                self.market_behavior(),

        }
        # ==========================================================
    # HIDDEN MARKOV MODEL (PLACEHOLDER)
    # ==========================================================

    def hmm_prediction(

        self,

    ) -> Dict:

        # Future Integration:
        # hmmlearn
        # pomegranate
        # pyhsmm

        return {

            "predicted_regime":

                self.classify_regime().value,

            "confidence":

                self.confidence_score(),

            "model":

                "Placeholder",

        }

    # ==========================================================
    # REGIME PROBABILITIES
    # ==========================================================

    def regime_probabilities(

        self,

    ) -> Dict[str, float]:

        score = self.regime_score()

        direction = self.trend_direction()

        probabilities = {

            "STRONG_BULL": 0.0,

            "BULL": 0.0,

            "SIDEWAYS": 0.0,

            "BEAR": 0.0,

            "STRONG_BEAR": 0.0,

        }

        if direction == "UP":

            probabilities["STRONG_BULL"] = min(

                score,

                100,

            ) / 100

            probabilities["BULL"] = 1 - probabilities["STRONG_BULL"]

        elif direction == "DOWN":

            probabilities["STRONG_BEAR"] = min(

                score,

                100,

            ) / 100

            probabilities["BEAR"] = 1 - probabilities["STRONG_BEAR"]

        else:

            probabilities["SIDEWAYS"] = 1.0

        return probabilities

    # ==========================================================
    # TRANSITION MATRIX
    # ==========================================================

    def transition_matrix(

        self,

    ) -> pd.DataFrame:

        states = [

            "STRONG_BULL",

            "BULL",

            "SIDEWAYS",

            "BEAR",

            "STRONG_BEAR",

        ]

        matrix = np.eye(

            len(states)

        )

        return pd.DataFrame(

            matrix,

            index=states,

            columns=states,

        )

    # ==========================================================
    # FORECAST NEXT REGIME
    # ==========================================================

    def forecast_regime(

        self,

        bars_ahead: int = 5,

    ) -> Dict:

        current = self.classify_regime()

        confidence = max(

            self.confidence_score()

            -

            bars_ahead * 2,

            20,

        )

        return {

            "current":

                current.value,

            "forecast":

                current.value,

            "bars_ahead":

                bars_ahead,

            "confidence":

                round(

                    confidence,

                    2,

                ),

        }

    # ==========================================================
    # STRATEGY RECOMMENDATION
    # ==========================================================

    def strategy_recommendation(

        self,

    ) -> Dict:

        regime = self.classify_regime()

        recommendations = {

            MarketRegime.STRONG_BULL: {

                "strategy":

                    "Trend Following",

                "bias":

                    "LONG",

                "risk":

                    "HIGH",

            },

            MarketRegime.BULL: {

                "strategy":

                    "Pullback Buy",

                "bias":

                    "LONG",

                "risk":

                    "MEDIUM",

            },

            MarketRegime.SIDEWAYS: {

                "strategy":

                    "Mean Reversion",

                "bias":

                    "BOTH",

                "risk":

                    "LOW",

            },

            MarketRegime.BEAR: {

                "strategy":

                    "Sell on Rise",

                "bias":

                    "SHORT",

                "risk":

                    "MEDIUM",

            },

            MarketRegime.STRONG_BEAR: {

                "strategy":

                    "Trend Following",

                "bias":

                    "SHORT",

                "risk":

                    "HIGH",

            },

            MarketRegime.HIGH_VOLATILITY: {

                "strategy":

                    "Volatility Breakout",

                "bias":

                    "REDUCED SIZE",

                "risk":

                    "VERY_HIGH",

            },

            MarketRegime.LOW_VOLATILITY: {

                "strategy":

                    "Range Trading",

                "bias":

                    "BOTH",

                "risk":

                    "LOW",

            },

        }

        return recommendations.get(

            regime,

            {},

        )

    # ==========================================================
    # SCANNER FILTERS
    # ==========================================================

    def scanner_filters(

        self,

    ) -> Dict:

        regime = self.classify_regime()

        if regime in (

            MarketRegime.BULL,

            MarketRegime.STRONG_BULL,

        ):

            return {

                "patterns": [

                    "Bull Flag",

                    "VCP",

                    "Cup & Handle",

                    "ORB",

                ],

                "minimum_rvol": 1.5,

            }

        if regime in (

            MarketRegime.BEAR,

            MarketRegime.STRONG_BEAR,

        ):

            return {

                "patterns": [

                    "Breakdown",

                    "Bear Flag",

                    "Lower High",

                ],

                "minimum_rvol": 2.0,

            }

        return {

            "patterns": [

                "Range Breakout",

                "Inside Bar",

            ],

            "minimum_rvol": 1.2,

        }

    # ==========================================================
    # RISK ALLOCATION
    # ==========================================================

    def risk_allocation(

        self,

        capital: float,

    ) -> Dict:

        confidence = self.confidence_score()

        regime = self.classify_regime()

        if regime == MarketRegime.HIGH_VOLATILITY:

            allocation = capital * 0.20

        elif confidence >= 80:

            allocation = capital * 0.50

        elif confidence >= 60:

            allocation = capital * 0.35

        else:

            allocation = capital * 0.20

        return {

            "capital": capital,

            "recommended_position": round(

                allocation,

                2,

            ),

            "position_percent": round(

                allocation

                /

                capital

                * 100,

                2,

            ),

        }

    # ==========================================================
    # AI MARKET REPORT
    # ==========================================================

    def ai_market_report(

        self,

        capital: float,

    ) -> Dict:

        return {

            "prediction":

                self.hmm_prediction(),

            "probabilities":

                self.regime_probabilities(),

            "forecast":

                self.forecast_regime(),

            "recommendation":

                self.strategy_recommendation(),

            "scanner":

                self.scanner_filters(),

            "risk":

                self.risk_allocation(

                    capital

                ),

        }
        # ==========================================================
    # SECTOR ROTATION SCORE
    # ==========================================================

    def sector_rotation_score(

        self,

        sector_returns: Dict[str, float],

    ) -> Dict:

        if not sector_returns:

            return {

                "leader": None,

                "laggard": None,

                "score": 50.0,

            }

        leader = max(

            sector_returns,

            key=sector_returns.get,

        )

        laggard = min(

            sector_returns,

            key=sector_returns.get,

        )

        values = list(

            sector_returns.values()

        )

        score = np.mean(

            values

        ) * 10 + 50

        score = max(

            0,

            min(

                score,

                100,

            ),

        )

        return {

            "leader": leader,

            "laggard": laggard,

            "score": round(

                score,

                2,

            ),

        }

    # ==========================================================
    # LEADERSHIP DETECTION
    # ==========================================================

    def leadership_strength(

        self,

        sector_returns: Dict[str, float],

    ) -> str:

        if not sector_returns:

            return "UNKNOWN"

        best = max(

            sector_returns.values()

        )

        if best >= 5:

            return "VERY_STRONG"

        if best >= 3:

            return "STRONG"

        if best >= 1:

            return "MODERATE"

        return "WEAK"

    # ==========================================================
    # ADVANCE / DECLINE RATIO
    # ==========================================================

    def advance_decline_ratio(

        self,

        advancing: int,

        declining: int,

    ) -> float:

        if declining == 0:

            return float(

                advancing

            )

        return round(

            advancing

            /

            declining,

            2,

        )

    # ==========================================================
    # BREADTH STATUS
    # ==========================================================

    def breadth_status(

        self,

        advancing: int,

        declining: int,

    ) -> str:

        ratio = self.advance_decline_ratio(

            advancing,

            declining,

        )

        if ratio >= 2:

            return "VERY_BULLISH"

        if ratio >= 1.2:

            return "BULLISH"

        if ratio >= 0.8:

            return "NEUTRAL"

        if ratio >= 0.5:

            return "BEARISH"

        return "VERY_BEARISH"

    # ==========================================================
    # VOLUME PARTICIPATION
    # ==========================================================

    def volume_participation(

        self,

    ) -> float:

        volume = self.data["Volume"]

        avg20 = volume.rolling(

            20

        ).mean()

        latest = float(

            volume.iloc[-1]

        )

        average = float(

            avg20.iloc[-1]

        )

        if average <= 0:

            return 1.0

        return round(

            latest

            /

            average,

            2,

        )

    # ==========================================================
    # ACCUMULATION DETECTION
    # ==========================================================

    def accumulation_phase(

        self,

    ) -> bool:

        close = self.data["Close"]

        volume = self.data["Volume"]

        avg_vol = volume.rolling(

            20

        ).mean()

        latest_close = close.iloc[-1]

        ema20 = self.ema(

            self.config.ema_fast

        ).iloc[-1]

        latest_volume = volume.iloc[-1]

        if (

            latest_close > ema20

            and

            latest_volume > avg_vol.iloc[-1] * 1.5

        ):

            return True

        return False

    # ==========================================================
    # DISTRIBUTION DETECTION
    # ==========================================================

    def distribution_phase(

        self,

    ) -> bool:

        close = self.data["Close"]

        volume = self.data["Volume"]

        avg_vol = volume.rolling(

            20

        ).mean()

        ema20 = self.ema(

            self.config.ema_fast

        ).iloc[-1]

        if (

            close.iloc[-1] < ema20

            and

            volume.iloc[-1] > avg_vol.iloc[-1] * 1.5

        ):

            return True

        return False

    # ==========================================================
    # MARKET PARTICIPATION SCORE
    # ==========================================================

    def participation_score(

        self,

        advancing: int,

        declining: int,

    ) -> float:

        breadth = self.advance_decline_ratio(

            advancing,

            declining,

        )

        volume = self.volume_participation()

        score = (

            min(

                breadth,

                3,

            )

            / 3

        ) * 50

        score += min(

            volume,

            2,

        ) / 2 * 50

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # COMPOSITE SECTOR SCORE
    # ==========================================================

    def composite_sector_score(

        self,

        sector_returns: Dict[str, float],

        advancing: int,

        declining: int,

    ) -> Dict:

        rotation = self.sector_rotation_score(

            sector_returns

        )

        participation = self.participation_score(

            advancing,

            declining,

        )

        composite = (

            rotation["score"] * 0.60

            +

            participation * 0.40

        )

        return {

            "rotation_score": rotation["score"],

            "leader": rotation["leader"],

            "laggard": rotation["laggard"],

            "leadership":

                self.leadership_strength(

                    sector_returns

                ),

            "breadth":

                self.breadth_status(

                    advancing,

                    declining,

                ),

            "participation":

                participation,

            "accumulation":

                self.accumulation_phase(),

            "distribution":

                self.distribution_phase(),

            "composite_score":

                round(

                    composite,

                    2,

                ),

        }
        # ==========================================================
    # SWING HIGHS
    # ==========================================================

    def swing_highs(

        self,

        lookback: int = 5,

    ) -> pd.Series:

        highs = self.data["High"]

        return highs.where(

            highs == highs.rolling(

                lookback * 2 + 1,

                center=True,

            ).max()

        )

    # ==========================================================
    # SWING LOWS
    # ==========================================================

    def swing_lows(

        self,

        lookback: int = 5,

    ) -> pd.Series:

        lows = self.data["Low"]

        return lows.where(

            lows == lows.rolling(

                lookback * 2 + 1,

                center=True,

            ).min()

        )

    # ==========================================================
    # BREAK OF STRUCTURE (BOS)
    # ==========================================================

    def break_of_structure(

        self,

    ) -> Dict:

        highs = self.swing_highs().dropna()

        lows = self.swing_lows().dropna()

        close = float(

            self.data["Close"].iloc[-1]

        )

        bullish = False

        bearish = False

        if len(highs) > 0:

            bullish = close > float(

                highs.iloc[-1]

            )

        if len(lows) > 0:

            bearish = close < float(

                lows.iloc[-1]

            )

        return {

            "bullish": bullish,

            "bearish": bearish,

            "last_high": None if len(highs) == 0 else float(highs.iloc[-1]),

            "last_low": None if len(lows) == 0 else float(lows.iloc[-1]),

        }

    # ==========================================================
    # CHANGE OF CHARACTER (CHOCH)
    # ==========================================================

    def change_of_character(

        self,

    ) -> Dict:

        transition = self.trend_transition()

        bos = self.break_of_structure()

        bullish = (

            transition == "BULLISH_CROSSOVER"

            and

            bos["bullish"]

        )

        bearish = (

            transition == "BEARISH_CROSSOVER"

            and

            bos["bearish"]

        )

        return {

            "bullish": bullish,

            "bearish": bearish,

        }

    # ==========================================================
    # LIQUIDITY SWEEP
    # ==========================================================

    def liquidity_sweep(

        self,

        lookback: int = 20,

    ) -> Dict:

        recent_high = self.data["High"].iloc[-lookback:].max()

        recent_low = self.data["Low"].iloc[-lookback:].min()

        latest = self.data.iloc[-1]

        sweep_high = (

            latest["High"] > recent_high

            and

            latest["Close"] < recent_high

        )

        sweep_low = (

            latest["Low"] < recent_low

            and

            latest["Close"] > recent_low

        )

        return {

            "high_sweep": sweep_high,

            "low_sweep": sweep_low,

            "reference_high": float(recent_high),

            "reference_low": float(recent_low),

        }

    # ==========================================================
    # ORDER BLOCK
    # ==========================================================

    def order_block(

        self,

    ) -> Dict:

        candles = self.data.tail(

            10

        )

        bullish = candles.loc[

            candles["Close"] < candles["Open"]

        ]

        bearish = candles.loc[

            candles["Close"] > candles["Open"]

        ]

        bullish_block = None

        bearish_block = None

        if not bullish.empty:

            last = bullish.iloc[-1]

            bullish_block = {

                "high": float(last["High"]),

                "low": float(last["Low"]),

            }

        if not bearish.empty:

            last = bearish.iloc[-1]

            bearish_block = {

                "high": float(last["High"]),

                "low": float(last["Low"]),

            }

        return {

            "bullish": bullish_block,

            "bearish": bearish_block,

        }

    # ==========================================================
    # FAIR VALUE GAP
    # ==========================================================

    def fair_value_gap(

        self,

    ) -> List[Dict]:

        gaps = []

        df = self.data.reset_index(

            drop=True

        )

        for i in range(

            2,

            len(df),

        ):

            first = df.iloc[i - 2]

            third = df.iloc[i]

            if first["High"] < third["Low"]:

                gaps.append({

                    "type": "Bullish",

                    "top": float(third["Low"]),

                    "bottom": float(first["High"]),

                    "index": i,

                })

            elif first["Low"] > third["High"]:

                gaps.append({

                    "type": "Bearish",

                    "top": float(first["Low"]),

                    "bottom": float(third["High"]),

                    "index": i,

                })

        return gaps

    # ==========================================================
    # PREMIUM / DISCOUNT
    # ==========================================================

    def premium_discount_zone(

        self,

        lookback: int = 100,

    ) -> Dict:

        high = self.data["High"].tail(

            lookback

        ).max()

        low = self.data["Low"].tail(

            lookback

        ).min()

        midpoint = (

            high + low

        ) / 2

        price = float(

            self.data["Close"].iloc[-1]

        )

        if price >= midpoint:

            zone = "PREMIUM"

        else:

            zone = "DISCOUNT"

        return {

            "zone": zone,

            "midpoint": float(midpoint),

            "range_high": float(high),

            "range_low": float(low),

        }

    # ==========================================================
    # SMART MONEY SUMMARY
    # ==========================================================

    def smart_money_summary(

        self,

    ) -> Dict:

        return {

            "bos":

                self.break_of_structure(),

            "choch":

                self.change_of_character(),

            "liquidity":

                self.liquidity_sweep(),

            "order_block":

                self.order_block(),

            "fair_value_gap":

                self.fair_value_gap(),

            "premium_discount":

                self.premium_discount_zone(),

        }
        # ==========================================================
    # WYCKOFF PHASE DETECTION
    # ==========================================================

    def wyckoff_phase(

        self,

    ) -> str:

        close = self.data["Close"]

        volume = self.data["Volume"]

        ema50 = self.ema(

            self.config.ema_slow

        )

        latest_close = float(

            close.iloc[-1]

        )

        latest_ema = float(

            ema50.iloc[-1]

        )

        avg_volume = float(

            volume.tail(20).mean()

        )

        latest_volume = float(

            volume.iloc[-1]

        )

        if (

            latest_close > latest_ema

            and latest_volume > avg_volume * 1.30

        ):

            return "MARKUP"

        if (

            latest_close < latest_ema

            and latest_volume > avg_volume * 1.30

        ):

            return "MARKDOWN"

        if self.accumulation_phase():

            return "ACCUMULATION"

        if self.distribution_phase():

            return "DISTRIBUTION"

        return "RANGE"

    # ==========================================================
    # MARKET CYCLE
    # ==========================================================

    def market_cycle(

        self,

    ) -> str:

        regime = self.classify_regime()

        phase = self.wyckoff_phase()

        if regime in (

            MarketRegime.STRONG_BULL,

            MarketRegime.BULL,

        ):

            if phase == "MARKUP":

                return "EARLY_BULL"

            return "MATURE_BULL"

        if regime in (

            MarketRegime.STRONG_BEAR,

            MarketRegime.BEAR,

        ):

            if phase == "MARKDOWN":

                return "EARLY_BEAR"

            return "MATURE_BEAR"

        return "CONSOLIDATION"

    # ==========================================================
    # EXPANSION / CONTRACTION
    # ==========================================================

    def volatility_expansion(

        self,

    ) -> Dict:

        atr = self.atr()

        current = float(

            atr.iloc[-1]

        )

        average = float(

            atr.tail(20).mean()

        )

        if average == 0:

            ratio = 1

        else:

            ratio = current / average

        if ratio > 1.20:

            state = "EXPANSION"

        elif ratio < 0.80:

            state = "CONTRACTION"

        else:

            state = "NORMAL"

        return {

            "state": state,

            "ratio": round(

                ratio,

                2,

            ),

        }

    # ==========================================================
    # VOLATILITY COMPRESSION
    # ==========================================================

    def volatility_compression(

        self,

        period: int = 20,

    ) -> bool:

        atr = self.atr()

        current = float(

            atr.iloc[-1]

        )

        historical = float(

            atr.tail(period).mean()

        )

        return current < historical * 0.75

    # ==========================================================
    # AI ALERTS
    # ==========================================================

    def ai_alerts(

        self,

    ) -> List[str]:

        alerts = []

        if self.volatility_shock():

            alerts.append(

                "Volatility Shock Detected"

            )

        if self.accumulation_phase():

            alerts.append(

                "Institutional Accumulation"

            )

        if self.distribution_phase():

            alerts.append(

                "Institutional Distribution"

            )

        bos = self.break_of_structure()

        if bos["bullish"]:

            alerts.append(

                "Bullish Break of Structure"

            )

        if bos["bearish"]:

            alerts.append(

                "Bearish Break of Structure"

            )

        choch = self.change_of_character()

        if choch["bullish"]:

            alerts.append(

                "Bullish CHOCH"

            )

        if choch["bearish"]:

            alerts.append(

                "Bearish CHOCH"

            )

        if self.volatility_compression():

            alerts.append(

                "Volatility Compression"

            )

        return alerts

    # ==========================================================
    # ENTRY BIAS
    # ==========================================================

    def entry_bias(

        self,

    ) -> str:

        regime = self.classify_regime()

        if regime in (

            MarketRegime.STRONG_BULL,

            MarketRegime.BULL,

        ):

            return "LONG"

        if regime in (

            MarketRegime.STRONG_BEAR,

            MarketRegime.BEAR,

        ):

            return "SHORT"

        return "WAIT"

    # ==========================================================
    # EXIT BIAS
    # ==========================================================

    def exit_bias(

        self,

    ) -> str:

        alerts = self.ai_alerts()

        if (

            "Institutional Distribution" in alerts

            or

            "Bearish Break of Structure" in alerts

        ):

            return "EXIT_LONG"

        if (

            "Institutional Accumulation" in alerts

            or

            "Bullish Break of Structure" in alerts

        ):

            return "EXIT_SHORT"

        return "HOLD"

    # ==========================================================
    # PROFESSIONAL TRADING PLAN
    # ==========================================================

    def trading_plan(

        self,

    ) -> Dict:

        return {

            "market_cycle":

                self.market_cycle(),

            "wyckoff":

                self.wyckoff_phase(),

            "entry":

                self.entry_bias(),

            "exit":

                self.exit_bias(),

            "alerts":

                self.ai_alerts(),

            "strategy":

                self.strategy_recommendation(),

            "expansion":

                self.volatility_expansion(),

            "compression":

                self.volatility_compression(),

        }

    # ==========================================================
    # COMPLETE AI SUMMARY
    # ==========================================================

    def ai_summary(

        self,

    ) -> Dict:

        return {

            "regime":

                self.classify_regime().value,

            "trend":

                self.trend_direction(),

            "confidence":

                self.confidence_score(),

            "cycle":

                self.market_cycle(),

            "wyckoff":

                self.wyckoff_phase(),

            "entry_bias":

                self.entry_bias(),

            "exit_bias":

                self.exit_bias(),

            "alerts":

                self.ai_alerts(),

            "smc":

                self.smart_money_summary(),

            "plan":

                self.trading_plan(),

        }
        # ==========================================================
    # ANALYZE
    # ==========================================================

    def analyze(

        self,

        sector_score: float = 50.0,

        fii_net: float = 0.0,

        dii_net: float = 0.0,

    ) -> RegimeResult:

        self.validate()

        state = self.build_state(

            sector_score

        )

        state["market_health"] = self.market_health_score(

            fii_net,

            dii_net,

            sector_score,

        )

        state["institutional_sentiment"] = self.fii_dii_sentiment(

            fii_net,

            dii_net,

        )

        state["ai_summary"] = self.ai_summary()

        state["analysis_time"] = datetime.now()

        result = RegimeResult(

            regime=self.classify_regime(),

            trend_strength=self.trend_strength(),

            volatility=self.volatility_regime(),

            score=state["regime_score"],

            confidence=state["confidence"],

            details=state,

        )

        self.result = result

        self.history.append(

            result

        )

        return result

    # ==========================================================
    # EXECUTE
    # ==========================================================

    def execute(

        self,

        sector_score: float = 50.0,

        fii_net: float = 0.0,

        dii_net: float = 0.0,

    ) -> RegimeResult:

        start = time.perf_counter()

        self.running = True

        try:

            result = self.analyze(

                sector_score,

                fii_net,

                dii_net,

            )

            self.last_runtime = (

                time.perf_counter()

                - start

            )

            return result

        finally:

            self.running = False

    # ==========================================================
    # RESULT AS DICT
    # ==========================================================

    def to_dict(

        self,

    ) -> Dict:

        if self.result is None:

            return {}

        return {

            "regime":

                self.result.regime.value,

            "trend_strength":

                self.result.trend_strength.value,

            "volatility":

                self.result.volatility.value,

            "score":

                self.result.score,

            "confidence":

                self.result.confidence,

            "details":

                self.result.details,

        }

    # ==========================================================
    # RESULT AS JSON
    # ==========================================================

    def to_json(

        self,

        indent: int = 4,

    ) -> str:

        return json.dumps(

            self.to_dict(),

            default=str,

            indent=indent,

        )

    # ==========================================================
    # EXPORT JSON
    # ==========================================================

    def export_json(

        self,

        filename: str,

    ) -> None:

        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                self.to_dict(),

                file,

                indent=4,

                default=str,

            )

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_csv(

        self,

        filename: str,

    ) -> None:

        df = pd.json_normalize(

            self.to_dict()

        )

        df.to_csv(

            filename,

            index=False,

        )

    # ==========================================================
    # EXPORT DATAFRAME
    # ==========================================================

    def to_dataframe(

        self,

    ) -> pd.DataFrame:

        return pd.json_normalize(

            self.to_dict()

        )

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================

    def performance_metrics(

        self,

    ) -> Dict:

        return {

            "runtime_seconds":

                getattr(

                    self,

                    "last_runtime",

                    0.0,

                ),

            "history_size":

                len(

                    self.history

                ),

            "symbol":

                self.symbol,

            "bars":

                0 if self.data is None else len(self.data),

        }

    # ==========================================================
    # LOG SUMMARY
    # ==========================================================

    def log_summary(

        self,

        logger=None,

    ) -> None:

        if self.result is None:

            return

        message = (

            f"{self.symbol} | "

            f"{self.result.regime.value} | "

            f"Score={self.result.score:.2f} | "

            f"Confidence={self.result.confidence:.2f}"

        )

        if logger is not None:

            logger.info(

                message

            )

        else:

            print(

                message

            )

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(

        self,

    ) -> str:

        if self.result is None:

            return (

                "MarketRegimeDetector(Not Analyzed)"

            )

        return (

            f"MarketRegimeDetector("

            f"{self.symbol}, "

            f"{self.result.regime.value}, "

            f"{self.result.confidence:.2f}%)"

        )

    # ==========================================================
    # REPRESENTATION
    # ==========================================================

    def __repr__(

        self,

    ) -> str:

        return self.__str__()

    # ==========================================================
    # HISTORY DATAFRAME
    # ==========================================================

    def history_dataframe(

        self,

    ) -> pd.DataFrame:

        rows = []

        for item in self.history:

            rows.append({

                "Regime":

                    item.regime.value,

                "Trend":

                    item.trend_strength.value,

                "Volatility":

                    item.volatility.value,

                "Score":

                    item.score,

                "Confidence":

                    item.confidence,

            })

        return pd.DataFrame(

            rows

        )

    # ==========================================================
    # SAVE HISTORY
    # ==========================================================

    def save_history(

        self,

        filename: str,

    ) -> None:

        self.history_dataframe().to_csv(

            filename,

            index=False,

        )

# ==============================================================
# END OF FILE
# ==============================================================
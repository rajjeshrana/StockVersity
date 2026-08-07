"""
==============================================================
StockVersity Scanner Pro v3
Professional Scanner Engine
==============================================================
Institutional Grade Scanner

Modules
--------
✔ Intraday Scanner
✔ Swing Scanner
✔ Positional Scanner
✔ AI Ranking Engine
✔ Volume Analysis
✔ VWAP
✔ EMA Filters
✔ ATR
✔ Relative Strength
✔ Risk Reward Engine
==============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import json
import numpy as np
import pandas as pd


# ==========================================================
# OPPORTUNITY MODEL
# ==========================================================

@dataclass
class Opportunity:

    symbol: str = ""

    company: str = ""

    sector: str = ""

    signal: str = ""

    pattern: str = ""

    timeframe: str = ""

    entry: float = 0.0

    stoploss: float = 0.0

    target: float = 0.0

    risk_reward: float = 0.0

    ai_score: float = 0.0

    volume_ratio: float = 0.0

    price: float = 0.0

    change_percent: float = 0.0

    atr: float = 0.0

    ema20: float = 0.0

    ema50: float = 0.0

    ema200: float = 0.0

    vwap: float = 0.0

    rsi: float = 0.0

    macd: float = 0.0

    macd_signal: float = 0.0

    adx: float = 0.0

    volume: float = 0.0

    delivery: float = 0.0

    updated: str = ""


# ==========================================================
# SCANNER ENGINE
# ==========================================================

class ScannerEngine:

    """
    Main Scanner Engine
    """

    def __init__(self):

        self.market_data = pd.DataFrame()

        self.opportunities: List[Opportunity] = []

        self.last_scan = None

        self.watchlist = []

        self.initialize()

    # ======================================================
    # INITIALIZE
    # ======================================================

    def initialize(self):

        self.last_scan = datetime.now()

        self.opportunities.clear()

    # ======================================================
    # LOAD MARKET DATA
    # ======================================================

    def load_market_data(

        self,

        dataframe: pd.DataFrame,

    ):

        self.market_data = dataframe.copy()

    # ======================================================
    # GET OPPORTUNITIES
    # ======================================================

    def get_opportunities(

        self,

    ) -> List[Opportunity]:

        return self.opportunities

    # ======================================================
    # CLEAR
    # ======================================================

    def clear(self):

        self.opportunities.clear()

    # ======================================================
    # SCAN
    # ======================================================

    def scan(self):

        self.clear()

        if self.market_data.empty:

            return []

        self.scan_intraday()

        self.scan_swing()

        self.scan_positional()

        self.rank_opportunities()

        self.last_scan = datetime.now()

        return self.opportunities
        # ======================================================
    # INDICATOR CALCULATIONS
    # ======================================================

    def ema(self, series: pd.Series, period: int) -> pd.Series:

        return series.ewm(
            span=period,
            adjust=False
        ).mean()

    # ======================================================

    def sma(self, series: pd.Series, period: int) -> pd.Series:

        return series.rolling(period).mean()

    # ======================================================

    def vwap(self, df: pd.DataFrame) -> pd.Series:

        typical_price = (
            df["high"] +
            df["low"] +
            df["close"]
        ) / 3

        cumulative_tp_vol = (
            typical_price * df["volume"]
        ).cumsum()

        cumulative_volume = (
            df["volume"].cumsum()
        )

        return cumulative_tp_vol / cumulative_volume

    # ======================================================

    def atr(
        self,
        df: pd.DataFrame,
        period: int = 14,
    ) -> pd.Series:

        high_low = df["high"] - df["low"]

        high_close = np.abs(
            df["high"] -
            df["close"].shift(1)
        )

        low_close = np.abs(
            df["low"] -
            df["close"].shift(1)
        )

        true_range = pd.concat(

            [

                high_low,

                high_close,

                low_close,

            ],

            axis=1,

        ).max(axis=1)

        return true_range.rolling(
            period
        ).mean()

    # ======================================================

    def rsi(
        self,
        close: pd.Series,
        period: int = 14,
    ):

        delta = close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(period).mean()

        avg_loss = loss.rolling(period).mean()

        rs = avg_gain / avg_loss

        return 100 - (

            100 / (1 + rs)

        )

    # ======================================================

    def macd(
        self,
        close: pd.Series,
        fast=12,
        slow=26,
        signal=9,
    ):

        ema_fast = self.ema(
            close,
            fast,
        )

        ema_slow = self.ema(
            close,
            slow,
        )

        macd_line = ema_fast - ema_slow

        signal_line = self.ema(
            macd_line,
            signal,
        )

        histogram = (

            macd_line -

            signal_line

        )

        return (

            macd_line,

            signal_line,

            histogram,

        )

    # ======================================================

    def adx(
        self,
        df: pd.DataFrame,
        period: int = 14,
    ):

        plus_dm = (
            df["high"].diff()
        )

        minus_dm = (
            -df["low"].diff()
        )

        plus_dm = np.where(

            (

                plus_dm >

                minus_dm

            ) & (

                plus_dm > 0

            ),

            plus_dm,

            0,

        )

        minus_dm = np.where(

            (

                minus_dm >

                df["high"].diff()

            ) & (

                minus_dm > 0

            ),

            minus_dm,

            0,

        )

        atr = self.atr(
            df,
            period,
        )

        plus_di = (

            100 *

            pd.Series(plus_dm)

            .rolling(period)

            .sum()

            / atr

        )

        minus_di = (

            100 *

            pd.Series(minus_dm)

            .rolling(period)

            .sum()

            / atr

        )

        dx = (

            abs(

                plus_di -

                minus_di

            )

            /

            (

                plus_di +

                minus_di

            )

        ) * 100

        return dx.rolling(
            period
        ).mean()

    # ======================================================

    def volume_ratio(
        self,
        volume: pd.Series,
        period: int = 20,
    ):

        average = volume.rolling(
            period
        ).mean()

        return volume / average

    # ======================================================
    # APPLY ALL INDICATORS
    # ======================================================

    def calculate_indicators(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        df = df.copy()

        df["EMA20"] = self.ema(
            df["close"],
            20,
        )

        df["EMA50"] = self.ema(
            df["close"],
            50,
        )

        df["EMA200"] = self.ema(
            df["close"],
            200,
        )

        df["VWAP"] = self.vwap(df)

        df["ATR"] = self.atr(df)

        df["RSI"] = self.rsi(
            df["close"]
        )

        macd_line, signal, hist = self.macd(
            df["close"]
        )

        df["MACD"] = macd_line

        df["MACD_SIGNAL"] = signal

        df["MACD_HIST"] = hist

        df["ADX"] = self.adx(df)

        df["RVOL"] = self.volume_ratio(
            df["volume"]
        )

        return df
        # ======================================================
    # INTRADAY SCANNER
    # ======================================================

    def scan_intraday(self):

        if self.market_data.empty:
            return

        df = self.calculate_indicators(
            self.market_data
        )

        for _, row in df.iterrows():

            # -------------------------------
            # Trend Filter
            # -------------------------------

            if row["close"] <= row["EMA20"]:
                continue

            if row["EMA20"] <= row["EMA50"]:
                continue

            if row["EMA50"] <= row["EMA200"]:
                continue

            # -------------------------------
            # VWAP Filter
            # -------------------------------

            if row["close"] <= row["VWAP"]:
                continue

            # -------------------------------
            # Relative Volume
            # -------------------------------

            if row["RVOL"] < 2:
                continue

            # -------------------------------
            # RSI
            # -------------------------------

            if row["RSI"] < 55:
                continue

            # -------------------------------
            # ADX
            # -------------------------------

            if row["ADX"] < 20:
                continue

            # -------------------------------
            # MACD Confirmation
            # -------------------------------

            if row["MACD"] <= row["MACD_SIGNAL"]:
                continue

            # -------------------------------
            # Risk Management
            # -------------------------------

            entry = float(row["close"])

            stoploss = entry - row["ATR"]

            target = entry + (row["ATR"] * 2)

            rr = round(

                (target - entry) /

                (entry - stoploss),

                2,

            )

            # -------------------------------
            # AI SCORE
            # -------------------------------

            ai = 0

            if row["close"] > row["EMA20"]:
                ai += 10

            if row["EMA20"] > row["EMA50"]:
                ai += 10

            if row["EMA50"] > row["EMA200"]:
                ai += 10

            if row["close"] > row["VWAP"]:
                ai += 10

            if row["RVOL"] >= 2:
                ai += 15

            if row["RVOL"] >= 3:
                ai += 10

            if row["RSI"] >= 60:
                ai += 10

            if row["MACD"] > row["MACD_SIGNAL"]:
                ai += 10

            if row["ADX"] >= 25:
                ai += 10

            if rr >= 2:
                ai += 5

            ai = min(ai, 100)

            # -------------------------------
            # CREATE OPPORTUNITY
            # -------------------------------

            opportunity = Opportunity(

                symbol=row.get(
                    "symbol",
                    "",
                ),

                company=row.get(
                    "company",
                    "",
                ),

                sector=row.get(
                    "sector",
                    "",
                ),

                signal="BUY",

                pattern="Momentum Breakout",

                timeframe="Intraday",

                entry=round(entry, 2),

                stoploss=round(stoploss, 2),

                target=round(target, 2),

                risk_reward=rr,

                ai_score=ai,

                volume_ratio=round(
                    row["RVOL"],
                    2,
                ),

                price=round(
                    row["close"],
                    2,
                ),

                change_percent=round(
                    row.get(
                        "change_percent",
                        0,
                    ),
                    2,
                ),

                atr=round(
                    row["ATR"],
                    2,
                ),

                ema20=round(
                    row["EMA20"],
                    2,
                ),

                ema50=round(
                    row["EMA50"],
                    2,
                ),

                ema200=round(
                    row["EMA200"],
                    2,
                ),

                vwap=round(
                    row["VWAP"],
                    2,
                ),

                rsi=round(
                    row["RSI"],
                    2,
                ),

                macd=round(
                    row["MACD"],
                    2,
                ),

                macd_signal=round(
                    row["MACD_SIGNAL"],
                    2,
                ),

                adx=round(
                    row["ADX"],
                    2,
                ),

                volume=row["volume"],

                updated=datetime.now().strftime(
                    "%H:%M:%S"
                ),

            )

            self.opportunities.append(
                opportunity
            )
                # ======================================================
    # SWING SCANNER
    # ======================================================

    def scan_swing(self):

        if self.market_data.empty:
            return

        df = self.calculate_indicators(
            self.market_data
        )

        for _, row in df.iterrows():

            # --------------------------------
            # PRIMARY TREND
            # --------------------------------

            if row["EMA20"] <= row["EMA50"]:
                continue

            if row["EMA50"] <= row["EMA200"]:
                continue

            # --------------------------------
            # RSI
            # --------------------------------

            if row["RSI"] < 50 or row["RSI"] > 72:
                continue

            # --------------------------------
            # ADX
            # --------------------------------

            if row["ADX"] < 20:
                continue

            # --------------------------------
            # MACD Confirmation
            # --------------------------------

            if row["MACD"] <= row["MACD_SIGNAL"]:
                continue

            # --------------------------------
            # Relative Volume
            # --------------------------------

            if row["RVOL"] < 1.50:
                continue

            # --------------------------------
            # Pattern Detection
            # --------------------------------

            pattern = "Swing Breakout"

            if row["close"] > row["EMA20"] * 1.01:
                pattern = "Bull Flag"

            elif abs(
                row["close"] - row["EMA20"]
            ) <= row["ATR"] * 0.20:

                pattern = "EMA Pullback"

            elif row["RVOL"] >= 2.5:

                pattern = "Cup & Handle"

            elif row["ATR"] < (
                row["close"] * 0.02
            ):

                pattern = "VCP"

            # --------------------------------
            # Trade Levels
            # --------------------------------

            entry = float(row["close"])

            stoploss = min(

                row["EMA20"],

                entry - row["ATR"]

            )

            target = entry + (

                (entry - stoploss) * 3

            )

            rr = round(

                (target - entry)

                /

                (entry - stoploss),

                2,

            )

            # --------------------------------
            # AI SCORE
            # --------------------------------

            score = 0

            if row["EMA20"] > row["EMA50"]:
                score += 15

            if row["EMA50"] > row["EMA200"]:
                score += 15

            if row["MACD"] > row["MACD_SIGNAL"]:
                score += 10

            if row["RSI"] >= 55:
                score += 10

            if row["ADX"] >= 25:
                score += 10

            if row["RVOL"] >= 2:
                score += 10

            if pattern == "Bull Flag":
                score += 10

            elif pattern == "Cup & Handle":
                score += 15

            elif pattern == "VCP":
                score += 20

            elif pattern == "EMA Pullback":
                score += 15

            if rr >= 3:
                score += 10

            score = min(score, 100)

            # --------------------------------
            # CREATE OPPORTUNITY
            # --------------------------------

            opportunity = Opportunity(

                symbol=row.get(
                    "symbol",
                    "",
                ),

                company=row.get(
                    "company",
                    "",
                ),

                sector=row.get(
                    "sector",
                    "",
                ),

                signal="BUY",

                pattern=pattern,

                timeframe="Swing",

                entry=round(
                    entry,
                    2,
                ),

                stoploss=round(
                    stoploss,
                    2,
                ),

                target=round(
                    target,
                    2,
                ),

                risk_reward=rr,

                ai_score=score,

                volume_ratio=round(
                    row["RVOL"],
                    2,
                ),

                price=round(
                    row["close"],
                    2,
                ),

                change_percent=round(
                    row.get(
                        "change_percent",
                        0,
                    ),
                    2,
                ),

                atr=round(
                    row["ATR"],
                    2,
                ),

                ema20=round(
                    row["EMA20"],
                    2,
                ),

                ema50=round(
                    row["EMA50"],
                    2,
                ),

                ema200=round(
                    row["EMA200"],
                    2,
                ),

                vwap=round(
                    row["VWAP"],
                    2,
                ),

                rsi=round(
                    row["RSI"],
                    2,
                ),

                macd=round(
                    row["MACD"],
                    2,
                ),

                macd_signal=round(
                    row["MACD_SIGNAL"],
                    2,
                ),

                adx=round(
                    row["ADX"],
                    2,
                ),

                volume=row["volume"],

                updated=datetime.now().strftime(
                    "%H:%M:%S"
                ),

            )

            self.opportunities.append(
                opportunity
            )
                # ======================================================
    # POSITIONAL SCANNER
    # ======================================================

    def scan_positional(self):

        if self.market_data.empty:
            return

        df = self.calculate_indicators(
            self.market_data
        )

        for _, row in df.iterrows():

            # ------------------------------------------
            # Long-Term Trend
            # ------------------------------------------

            if row["EMA50"] <= row["EMA200"]:
                continue

            if row["close"] <= row["EMA50"]:
                continue

            # ------------------------------------------
            # Strong Momentum
            # ------------------------------------------

            if row["RSI"] < 55:
                continue

            if row["ADX"] < 25:
                continue

            # ------------------------------------------
            # Volume Confirmation
            # ------------------------------------------

            if row["RVOL"] < 1.30:
                continue

            # ------------------------------------------
            # 52 Week High Filter
            # ------------------------------------------

            pattern = "Long Term Trend"

            if "high_52week" in row.index:

                if row["close"] >= row["high_52week"] * 0.99:

                    pattern = "52 Week Breakout"

            # ------------------------------------------
            # Delivery Filter
            # ------------------------------------------

            if "delivery" in row.index:

                if row["delivery"] >= 60:

                    pattern = "High Delivery"

            # ------------------------------------------
            # Trade Levels
            # ------------------------------------------

            entry = float(row["close"])

            stoploss = min(

                row["EMA50"],

                entry - (2 * row["ATR"])

            )

            risk = entry - stoploss

            target = entry + (risk * 4)

            rr = round(

                (target - entry) / risk,

                2

            )

            # ------------------------------------------
            # AI Score
            # ------------------------------------------

            score = 0

            if row["EMA50"] > row["EMA200"]:
                score += 20

            if row["close"] > row["EMA50"]:
                score += 15

            if row["close"] > row["EMA200"]:
                score += 10

            if row["RSI"] >= 60:
                score += 10

            if row["ADX"] >= 30:
                score += 10

            if row["RVOL"] >= 2:
                score += 10

            if pattern == "52 Week Breakout":
                score += 15

            if pattern == "High Delivery":
                score += 10

            if rr >= 3:
                score += 10

            score = min(score, 100)

            # ------------------------------------------
            # Opportunity
            # ------------------------------------------

            opportunity = Opportunity(

                symbol=row.get(
                    "symbol",
                    ""
                ),

                company=row.get(
                    "company",
                    ""
                ),

                sector=row.get(
                    "sector",
                    ""
                ),

                signal="BUY",

                pattern=pattern,

                timeframe="Positional",

                entry=round(
                    entry,
                    2
                ),

                stoploss=round(
                    stoploss,
                    2
                ),

                target=round(
                    target,
                    2
                ),

                risk_reward=rr,

                ai_score=score,

                volume_ratio=round(
                    row["RVOL"],
                    2
                ),

                price=round(
                    row["close"],
                    2
                ),

                change_percent=round(
                    row.get(
                        "change_percent",
                        0
                    ),
                    2
                ),

                atr=round(
                    row["ATR"],
                    2
                ),

                ema20=round(
                    row["EMA20"],
                    2
                ),

                ema50=round(
                    row["EMA50"],
                    2
                ),

                ema200=round(
                    row["EMA200"],
                    2
                ),

                vwap=round(
                    row["VWAP"],
                    2
                ),

                rsi=round(
                    row["RSI"],
                    2
                ),

                macd=round(
                    row["MACD"],
                    2
                ),

                macd_signal=round(
                    row["MACD_SIGNAL"],
                    2
                ),

                adx=round(
                    row["ADX"],
                    2
                ),

                volume=row["volume"],

                delivery=row.get(
                    "delivery",
                    0
                ),

                updated=datetime.now().strftime(
                    "%H:%M:%S"
                )

            )

            self.opportunities.append(
                opportunity
            )
                # ======================================================
    # AI RANKING ENGINE
    # ======================================================

    def rank_opportunities(self):

        if not self.opportunities:
            return

        ranked = []

        seen = set()

        for opportunity in self.opportunities:

            symbol = opportunity.symbol.upper()

            # ------------------------------------------
            # REMOVE DUPLICATES
            # ------------------------------------------

            if symbol in seen:
                continue

            seen.add(symbol)

            score = opportunity.ai_score

            # ------------------------------------------
            # RISK / REWARD BONUS
            # ------------------------------------------

            if opportunity.risk_reward >= 5:
                score += 8

            elif opportunity.risk_reward >= 4:
                score += 6

            elif opportunity.risk_reward >= 3:
                score += 4

            elif opportunity.risk_reward >= 2:
                score += 2

            # ------------------------------------------
            # VOLUME BONUS
            # ------------------------------------------

            if opportunity.volume_ratio >= 5:

                score += 8

            elif opportunity.volume_ratio >= 3:

                score += 6

            elif opportunity.volume_ratio >= 2:

                score += 4

            # ------------------------------------------
            # ADX BONUS
            # ------------------------------------------

            if opportunity.adx >= 40:

                score += 6

            elif opportunity.adx >= 30:

                score += 4

            # ------------------------------------------
            # RSI BONUS
            # ------------------------------------------

            if 55 <= opportunity.rsi <= 70:

                score += 4

            elif opportunity.rsi > 70:

                score -= 2

            # ------------------------------------------
            # EMA ALIGNMENT BONUS
            # ------------------------------------------

            if (

                opportunity.price >

                opportunity.ema20 >

                opportunity.ema50 >

                opportunity.ema200

            ):

                score += 8

            # ------------------------------------------
            # VWAP BONUS
            # ------------------------------------------

            if opportunity.price > opportunity.vwap:

                score += 3

            # ------------------------------------------
            # MACD BONUS
            # ------------------------------------------

            if opportunity.macd > opportunity.macd_signal:

                score += 3

            # ------------------------------------------
            # NORMALIZE SCORE
            # ------------------------------------------

            score = max(0, min(score, 100))

            opportunity.ai_score = round(score, 1)

            ranked.append(opportunity)

        # ==================================================
        # SORT BY SCORE
        # ==================================================

        ranked.sort(

            key=lambda x: (

                x.ai_score,

                x.risk_reward,

                x.volume_ratio,

            ),

            reverse=True,

        )

        self.opportunities = ranked

        self.assign_priority()

    # ======================================================
    # PRIORITY ASSIGNMENT
    # ======================================================

    def assign_priority(self):

        for opportunity in self.opportunities:

            score = opportunity.ai_score

            if score >= 95:

                priority = "A+"

                confidence = "Very High"

            elif score >= 90:

                priority = "A"

                confidence = "High"

            elif score >= 80:

                priority = "B+"

                confidence = "Good"

            elif score >= 70:

                priority = "B"

                confidence = "Average"

            else:

                priority = "C"

                confidence = "Low"

            setattr(

                opportunity,

                "priority",

                priority,

            )

            setattr(

                opportunity,

                "confidence",

                confidence,

            )

    # ======================================================
    # TOP OPPORTUNITIES
    # ======================================================

    def top_opportunities(

        self,

        limit=20,

    ):

        return self.opportunities[:limit]

    # ======================================================
    # FILTER BY SCORE
    # ======================================================

    def minimum_ai_score(

        self,

        minimum=80,

    ):

        return [

            x

            for x in self.opportunities

            if x.ai_score >= minimum

        ]

    # ======================================================
    # FILTER BY PRIORITY
    # ======================================================

    def filter_priority(

        self,

        priority="A+",

    ):

        return [

            x

            for x in self.opportunities

            if getattr(

                x,

                "priority",

                ""

            ) == priority

        ]
        # ======================================================
    # INSTITUTIONAL FILTERS
    # ======================================================

    def institutional_filter(self, row):

        """
        Returns True if the stock satisfies all
        institutional-quality filters.
        """

        # --------------------------------------------------
        # PRICE FILTER
        # --------------------------------------------------

        if row["close"] < 50:
            return False

        if row["close"] > 10000:
            return False

        # --------------------------------------------------
        # VOLUME FILTER
        # --------------------------------------------------

        if row["volume"] < 100000:
            return False

        # --------------------------------------------------
        # RELATIVE VOLUME
        # --------------------------------------------------

        if row["RVOL"] < 1.5:
            return False

        # --------------------------------------------------
        # TREND
        # --------------------------------------------------

        if row["EMA20"] < row["EMA50"]:
            return False

        if row["EMA50"] < row["EMA200"]:
            return False

        # --------------------------------------------------
        # ADX
        # --------------------------------------------------

        if row["ADX"] < 20:
            return False

        return True

    # ======================================================
    # GAP FILTER
    # ======================================================

    def gap_filter(

        self,

        row,

        max_gap=3,

    ):

        if "previous_close" not in row.index:
            return True

        previous = row["previous_close"]

        gap = abs(

            (

                row["open"] -

                previous

            )

            / previous

        ) * 100

        return gap <= max_gap

    # ======================================================
    # OPENING RANGE BREAKOUT
    # ======================================================

    def orb_filter(

        self,

        row,

    ):

        if "orb_high" not in row.index:
            return True

        return row["close"] > row["orb_high"]

    # ======================================================
    # DELIVERY FILTER
    # ======================================================

    def delivery_filter(

        self,

        row,

        minimum=40,

    ):

        if "delivery" not in row.index:

            return True

        return row["delivery"] >= minimum

    # ======================================================
    # 52 WEEK HIGH FILTER
    # ======================================================

    def breakout_52week(

        self,

        row,

    ):

        if "high_52week" not in row.index:

            return False

        return row["close"] >= (

            row["high_52week"] * 0.99

        )

    # ======================================================
    # MACD FILTER
    # ======================================================

    def macd_filter(

        self,

        row,

    ):

        return row["MACD"] > row["MACD_SIGNAL"]

    # ======================================================
    # VWAP FILTER
    # ======================================================

    def vwap_filter(

        self,

        row,

    ):

        return row["close"] > row["VWAP"]

    # ======================================================
    # RSI FILTER
    # ======================================================

    def rsi_filter(

        self,

        row,

        minimum=55,

        maximum=75,

    ):

        return minimum <= row["RSI"] <= maximum

    # ======================================================
    # F&O FILTER
    # ======================================================

    def fo_filter(

        self,

        row,

    ):

        if "fo_stock" not in row.index:

            return True

        return bool(row["fo_stock"])

    # ======================================================
    # NIFTY TREND FILTER
    # ======================================================

    def nifty_trend_filter(

        self,

        nifty_close,

        nifty_20,

        nifty_50,

    ):

        return (

            nifty_close >

            nifty_20 >

            nifty_50

        )

    # ======================================================
    # SECTOR STRENGTH
    # ======================================================

    def sector_strength(

        self,

        sector_change,

    ):

        return sector_change >= 1.0

    # ======================================================
    # FINAL FILTER
    # ======================================================

    def passes_all_filters(

        self,

        row,

    ):

        return (

            self.institutional_filter(row)

            and self.gap_filter(row)

            and self.orb_filter(row)

            and self.delivery_filter(row)

            and self.macd_filter(row)

            and self.vwap_filter(row)

            and self.rsi_filter(row)

            and self.fo_filter(row)

        )
        # ======================================================
    # PATTERN DETECTION ENGINE
    # ======================================================

    def detect_pattern(self, df):

        """
        Returns the highest probability pattern.
        """

        if self.is_bull_flag(df):
            return "Bull Flag"

        if self.is_falling_wedge(df):
            return "Falling Wedge"

        if self.is_vcp(df):
            return "VCP"

        if self.is_cup_handle(df):
            return "Cup & Handle"

        if self.is_ascending_triangle(df):
            return "Ascending Triangle"

        if self.is_breakout(df):
            return "Breakout"

        if self.is_pullback(df):
            return "EMA Pullback"

        if self.is_consolidation(df):
            return "Consolidation"

        return "Trend"

    # ======================================================
    # BULL FLAG
    # ======================================================

    def is_bull_flag(self, df):

        if len(df) < 20:
            return False

        latest = df.iloc[-1]

        return (

            latest["EMA20"] > latest["EMA50"]

            and latest["close"] > latest["EMA20"]

            and latest["RVOL"] >= 2

            and latest["RSI"] >= 55

        )

    # ======================================================
    # FALLING WEDGE
    # ======================================================

    def is_falling_wedge(self, df):

        if len(df) < 30:
            return False

        highs = df["high"].tail(20)

        lows = df["low"].tail(20)

        return (

            highs.iloc[-1] < highs.iloc[0]

            and lows.iloc[-1] < lows.iloc[0]

            and df.iloc[-1]["close"] > df.iloc[-1]["EMA20"]

        )

    # ======================================================
    # VCP
    # ======================================================

    def is_vcp(self, df):

        if len(df) < 30:
            return False

        atr = df["ATR"].tail(10)

        volume = df["volume"].tail(10)

        return (

            atr.iloc[-1] < atr.mean()

            and volume.iloc[-1] > volume.mean()

            and df.iloc[-1]["close"] > df.iloc[-1]["EMA20"]

        )

    # ======================================================
    # CUP & HANDLE
    # ======================================================

    def is_cup_handle(self, df):

        if len(df) < 60:
            return False

        closes = df["close"].tail(60)

        lowest = closes.min()

        highest = closes.max()

        latest = closes.iloc[-1]

        return (

            latest >= highest * 0.98

            and (highest - lowest) / highest > 0.15

        )

    # ======================================================
    # ASCENDING TRIANGLE
    # ======================================================

    def is_ascending_triangle(self, df):

        if len(df) < 30:
            return False

        highs = df["high"].tail(20)

        lows = df["low"].tail(20)

        resistance = highs.max()

        rising_lows = lows.iloc[-1] > lows.iloc[0]

        breakout = df.iloc[-1]["close"] >= resistance * 0.995

        return (

            rising_lows

            and breakout

        )

    # ======================================================
    # BREAKOUT
    # ======================================================

    def is_breakout(self, df):

        if len(df) < 20:
            return False

        latest = df.iloc[-1]

        previous_high = df["high"].tail(20).max()

        return (

            latest["close"] >= previous_high

            and latest["RVOL"] >= 2

        )

    # ======================================================
    # EMA PULLBACK
    # ======================================================

    def is_pullback(self, df):

        latest = df.iloc[-1]

        return (

            abs(

                latest["close"]

                -

                latest["EMA20"]

            ) <= latest["ATR"] * 0.30

            and latest["EMA20"] > latest["EMA50"]

        )

    # ======================================================
    # CONSOLIDATION
    # ======================================================

    def is_consolidation(self, df):

        if len(df) < 15:
            return False

        high = df["high"].tail(10).max()

        low = df["low"].tail(10).min()

        return (

            (high - low)

            / low

        ) < 0.04

    # ======================================================
    # MULTI TIMEFRAME CONFIRMATION
    # ======================================================

    def multi_timeframe_confirmation(

        self,

        daily,

        hourly=None,

        weekly=None,

    ):

        score = 0

        if daily is not None:

            if daily["EMA20"] > daily["EMA50"]:

                score += 1

        if hourly is not None:

            if hourly["EMA20"] > hourly["EMA50"]:

                score += 1

        if weekly is not None:

            if weekly["EMA20"] > weekly["EMA50"]:

                score += 1

        return score >= 2
        # ======================================================
    # RISK MANAGEMENT ENGINE
    # ======================================================

    def calculate_position_size(
        self,
        capital,
        risk_percent,
        entry,
        stoploss,
    ):

        """
        Returns quantity based on fixed risk.
        """

        if entry <= stoploss:
            return 0

        risk_amount = capital * (risk_percent / 100)

        risk_per_share = entry - stoploss

        qty = int(risk_amount / risk_per_share)

        return max(qty, 0)

    # ======================================================
    # ATR STOP LOSS
    # ======================================================

    def atr_stoploss(
        self,
        entry,
        atr,
        multiplier=1.5,
    ):

        return round(

            entry - (atr * multiplier),

            2,

        )

    # ======================================================
    # ATR TARGET
    # ======================================================

    def atr_target(
        self,
        entry,
        atr,
        multiplier=3,
    ):

        return round(

            entry + (atr * multiplier),

            2,

        )

    # ======================================================
    # TRAILING STOP
    # ======================================================

    def trailing_stop(
        self,
        current_price,
        highest_price,
        atr,
        multiplier=2,
    ):

        stop = highest_price - (

            atr * multiplier

        )

        return round(

            min(current_price, stop),

            2,

        )

    # ======================================================
    # RISK REWARD
    # ======================================================

    def risk_reward(
        self,
        entry,
        stoploss,
        target,
    ):

        risk = entry - stoploss

        reward = target - entry

        if risk <= 0:

            return 0

        return round(

            reward / risk,

            2,

        )

    # ======================================================
    # CAPITAL ALLOCATION
    # ======================================================

    def allocate_capital(
        self,
        capital,
        opportunities,
    ):

        if len(opportunities) == 0:

            return {}

        allocation = capital / len(opportunities)

        result = {}

        for stock in opportunities:

            result[stock.symbol] = round(

                allocation,

                2,

            )

        return result

    # ======================================================
    # MAXIMUM EXPOSURE
    # ======================================================

    def exposure_check(
        self,
        capital,
        invested,
        maximum=0.70,
    ):

        return invested <= capital * maximum

    # ======================================================
    # TRADE VALIDATION
    # ======================================================

    def validate_trade(
        self,
        opportunity,
    ):

        if opportunity.ai_score < 70:

            return False

        if opportunity.risk_reward < 2:

            return False

        if opportunity.volume_ratio < 1.5:

            return False

        if opportunity.adx < 20:

            return False

        return True

    # ======================================================
    # WATCHLIST
    # ======================================================

    def build_watchlist(self):

        self.watchlist = [

            x

            for x in self.opportunities

            if self.validate_trade(x)

        ]

        return self.watchlist

    # ======================================================
    # BEST PICKS
    # ======================================================

    def best_trades(
        self,
        limit=10,
    ):

        return sorted(

            self.watchlist,

            key=lambda x: (

                x.ai_score,

                x.risk_reward,

                x.volume_ratio,

            ),

            reverse=True,

        )[:limit]

    # ======================================================
    # PORTFOLIO SUMMARY
    # ======================================================

    def portfolio_summary(
        self,
        capital,
        risk_percent=1,
    ):

        summary = []

        for trade in self.best_trades():

            qty = self.calculate_position_size(

                capital,

                risk_percent,

                trade.entry,

                trade.stoploss,

            )

            summary.append({

                "symbol": trade.symbol,

                "entry": trade.entry,

                "stoploss": trade.stoploss,

                "target": trade.target,

                "quantity": qty,

                "risk_reward": trade.risk_reward,

                "ai_score": trade.ai_score,

                "priority": getattr(

                    trade,

                    "priority",

                    "N/A",

                ),

            })

        return summary

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.market_data = pd.DataFrame()

        self.opportunities.clear()

        self.watchlist.clear()

        self.last_scan = datetime.now()
            # ======================================================
    # SCANNER STATISTICS
    # ======================================================

    def statistics(self):

        stats = {

            "total": len(self.opportunities),

            "intraday": 0,

            "swing": 0,

            "positional": 0,

            "average_score": 0,

            "highest_score": 0,

            "highest_rr": 0,

        }

        if not self.opportunities:

            return stats

        total_score = 0

        highest_score = 0

        highest_rr = 0

        for trade in self.opportunities:

            total_score += trade.ai_score

            highest_score = max(
                highest_score,
                trade.ai_score,
            )

            highest_rr = max(
                highest_rr,
                trade.risk_reward,
            )

            tf = trade.timeframe.lower()

            if tf == "intraday":
                stats["intraday"] += 1

            elif tf == "swing":
                stats["swing"] += 1

            elif tf == "positional":
                stats["positional"] += 1

        stats["average_score"] = round(
            total_score / len(self.opportunities),
            2,
        )

        stats["highest_score"] = highest_score

        stats["highest_rr"] = highest_rr

        return stats

    # ======================================================
    # EXPORT CSV
    # ======================================================

    def export_csv(
        self,
        filename="scanner_results.csv",
    ):

        rows = []

        for trade in self.opportunities:

            rows.append({

                "Symbol": trade.symbol,

                "Company": trade.company,

                "Sector": trade.sector,

                "Timeframe": trade.timeframe,

                "Signal": trade.signal,

                "Pattern": trade.pattern,

                "Price": trade.price,

                "Entry": trade.entry,

                "Stoploss": trade.stoploss,

                "Target": trade.target,

                "RR": trade.risk_reward,

                "AI Score": trade.ai_score,

                "Priority": getattr(
                    trade,
                    "priority",
                    "",
                ),

                "Confidence": getattr(
                    trade,
                    "confidence",
                    "",
                ),

                "Volume Ratio": trade.volume_ratio,

                "RSI": trade.rsi,

                "ADX": trade.adx,

                "Updated": trade.updated,

            })

        pd.DataFrame(rows).to_csv(
            filename,
            index=False,
        )

        return filename

    # ======================================================
    # EXPORT JSON
    # ======================================================

    def export_json(
        self,
        filename="scanner_results.json",
    ):

        data = []

        for trade in self.opportunities:

            data.append(vars(trade))

        with open(
            filename,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                default=str,
            )

        return filename

    # ======================================================
    # IMPORT WATCHLIST
    # ======================================================

    def import_watchlist(
        self,
        symbols,
    ):

        self.watchlist = []

        allowed = {

            symbol.upper()

            for symbol in symbols

        }

        for trade in self.opportunities:

            if trade.symbol.upper() in allowed:

                self.watchlist.append(trade)

        return self.watchlist

    # ======================================================
    # SEARCH
    # ======================================================

    def search(
        self,
        symbol,
    ):

        symbol = symbol.upper()

        for trade in self.opportunities:

            if trade.symbol.upper() == symbol:

                return trade

        return None

    # ======================================================
    # FILTER
    # ======================================================

    def filter_by_timeframe(
        self,
        timeframe,
    ):

        return [

            trade

            for trade in self.opportunities

            if trade.timeframe.lower()

            == timeframe.lower()

        ]

    # ======================================================
    # SORT
    # ======================================================

    def sort_by_score(self):

        self.opportunities.sort(

            key=lambda x: x.ai_score,

            reverse=True,

        )

        return self.opportunities

    def sort_by_rr(self):

        self.opportunities.sort(

            key=lambda x: x.risk_reward,

            reverse=True,

        )

        return self.opportunities

    # ======================================================
    # SCAN HISTORY
    # ======================================================

    def save_scan_history(self):

        self.scan_history.append({

            "timestamp": datetime.now(),

            "count": len(self.opportunities),

            "average_score": self.statistics()["average_score"],

        })

    def history(self):

        return self.scan_history

    # ======================================================
    # PUBLIC API
    # ======================================================

    def get_all(self):

        return self.opportunities

    def get_watchlist(self):

        return self.watchlist

    def get_statistics(self):

        return self.statistics()

    # ======================================================
    # STRING REPRESENTATION
    # ======================================================

    def __repr__(self):

        return (

            f"<ScannerEngine "

            f"stocks={len(self.market_data)} "

            f"opportunities={len(self.opportunities)}>"

        )

# ==========================================================
# END OF FILE
# ==========================================================
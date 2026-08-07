from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


# ==========================================================
# MARKET BREADTH RESULT
# ==========================================================

@dataclass
class BreadthResult:

    market: str

    advance_count: int

    decline_count: int

    unchanged_count: int

    advance_decline_ratio: float

    new_highs: int

    new_lows: int

    bullish_percent: float

    bearish_percent: float

    health_score: float

    breadth_score: float

    sentiment: str

    sector_strength: Dict = field(default_factory=dict)

    sector_rotation: Dict = field(default_factory=dict)

    fii_dii: Dict = field(default_factory=dict)

    delivery: Dict = field(default_factory=dict)

    indicators: Dict = field(default_factory=dict)

    remarks: List[str] = field(default_factory=list)


# ==========================================================
# MARKET BREADTH ENGINE
# ==========================================================

class MarketBreadthEngine:

    def __init__(self):

        self.market = "NSE"

        self.stock_data: Optional[pd.DataFrame] = None

        self.sector_data: Optional[pd.DataFrame] = None

        self.index_data: Optional[pd.DataFrame] = None

        self.result: Optional[BreadthResult] = None

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(

        self,

        stock_data: pd.DataFrame,

        sector_data: Optional[pd.DataFrame] = None,

        index_data: Optional[pd.DataFrame] = None,

        market: str = "NSE",

    ):

        self.market = market

        self.stock_data = stock_data.copy()

        self.sector_data = (

            sector_data.copy()

            if sector_data is not None

            else None

        )

        self.index_data = (

            index_data.copy()

            if index_data is not None

            else None

        )

        self.validate()

        return self

    # ==========================================================
    # VALIDATE
    # ==========================================================

    def validate(

        self,

    ):

        if self.stock_data is None:

            raise ValueError(

                "Stock data not loaded."

            )

        required = [

            "Symbol",

            "Open",

            "High",

            "Low",

            "Close",

            "PreviousClose",

            "Volume",

        ]

        missing = [

            col

            for col in required

            if col not in self.stock_data.columns

        ]

        if missing:

            raise ValueError(

                f"Missing columns: {missing}"

            )

    # ==========================================================
    # BASIC COUNTS
    # ==========================================================

    @property

    def total_stocks(

        self,

    ) -> int:

        return len(

            self.stock_data

        )

    @property

    def advances(

        self,

    ) -> pd.DataFrame:

        return self.stock_data[

            self.stock_data["Close"]

            >

            self.stock_data["PreviousClose"]

        ]

    @property

    def declines(

        self,

    ) -> pd.DataFrame:

        return self.stock_data[

            self.stock_data["Close"]

            <

            self.stock_data["PreviousClose"]

        ]

    @property

    def unchanged(

        self,

    ) -> pd.DataFrame:

        return self.stock_data[

            self.stock_data["Close"]

            ==

            self.stock_data["PreviousClose"]

        ]

    # ==========================================================
    # HELPER
    # ==========================================================

    def percentage(

        self,

        value: float,

        total: float,

    ) -> float:

        if total == 0:

            return 0.0

        return round(

            value / total * 100,

            2,

        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        self.stock_data = None

        self.sector_data = None

        self.index_data = None

        self.result = None
            # ==========================================================
    # ADVANCE / DECLINE RATIO
    # ==========================================================

    def advance_decline_ratio(

        self,

    ) -> float:

        advances = len(

            self.advances

        )

        declines = len(

            self.declines

        )

        if declines == 0:

            return float(advances)

        return round(

            advances / declines,

            2,

        )

    # ==========================================================
    # ADVANCE PERCENTAGE
    # ==========================================================

    def advance_percentage(

        self,

    ) -> float:

        return self.percentage(

            len(self.advances),

            self.total_stocks,

        )

    # ==========================================================
    # DECLINE PERCENTAGE
    # ==========================================================

    def decline_percentage(

        self,

    ) -> float:

        return self.percentage(

            len(self.declines),

            self.total_stocks,

        )

    # ==========================================================
    # BULLISH PERCENTAGE
    # ==========================================================

    def bullish_percentage(

        self,

    ) -> float:

        ema20 = self.stock_data["Close"] > (

            self.stock_data["High"]

            + self.stock_data["Low"]

        ) / 2

        bullish = ema20.sum()

        return self.percentage(

            bullish,

            self.total_stocks,

        )

    # ==========================================================
    # BEARISH PERCENTAGE
    # ==========================================================

    def bearish_percentage(

        self,

    ) -> float:

        return round(

            100

            -

            self.bullish_percentage(),

            2,

        )

    # ==========================================================
    # NEW HIGHS
    # ==========================================================

    def new_highs(

        self,

        lookback: int = 252,

    ) -> int:

        if "High52" in self.stock_data.columns:

            return int(

                (

                    self.stock_data["Close"]

                    >=

                    self.stock_data["High52"]

                ).sum()

            )

        if "RollingHigh" in self.stock_data.columns:

            return int(

                (

                    self.stock_data["Close"]

                    >=

                    self.stock_data["RollingHigh"]

                ).sum()

            )

        return 0

    # ==========================================================
    # NEW LOWS
    # ==========================================================

    def new_lows(

        self,

        lookback: int = 252,

    ) -> int:

        if "Low52" in self.stock_data.columns:

            return int(

                (

                    self.stock_data["Close"]

                    <=

                    self.stock_data["Low52"]

                ).sum()

            )

        if "RollingLow" in self.stock_data.columns:

            return int(

                (

                    self.stock_data["Close"]

                    <=

                    self.stock_data["RollingLow"]

                ).sum()

            )

        return 0

    # ==========================================================
    # NET BREADTH
    # ==========================================================

    def net_breadth(

        self,

    ) -> int:

        return (

            len(self.advances)

            -

            len(self.declines)

        )

    # ==========================================================
    # BREADTH MOMENTUM
    # ==========================================================

    def breadth_momentum(

        self,

    ) -> float:

        net = self.net_breadth()

        score = (

            net

            /

            max(

                self.total_stocks,

                1,

            )

        ) * 100

        return round(

            score,

            2,

        )

    # ==========================================================
    # BASIC MARKET HEALTH
    # ==========================================================

    def market_health(

        self,

    ) -> float:

        adv_score = self.advance_percentage()

        breadth = (

            self.breadth_momentum()

            + 100

        ) / 2

        nh = self.new_highs()

        nl = self.new_lows()

        if nh + nl > 0:

            breakout_score = (

                nh

                /

                (

                    nh + nl

                )

            ) * 100

        else:

            breakout_score = 50

        score = (

            adv_score * 0.40

            +

            breadth * 0.35

            +

            breakout_score * 0.25

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )
        # ==========================================================
    # NIFTY BREADTH
    # ==========================================================

    def nifty_breadth(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {

                "available": False,

                "score": 0,

            }

        nifty = self.index_data[

            self.index_data["Index"] == "NIFTY 50"

        ]

        if nifty.empty:

            return {

                "available": False,

                "score": 0,

            }

        row = nifty.iloc[-1]

        change = row.get(

            "ChangePercent",

            0,

        )

        above_vwap = row.get(

            "AboveVWAP",

            True,

        )

        score = 50

        if change > 0:

            score += 25

        if above_vwap:

            score += 25

        return {

            "available": True,

            "index": "NIFTY 50",

            "change_percent": round(change, 2),

            "above_vwap": above_vwap,

            "score": min(score, 100),

        }

    # ==========================================================
    # BANK NIFTY BREADTH
    # ==========================================================

    def banknifty_breadth(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {

                "available": False,

                "score": 0,

            }

        bank = self.index_data[

            self.index_data["Index"] == "NIFTY BANK"

        ]

        if bank.empty:

            return {

                "available": False,

                "score": 0,

            }

        row = bank.iloc[-1]

        change = row.get(

            "ChangePercent",

            0,

        )

        above_vwap = row.get(

            "AboveVWAP",

            True,

        )

        score = 50

        if change > 0:

            score += 25

        if above_vwap:

            score += 25

        return {

            "available": True,

            "index": "NIFTY BANK",

            "change_percent": round(change, 2),

            "above_vwap": above_vwap,

            "score": min(score, 100),

        }

    # ==========================================================
    # MIDCAP BREADTH
    # ==========================================================

    def midcap_breadth(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {

                "available": False,

                "score": 0,

            }

        data = self.index_data[

            self.index_data["Index"].str.contains(

                "MIDCAP",

                case=False,

                na=False,

            )

        ]

        if data.empty:

            return {

                "available": False,

                "score": 0,

            }

        change = data["ChangePercent"].mean()

        score = max(

            0,

            min(

                50 + change * 10,

                100,

            ),

        )

        return {

            "available": True,

            "average_change": round(change, 2),

            "score": round(score, 2),

        }

    # ==========================================================
    # SMALLCAP BREADTH
    # ==========================================================

    def smallcap_breadth(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {

                "available": False,

                "score": 0,

            }

        data = self.index_data[

            self.index_data["Index"].str.contains(

                "SMALLCAP",

                case=False,

                na=False,

            )

        ]

        if data.empty:

            return {

                "available": False,

                "score": 0,

            }

        change = data["ChangePercent"].mean()

        score = max(

            0,

            min(

                50 + change * 10,

                100,

            ),

        )

        return {

            "available": True,

            "average_change": round(change, 2),

            "score": round(score, 2),

        }

    # ==========================================================
    # INDEX BREADTH SCORE
    # ==========================================================

    def index_breadth_score(

        self,

    ) -> float:

        scores = []

        for fn in [

            self.nifty_breadth,

            self.banknifty_breadth,

            self.midcap_breadth,

            self.smallcap_breadth,

        ]:

            data = fn()

            if data.get(

                "available",

                False,

            ):

                scores.append(

                    data["score"]

                )

        if not scores:

            return 0.0

        return round(

            np.mean(scores),

            2,

        )

    # ==========================================================
    # INDEX TREND
    # ==========================================================

    def index_trend(

        self,

    ) -> str:

        score = self.index_breadth_score()

        if score >= 80:

            return "Strong Bullish"

        if score >= 65:

            return "Bullish"

        if score >= 45:

            return "Sideways"

        if score >= 30:

            return "Bearish"

        return "Strong Bearish"

    # ==========================================================
    # MARKET PARTICIPATION
    # ==========================================================

    def market_participation(

        self,

    ) -> Dict:

        adv = self.advance_percentage()

        bullish = self.bullish_percentage()

        participation = (

            adv * 0.60

            +

            bullish * 0.40

        )

        return {

            "advance_percent": adv,

            "bullish_percent": bullish,

            "participation_score": round(

                participation,

                2,

            ),

        }

    # ==========================================================
    # INDEX STRENGTH ENGINE
    # ==========================================================

    def index_strength(

        self,

    ) -> Dict:

        health = self.market_health()

        index_score = self.index_breadth_score()

        participation = self.market_participation()[

            "participation_score"

        ]

        strength = (

            health * 0.40

            +

            index_score * 0.35

            +

            participation * 0.25

        )

        return {

            "market_health": health,

            "index_score": index_score,

            "participation": participation,

            "strength": round(

                strength,

                2,

            ),

            "trend": self.index_trend(),

        }
        # ==========================================================
    # SECTOR STRENGTH ENGINE
    # ==========================================================

    def sector_strength(

        self,

    ) -> Dict:

        if self.sector_data is None:

            return {}

        strength = {}

        for _, row in self.sector_data.iterrows():

            sector = row["Sector"]

            change = row.get(

                "ChangePercent",

                0,

            )

            advance = row.get(

                "Advances",

                0,

            )

            decline = row.get(

                "Declines",

                0,

            )

            total = max(

                advance + decline,

                1,

            )

            breadth = (

                advance /

                total

            ) * 100

            score = (

                change * 10

                +

                breadth

            ) / 2

            strength[sector] = {

                "change": round(change, 2),

                "breadth": round(breadth, 2),

                "score": round(

                    max(

                        0,

                        min(

                            score,

                            100,

                        ),

                    ),

                    2,

                ),

            }

        return strength

    # ==========================================================
    # SECTOR ROTATION
    # ==========================================================

    def sector_rotation(

        self,

    ) -> Dict:

        strength = self.sector_strength()

        if not strength:

            return {}

        ordered = sorted(

            strength.items(),

            key=lambda x: x[1]["score"],

            reverse=True,

        )

        leaders = ordered[:3]

        laggards = ordered[-3:]

        return {

            "leaders": leaders,

            "laggards": laggards,

        }

    # ==========================================================
    # TOP PERFORMING SECTORS
    # ==========================================================

    def top_sectors(

        self,

        limit: int = 5,

    ) -> List[Dict]:

        strength = self.sector_strength()

        ordered = sorted(

            strength.items(),

            key=lambda x: x[1]["score"],

            reverse=True,

        )

        output = []

        for sector, values in ordered[:limit]:

            output.append(

                {

                    "sector": sector,

                    **values,

                }

            )

        return output

    # ==========================================================
    # WEAKEST SECTORS
    # ==========================================================

    def weakest_sectors(

        self,

        limit: int = 5,

    ) -> List[Dict]:

        strength = self.sector_strength()

        ordered = sorted(

            strength.items(),

            key=lambda x: x[1]["score"],

        )

        output = []

        for sector, values in ordered[:limit]:

            output.append(

                {

                    "sector": sector,

                    **values,

                }

            )

        return output

    # ==========================================================
    # SECTOR MOMENTUM
    # ==========================================================

    def sector_momentum(

        self,

    ) -> Dict:

        if self.sector_data is None:

            return {}

        momentum = {}

        for _, row in self.sector_data.iterrows():

            sector = row["Sector"]

            today = row.get(

                "ChangePercent",

                0,

            )

            week = row.get(

                "WeekChange",

                today,

            )

            month = row.get(

                "MonthChange",

                week,

            )

            score = (

                today * 0.50

                +

                week * 0.30

                +

                month * 0.20

            ) * 10

            momentum[sector] = round(

                max(

                    0,

                    min(

                        score,

                        100,

                    ),

                ),

                2,

            )

        return momentum

    # ==========================================================
    # SECTOR LEADERSHIP SCORE
    # ==========================================================

    def sector_leadership(

        self,

    ) -> Dict:

        strength = self.sector_strength()

        momentum = self.sector_momentum()

        leadership = {}

        for sector in strength.keys():

            score = (

                strength[sector]["score"] * 0.60

                +

                momentum.get(

                    sector,

                    50,

                ) * 0.40

            )

            leadership[sector] = round(

                score,

                2,

            )

        return leadership

    # ==========================================================
    # SECTOR BREADTH
    # ==========================================================

    def sector_breadth(

        self,

    ) -> Dict:

        if self.sector_data is None:

            return {}

        result = {}

        for _, row in self.sector_data.iterrows():

            sector = row["Sector"]

            adv = row.get(

                "Advances",

                0,

            )

            dec = row.get(

                "Declines",

                0,

            )

            total = max(

                adv + dec,

                1,

            )

            result[sector] = round(

                adv /

                total *

                100,

                2,

            )

        return result

    # ==========================================================
    # AI SECTOR ROTATION SCORE
    # ==========================================================

    def ai_sector_rotation_score(

        self,

    ) -> float:

        leadership = self.sector_leadership()

        if not leadership:

            return 0.0

        scores = list(

            leadership.values()

        )

        top5 = sorted(

            scores,

            reverse=True,

        )[:5]

        return round(

            np.mean(

                top5,

            ),

            2,

        )
        # ==========================================================
    # FII ACTIVITY ANALYSIS
    # ==========================================================

    def fii_activity(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {}

        fii_buy = self.index_data.get(

            "FIIBuy",

            pd.Series([0]),

        ).sum()

        fii_sell = self.index_data.get(

            "FIISell",

            pd.Series([0]),

        ).sum()

        net = fii_buy - fii_sell

        score = 50

        if net > 0:

            score += min(

                abs(net) / 100,

                50,

            )

        else:

            score -= min(

                abs(net) / 100,

                50,

            )

        return {

            "buy": round(fii_buy, 2),

            "sell": round(fii_sell, 2),

            "net": round(net, 2),

            "score": round(

                max(

                    0,

                    min(score, 100),

                ),

                2,

            ),

        }

    # ==========================================================
    # DII ACTIVITY ANALYSIS
    # ==========================================================

    def dii_activity(

        self,

    ) -> Dict:

        if self.index_data is None:

            return {}

        dii_buy = self.index_data.get(

            "DIIBuy",

            pd.Series([0]),

        ).sum()

        dii_sell = self.index_data.get(

            "DIISell",

            pd.Series([0]),

        ).sum()

        net = dii_buy - dii_sell

        score = 50

        if net > 0:

            score += min(

                abs(net) / 100,

                50,

            )

        else:

            score -= min(

                abs(net) / 100,

                50,

            )

        return {

            "buy": round(dii_buy, 2),

            "sell": round(dii_sell, 2),

            "net": round(net, 2),

            "score": round(

                max(

                    0,

                    min(score, 100),

                ),

                2,

            ),

        }

    # ==========================================================
    # COMBINED FII/DII SCORE
    # ==========================================================

    def fii_dii_score(

        self,

    ) -> Dict:

        fii = self.fii_activity()

        dii = self.dii_activity()

        if not fii or not dii:

            return {}

        score = (

            fii["score"] * 0.60 +

            dii["score"] * 0.40

        )

        sentiment = "Neutral"

        if score >= 75:

            sentiment = "Strong Buying"

        elif score >= 60:

            sentiment = "Buying"

        elif score <= 25:

            sentiment = "Strong Selling"

        elif score <= 40:

            sentiment = "Selling"

        return {

            "score": round(score, 2),

            "sentiment": sentiment,

            "fii": fii,

            "dii": dii,

        }

    # ==========================================================
    # DELIVERY PERCENTAGE
    # ==========================================================

    def delivery_analysis(

        self,

    ) -> Dict:

        if "DeliveryPercent" not in self.stock_data.columns:

            return {}

        avg_delivery = self.stock_data[

            "DeliveryPercent"

        ].mean()

        high_delivery = (

            self.stock_data[

                "DeliveryPercent"

            ] >= 60

        ).sum()

        score = min(

            avg_delivery,

            100,

        )

        return {

            "average_delivery": round(

                avg_delivery,

                2,

            ),

            "high_delivery_stocks": int(

                high_delivery,

            ),

            "score": round(score, 2),

        }

    # ==========================================================
    # INSTITUTIONAL PARTICIPATION
    # ==========================================================

    def institutional_participation(

        self,

    ) -> Dict:

        fii = self.fii_activity()

        dii = self.dii_activity()

        delivery = self.delivery_analysis()

        if not fii or not dii:

            return {}

        delivery_score = delivery.get(

            "score",

            50,

        )

        score = (

            fii["score"] * 0.40 +

            dii["score"] * 0.30 +

            delivery_score * 0.30

        )

        return {

            "score": round(score, 2),

            "delivery": delivery,

        }

    # ==========================================================
    # SMART MONEY FLOW
    # ==========================================================

    def smart_money_flow(

        self,

    ) -> Dict:

        fii = self.fii_activity()

        dii = self.dii_activity()

        if not fii or not dii:

            return {}

        net = fii["net"] + dii["net"]

        direction = "Neutral"

        if net > 0:

            direction = "Buying"

        elif net < 0:

            direction = "Selling"

        strength = min(

            abs(net) / 100,

            100,

        )

        return {

            "direction": direction,

            "net_flow": round(net, 2),

            "strength": round(strength, 2),

        }

    # ==========================================================
    # BUYING / SELLING PRESSURE
    # ==========================================================

    def buying_pressure(

        self,

    ) -> Dict:

        advances = len(self.advances)

        declines = len(self.declines)

        pressure = self.advance_decline_ratio()

        sentiment = "Neutral"

        if pressure >= 2:

            sentiment = "Strong Buying"

        elif pressure >= 1.2:

            sentiment = "Buying"

        elif pressure <= 0.5:

            sentiment = "Strong Selling"

        elif pressure <= 0.8:

            sentiment = "Selling"

        return {

            "advances": advances,

            "declines": declines,

            "ratio": pressure,

            "sentiment": sentiment,

        }

    # ==========================================================
    # INSTITUTIONAL BREADTH SCORE
    # ==========================================================

    def institutional_breadth_score(

        self,

    ) -> float:

        participation = self.institutional_participation()

        pressure = self.buying_pressure()

        if not participation:

            return 0.0

        ratio_score = min(

            pressure["ratio"] * 40,

            100,

        )

        score = (

            participation["score"] * 0.70 +

            ratio_score * 0.30

        )

        return round(

            min(score, 100),

            2,

        )
        # ==========================================================
    # AI MARKET HEALTH ENGINE
    # ==========================================================

    def ai_market_health(

        self,

    ) -> Dict:

        health = self.market_health()

        index = self.index_strength()

        institutional = self.institutional_breadth_score()

        participation = self.market_participation()[

            "participation_score"

        ]

        score = (

            health * 0.35 +

            index["strength"] * 0.30 +

            institutional * 0.20 +

            participation * 0.15

        )

        return {

            "health_score": round(score, 2),

            "market_health": round(health, 2),

            "index_strength": round(

                index["strength"],

                2,

            ),

            "institutional": round(

                institutional,

                2,

            ),

            "participation": round(

                participation,

                2,

            ),

        }

    # ==========================================================
    # AI BREADTH SCORE
    # ==========================================================

    def ai_breadth_score(

        self,

    ) -> float:

        health = self.ai_market_health()[

            "health_score"

        ]

        sector = self.ai_sector_rotation_score()

        breadth = self.breadth_momentum() + 100

        breadth /= 2

        score = (

            health * 0.50 +

            sector * 0.25 +

            breadth * 0.25

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # MARKET SENTIMENT
    # ==========================================================

    def market_sentiment(

        self,

    ) -> str:

        score = self.ai_breadth_score()

        if score >= 85:

            return "Extremely Bullish"

        if score >= 70:

            return "Bullish"

        if score >= 55:

            return "Neutral"

        if score >= 40:

            return "Bearish"

        return "Extremely Bearish"

    # ==========================================================
    # RISK ON / RISK OFF
    # ==========================================================

    def risk_mode(

        self,

    ) -> Dict:

        sentiment = self.market_sentiment()

        institutional = self.institutional_breadth_score()

        sector = self.ai_sector_rotation_score()

        risk_on = (

            institutional >= 65

            and

            sector >= 65

        )

        return {

            "mode":

                "Risk-On"

                if risk_on

                else "Risk-Off",

            "institutional_score":

                round(

                    institutional,

                    2,

                ),

            "sector_score":

                round(

                    sector,

                    2,

                ),

            "sentiment":

                sentiment,

        }

    # ==========================================================
    # INTERNAL MARKET STRENGTH
    # ==========================================================

    def internal_strength(

        self,

    ) -> Dict:

        adv = self.advance_percentage()

        nh = self.new_highs()

        nl = self.new_lows()

        ratio = self.advance_decline_ratio()

        score = (

            adv * 0.50 +

            min(

                ratio * 20,

                100,

            ) * 0.30 +

            (

                100

                if nh > nl

                else 40

            ) * 0.20

        )

        return {

            "score": round(score, 2),

            "new_highs": nh,

            "new_lows": nl,

            "advance_decline":

                round(

                    ratio,

                    2,

                ),

        }

    # ==========================================================
    # BREADTH TREND
    # ==========================================================

    def breadth_trend(

        self,

    ) -> Dict:

        momentum = self.breadth_momentum()

        score = self.ai_breadth_score()

        trend = "Sideways"

        if momentum > 20:

            trend = "Strong Uptrend"

        elif momentum > 5:

            trend = "Uptrend"

        elif momentum < -20:

            trend = "Strong Downtrend"

        elif momentum < -5:

            trend = "Downtrend"

        return {

            "trend": trend,

            "momentum": round(

                momentum,

                2,

            ),

            "score": round(

                score,

                2,

            ),

        }

    # ==========================================================
    # BREADTH WARNINGS
    # ==========================================================

    def breadth_warnings(

        self,

    ) -> List[str]:

        warnings = []

        if self.advance_decline_ratio() < 0.80:

            warnings.append(

                "Declining stocks significantly outnumber advancing stocks."

            )

        if self.new_lows() > self.new_highs():

            warnings.append(

                "New lows exceed new highs."

            )

        if self.institutional_breadth_score() < 40:

            warnings.append(

                "Institutional participation is weak."

            )

        if self.ai_sector_rotation_score() < 50:

            warnings.append(

                "Sector rotation is deteriorating."

            )

        if self.market_sentiment() in [

            "Bearish",

            "Extremely Bearish",

        ]:

            warnings.append(

                "Overall market breadth is bearish."

            )

        return warnings

    # ==========================================================
    # AI REMARKS
    # ==========================================================

    def ai_remarks(

        self,

    ) -> List[str]:

        remarks = []

        sentiment = self.market_sentiment()

        remarks.append(

            f"Market Sentiment: {sentiment}"

        )

        risk = self.risk_mode()

        remarks.append(

            f"Current Mode: {risk['mode']}"

        )

        trend = self.breadth_trend()

        remarks.append(

            f"Breadth Trend: {trend['trend']}"

        )

        institutional = self.institutional_breadth_score()

        if institutional >= 70:

            remarks.append(

                "Institutional buying supports the trend."

            )

        elif institutional <= 40:

            remarks.append(

                "Institutional participation remains weak."

            )

        if self.ai_sector_rotation_score() >= 70:

            remarks.append(

                "Leadership is concentrated in strong sectors."

            )

        return remarks
        # ==========================================================
    # MASTER ANALYSIS
    # ==========================================================

    def analyze(

        self,

    ) -> BreadthResult:

        advance_count = len(

            self.advances

        )

        decline_count = len(

            self.declines

        )

        unchanged_count = len(

            self.unchanged

        )

        ad_ratio = self.advance_decline_ratio()

        new_highs = self.new_highs()

        new_lows = self.new_lows()

        bullish = self.bullish_percentage()

        bearish = self.bearish_percentage()

        health = self.ai_market_health()

        breadth_score = self.ai_breadth_score()

        sentiment = self.market_sentiment()

        sector_strength = self.sector_strength()

        sector_rotation = self.sector_rotation()

        fii_dii = self.fii_dii_score()

        delivery = self.delivery_analysis()

        indicators = {

            "IndexStrength":

                self.index_strength(),

            "Participation":

                self.market_participation(),

            "BreadthTrend":

                self.breadth_trend(),

            "RiskMode":

                self.risk_mode(),

            "InternalStrength":

                self.internal_strength(),

            "Institutional":

                self.institutional_participation(),

            "SmartMoney":

                self.smart_money_flow(),

            "BuyingPressure":

                self.buying_pressure(),

        }

        remarks = self.ai_remarks()

        remarks.extend(

            self.breadth_warnings()

        )

        self.result = BreadthResult(

            market=self.market,

            advance_count=advance_count,

            decline_count=decline_count,

            unchanged_count=unchanged_count,

            advance_decline_ratio=ad_ratio,

            new_highs=new_highs,

            new_lows=new_lows,

            bullish_percent=bullish,

            bearish_percent=bearish,

            health_score=health["health_score"],

            breadth_score=breadth_score,

            sentiment=sentiment,

            sector_strength=sector_strength,

            sector_rotation=sector_rotation,

            fii_dii=fii_dii,

            delivery=delivery,

            indicators=indicators,

            remarks=remarks,

        )

        return self.result

    # ==========================================================
    # GET RESULT
    # ==========================================================

    def get_result(

        self,

    ) -> Optional[BreadthResult]:

        return self.result

    # ==========================================================
    # RESULT TO DICTIONARY
    # ==========================================================

    def to_dict(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "market":

                self.result.market,

            "advance_count":

                self.result.advance_count,

            "decline_count":

                self.result.decline_count,

            "unchanged_count":

                self.result.unchanged_count,

            "advance_decline_ratio":

                self.result.advance_decline_ratio,

            "new_highs":

                self.result.new_highs,

            "new_lows":

                self.result.new_lows,

            "bullish_percent":

                self.result.bullish_percent,

            "bearish_percent":

                self.result.bearish_percent,

            "health_score":

                self.result.health_score,

            "breadth_score":

                self.result.breadth_score,

            "sentiment":

                self.result.sentiment,

            "sector_strength":

                self.result.sector_strength,

            "sector_rotation":

                self.result.sector_rotation,

            "fii_dii":

                self.result.fii_dii,

            "delivery":

                self.result.delivery,

            "indicators":

                self.result.indicators,

            "remarks":

                self.result.remarks,

        }

    # ==========================================================
    # JSON OUTPUT
    # ==========================================================

    def json(

        self,

    ) -> Dict:

        return self.to_dict()

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "Market":

                self.result.market,

            "Sentiment":

                self.result.sentiment,

            "Breadth Score":

                self.result.breadth_score,

            "Health Score":

                self.result.health_score,

            "Advance/Decline":

                f"{self.result.advance_count}/{self.result.decline_count}",

            "New Highs":

                self.result.new_highs,

            "New Lows":

                self.result.new_lows,

        }

    # ==========================================================
    # DASHBOARD CARD
    # ==========================================================

    def dashboard(

        self,

    ) -> Dict:

        if self.result is None:

            self.analyze()

        return {

            "Market":

                self.result.market,

            "Breadth":

                round(

                    self.result.breadth_score,

                    2,

                ),

            "Health":

                round(

                    self.result.health_score,

                    2,

                ),

            "Sentiment":

                self.result.sentiment,

            "Advances":

                self.result.advance_count,

            "Declines":

                self.result.decline_count,

            "AI Score":

                round(

                    self.result.breadth_score,

                    2,

                ),

            "Risk Mode":

                self.risk_mode()["mode"],

        }

    # ==========================================================
    # PRINT REPORT
    # ==========================================================

    def print_report(

        self,

    ):

        if self.result is None:

            self.analyze()

        print("=" * 60)

        print("STOCKVERSITY AI MARKET BREADTH REPORT")

        print("=" * 60)

        print(f"Market           : {self.result.market}")

        print(f"Sentiment        : {self.result.sentiment}")

        print(f"Breadth Score    : {self.result.breadth_score:.2f}")

        print(f"Health Score     : {self.result.health_score:.2f}")

        print(f"Advance          : {self.result.advance_count}")

        print(f"Decline          : {self.result.decline_count}")

        print(f"Advance/Decline  : {self.result.advance_decline_ratio:.2f}")

        print(f"New Highs        : {self.result.new_highs}")

        print(f"New Lows         : {self.result.new_lows}")

        print()

        print("REMARKS")

        print("-" * 60)

        for remark in self.result.remarks:

            print(f"• {remark}")

        print()

        print("INDICATORS")

        print("-" * 60)

        for key, value in self.result.indicators.items():

            print(f"{key:25} : {value}")

        print("=" * 60)

    # ==========================================================
    # CALL SHORTCUT
    # ==========================================================

    def __call__(

        self,

    ) -> BreadthResult:

        return self.analyze()
        # ==========================================================
    # MULTI-TIMEFRAME BREADTH CONFIRMATION
    # ==========================================================

    def multi_timeframe_confirmation(

        self,

    ) -> Dict:

        daily = self.market_health()

        weekly = daily * 0.95

        monthly = daily * 0.90

        score = (

            daily * 0.50 +

            weekly * 0.30 +

            monthly * 0.20

        )

        confirmed = score >= 65

        return {

            "daily": round(daily, 2),

            "weekly": round(weekly, 2),

            "monthly": round(monthly, 2),

            "score": round(score, 2),

            "confirmed": confirmed,

        }

    # ==========================================================
    # BREADTH DIVERGENCE
    # ==========================================================

    def breadth_divergence(

        self,

    ) -> Dict:

        market = self.market_health()

        participation = self.market_participation()[

            "participation_score"

        ]

        divergence = abs(

            market - participation

        )

        detected = divergence > 20

        direction = "None"

        if detected:

            direction = (

                "Bullish"

                if participation > market

                else "Bearish"

            )

        return {

            "detected": detected,

            "direction": direction,

            "difference": round(divergence, 2),

            "score": round(

                min(divergence * 2, 100),

                2,

            ),

        }

    # ==========================================================
    # BREADTH THRUST
    # ==========================================================

    def breadth_thrust(

        self,

    ) -> Dict:

        adv = self.advance_percentage()

        ratio = self.advance_decline_ratio()

        detected = (

            adv >= 75

            and

            ratio >= 2.0

        )

        score = (

            adv * 0.60 +

            min(

                ratio * 20,

                100,

            ) * 0.40

        )

        return {

            "detected": detected,

            "score": round(score, 2),

            "advance_percent": adv,

            "ratio": ratio,

        }

    # ==========================================================
    # MARKET EXHAUSTION
    # ==========================================================

    def market_exhaustion(

        self,

    ) -> Dict:

        nh = self.new_highs()

        nl = self.new_lows()

        participation = self.market_participation()[

            "participation_score"

        ]

        exhausted = (

            participation > 80

            and

            nh < nl

        )

        score = (

            100

            if exhausted

            else 20

        )

        return {

            "detected": exhausted,

            "score": score,

            "new_highs": nh,

            "new_lows": nl,

        }

    # ==========================================================
    # EXPANSION / CONTRACTION
    # ==========================================================

    def market_expansion(

        self,

    ) -> Dict:

        breadth = abs(

            self.breadth_momentum()

        )

        expanding = breadth > 20

        state = (

            "Expansion"

            if expanding

            else "Contraction"

        )

        return {

            "state": state,

            "score": round(

                min(

                    breadth,

                    100,

                ),

                2,

            ),

        }

    # ==========================================================
    # VOLATILITY BREADTH
    # ==========================================================

    def volatility_breadth(

        self,

    ) -> Dict:

        volatility = (

            (

                self.stock_data["High"]

                -

                self.stock_data["Low"]

            )

            /

            self.stock_data["Close"]

        ).mean() * 100

        score = max(

            0,

            100 - volatility * 8,

        )

        return {

            "volatility":

                round(volatility, 2),

            "score":

                round(score, 2),

        }

    # ==========================================================
    # AI CONVICTION SCORE
    # ==========================================================

    def conviction_score(

        self,

    ) -> float:

        health = self.market_health()

        breadth = self.ai_breadth_score()

        institutional = self.institutional_breadth_score()

        mtf = self.multi_timeframe_confirmation()[

            "score"

        ]

        score = (

            health * 0.30 +

            breadth * 0.30 +

            institutional * 0.20 +

            mtf * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # INSTITUTIONAL MARKET QUALITY
    # ==========================================================

    def institutional_market_quality(

        self,

    ) -> Dict:

        conviction = self.conviction_score()

        thrust = self.breadth_thrust()

        divergence = self.breadth_divergence()

        volatility = self.volatility_breadth()

        score = (

            conviction * 0.45 +

            thrust["score"] * 0.20 +

            volatility["score"] * 0.20 +

            (

                100

                if not divergence["detected"]

                else 40

            ) * 0.15

        )

        return {

            "quality_score": round(score, 2),

            "institutional_grade": (

                "Excellent"

                if score >= 85

                else "Good"

                if score >= 70

                else "Average"

                if score >= 55

                else "Weak"

            ),

            "approved": score >= 70,

            "conviction": conviction,

            "breadth_thrust": thrust,

            "divergence": divergence,

            "volatility": volatility,

        }
        # ==========================================================
    # MULTI-TIMEFRAME BREADTH CONFIRMATION
    # ==========================================================

    def multi_timeframe_confirmation(

        self,

    ) -> Dict:

        daily = self.market_health()

        weekly = daily * 0.95

        monthly = daily * 0.90

        score = (

            daily * 0.50 +

            weekly * 0.30 +

            monthly * 0.20

        )

        confirmed = score >= 65

        return {

            "daily": round(daily, 2),

            "weekly": round(weekly, 2),

            "monthly": round(monthly, 2),

            "score": round(score, 2),

            "confirmed": confirmed,

        }

    # ==========================================================
    # BREADTH DIVERGENCE
    # ==========================================================

    def breadth_divergence(

        self,

    ) -> Dict:

        market = self.market_health()

        participation = self.market_participation()[

            "participation_score"

        ]

        divergence = abs(

            market - participation

        )

        detected = divergence > 20

        direction = "None"

        if detected:

            direction = (

                "Bullish"

                if participation > market

                else "Bearish"

            )

        return {

            "detected": detected,

            "direction": direction,

            "difference": round(divergence, 2),

            "score": round(

                min(divergence * 2, 100),

                2,

            ),

        }

    # ==========================================================
    # BREADTH THRUST
    # ==========================================================

    def breadth_thrust(

        self,

    ) -> Dict:

        adv = self.advance_percentage()

        ratio = self.advance_decline_ratio()

        detected = (

            adv >= 75

            and

            ratio >= 2.0

        )

        score = (

            adv * 0.60 +

            min(

                ratio * 20,

                100,

            ) * 0.40

        )

        return {

            "detected": detected,

            "score": round(score, 2),

            "advance_percent": adv,

            "ratio": ratio,

        }

    # ==========================================================
    # MARKET EXHAUSTION
    # ==========================================================

    def market_exhaustion(

        self,

    ) -> Dict:

        nh = self.new_highs()

        nl = self.new_lows()

        participation = self.market_participation()[

            "participation_score"

        ]

        exhausted = (

            participation > 80

            and

            nh < nl

        )

        score = (

            100

            if exhausted

            else 20

        )

        return {

            "detected": exhausted,

            "score": score,

            "new_highs": nh,

            "new_lows": nl,

        }

    # ==========================================================
    # EXPANSION / CONTRACTION
    # ==========================================================

    def market_expansion(

        self,

    ) -> Dict:

        breadth = abs(

            self.breadth_momentum()

        )

        expanding = breadth > 20

        state = (

            "Expansion"

            if expanding

            else "Contraction"

        )

        return {

            "state": state,

            "score": round(

                min(

                    breadth,

                    100,

                ),

                2,

            ),

        }

    # ==========================================================
    # VOLATILITY BREADTH
    # ==========================================================

    def volatility_breadth(

        self,

    ) -> Dict:

        volatility = (

            (

                self.stock_data["High"]

                -

                self.stock_data["Low"]

            )

            /

            self.stock_data["Close"]

        ).mean() * 100

        score = max(

            0,

            100 - volatility * 8,

        )

        return {

            "volatility":

                round(volatility, 2),

            "score":

                round(score, 2),

        }

    # ==========================================================
    # AI CONVICTION SCORE
    # ==========================================================

    def conviction_score(

        self,

    ) -> float:

        health = self.market_health()

        breadth = self.ai_breadth_score()

        institutional = self.institutional_breadth_score()

        mtf = self.multi_timeframe_confirmation()[

            "score"

        ]

        score = (

            health * 0.30 +

            breadth * 0.30 +

            institutional * 0.20 +

            mtf * 0.20

        )

        return round(

            min(

                score,

                100,

            ),

            2,

        )

    # ==========================================================
    # INSTITUTIONAL MARKET QUALITY
    # ==========================================================

    def institutional_market_quality(

        self,

    ) -> Dict:

        conviction = self.conviction_score()

        thrust = self.breadth_thrust()

        divergence = self.breadth_divergence()

        volatility = self.volatility_breadth()

        score = (

            conviction * 0.45 +

            thrust["score"] * 0.20 +

            volatility["score"] * 0.20 +

            (

                100

                if not divergence["detected"]

                else 40

            ) * 0.15

        )

        return {

            "quality_score": round(score, 2),

            "institutional_grade": (

                "Excellent"

                if score >= 85

                else "Good"

                if score >= 70

                else "Average"

                if score >= 55

                else "Weak"

            ),

            "approved": score >= 70,

            "conviction": conviction,

            "breadth_thrust": thrust,

            "divergence": divergence,

            "volatility": volatility,

        }
        # ==========================================================
    # EXPORT TO JSON
    # ==========================================================

    def export_json(

        self,

    ) -> str:

        if self.result is None:

            self.analyze()

        return json.dumps(

            self.to_dict(),

            indent=4,

            default=str,

        )

    # ==========================================================
    # EXPORT TO DATAFRAME
    # ==========================================================

    def export_dataframe(

        self,

    ) -> pd.DataFrame:

        if self.result is None:

            self.analyze()

        data = {

            "Market": [self.result.market],

            "Sentiment": [self.result.sentiment],

            "BreadthScore": [self.result.breadth_score],

            "HealthScore": [self.result.health_score],

            "Advance": [self.result.advance_count],

            "Decline": [self.result.decline_count],

            "AdvanceDeclineRatio": [

                self.result.advance_decline_ratio

            ],

            "NewHighs": [self.result.new_highs],

            "NewLows": [self.result.new_lows],

        }

        return pd.DataFrame(data)

    # ==========================================================
    # SAVE REPORT
    # ==========================================================

    def save_report(

        self,

        filename: str,

    ) -> bool:

        try:

            with open(

                filename,

                "w",

                encoding="utf-8",

            ) as file:

                file.write(

                    self.export_json()

                )

            return True

        except Exception:

            return False

    # ==========================================================
    # LOAD REPORT
    # ==========================================================

    @staticmethod

    def load_report(

        filename: str,

    ) -> Dict:

        with open(

            filename,

            "r",

            encoding="utf-8",

        ) as file:

            return json.load(file)

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate_result(

        self,

    ) -> bool:

        if self.result is None:

            return False

        mandatory = [

            self.result.market,

            self.result.sentiment,

            self.result.breadth_score,

            self.result.health_score,

        ]

        return all(

            value is not None

            for value in mandatory

        )

    # ==========================================================
    # DEBUG INFORMATION
    # ==========================================================

    def debug(

        self,

    ) -> Dict:

        return {

            "Stocks":

                len(self.stock_data),

            "Advances":

                len(self.advances),

            "Declines":

                len(self.declines),

            "Unchanged":

                len(self.unchanged),

            "BreadthScore":

                self.ai_breadth_score(),

            "HealthScore":

                self.ai_market_health()["health_score"],

            "Conviction":

                self.conviction_score(),

            "Institutional":

                self.institutional_breadth_score(),

            "SectorRotation":

                self.ai_sector_rotation_score(),

        }

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================

    def performance_metrics(

        self,

    ) -> Dict:

        score = self.conviction_score()

        quality = self.institutional_market_quality()

        return {

            "Conviction":

                score,

            "InstitutionalGrade":

                quality["institutional_grade"],

            "Approved":

                quality["approved"],

            "TradeEnvironment":

                self.trade_environment()["environment"],

            "Portfolio":

                self.portfolio_allocation(),

        }

    # ==========================================================
    # COMPLETE REPORT
    # ==========================================================

    def complete_report(

        self,

    ) -> Dict:

        return {

            "summary":

                self.summary(),

            "dashboard":

                self.dashboard(),

            "snapshot":

                self.market_snapshot(),

            "scorecard":

                self.market_scorecard(),

            "scanner":

                self.scanner_output(),

            "opportunity":

                self.opportunity_rating(),

            "portfolio":

                self.portfolio_allocation(),

            "performance":

                self.performance_metrics(),

            "remarks":

                self.ai_remarks(),

            "warnings":

                self.breadth_warnings(),

        }

    # ==========================================================
    # FINAL WRAPPER
    # ==========================================================

    def run(

        self,

    ) -> Dict:

        self.analyze()

        return self.complete_report()

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(

        self,

    ) -> str:

        if self.result is None:

            self.analyze()

        return (

            f"<MarketBreadthEngine "

            f"Market={self.result.market} "

            f"Sentiment={self.result.sentiment} "

            f"Breadth={self.result.breadth_score:.2f}>"

        )

    # ==========================================================
    # LENGTH
    # ==========================================================

    def __len__(

        self,

    ) -> int:

        return len(

            self.stock_data

        )

    # ==========================================================
    # END OF MODULE
    # ==========================================================
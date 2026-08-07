from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Opportunity:

    symbol: str

    company_name: str = ""

    sector: str = ""

    signal: str = ""

    pattern: str = ""

    timeframe: str = ""

    entry: float = 0.0

    stop_loss: float = 0.0

    target: float = 0.0

    risk_reward: float = 0.0

    ai_score: float = 0.0

    confidence: float = 0.0

    probability: float = 0.0

    volume_score: float = 0.0

    momentum_score: float = 0.0

    trend_score: float = 0.0

    delivery_score: float = 0.0

    relative_strength: float = 0.0

    recommendation: str = ""

    reason: str = ""

    scanner_name: str = ""

    strategy: str = ""

    exchange: str = "NSE"

    market_cap: float = 0.0

    price: float = 0.0

    change_percent: float = 0.0

    created_at: datetime = field(
        default_factory=datetime.now
    )

    updated_at: datetime = field(
        default_factory=datetime.now
    )

    # -------------------------------------------------

    @property
    def risk(self):

        return max(
            self.entry - self.stop_loss,
            0,
        )

    # -------------------------------------------------

    @property
    def reward(self):

        return max(
            self.target - self.entry,
            0,
        )

    # -------------------------------------------------

    @property
    def expected_return(self):

        if self.entry == 0:
            return 0

        return round(
            ((self.target - self.entry) / self.entry) * 100,
            2,
        )

    # -------------------------------------------------

    @property
    def stop_loss_percent(self):

        if self.entry == 0:
            return 0

        return round(
            ((self.entry - self.stop_loss) / self.entry) * 100,
            2,
        )

    # -------------------------------------------------

    @property
    def is_buy(self):

        return self.signal.upper() == "BUY"

    # -------------------------------------------------

    @property
    def is_sell(self):

        return self.signal.upper() == "SELL"

    # -------------------------------------------------

    def score(self):

        return round(

            (
                self.ai_score * 0.35
                + self.confidence * 0.20
                + self.momentum_score * 0.15
                + self.trend_score * 0.15
                + self.volume_score * 0.10
                + self.delivery_score * 0.05
            ),

            2,

        )

    # -------------------------------------------------

    def to_dict(self):

        return {

            "symbol": self.symbol,

            "company_name": self.company_name,

            "sector": self.sector,

            "signal": self.signal,

            "pattern": self.pattern,

            "timeframe": self.timeframe,

            "entry": self.entry,

            "stop_loss": self.stop_loss,

            "target": self.target,

            "risk_reward": self.risk_reward,

            "ai_score": self.ai_score,

            "confidence": self.confidence,

            "probability": self.probability,

            "volume_score": self.volume_score,

            "momentum_score": self.momentum_score,

            "trend_score": self.trend_score,

            "delivery_score": self.delivery_score,

            "relative_strength": self.relative_strength,

            "recommendation": self.recommendation,

            "reason": self.reason,

            "scanner_name": self.scanner_name,

            "strategy": self.strategy,

            "exchange": self.exchange,

            "market_cap": self.market_cap,

            "price": self.price,

            "change_percent": self.change_percent,

            "created_at": self.created_at.isoformat(),

            "updated_at": self.updated_at.isoformat(),

        }
        # -------------------------------------------------

    @classmethod
    def from_dict(cls, data):

        created = data.get("created_at")
        updated = data.get("updated_at")

        if isinstance(created, str):
            created = datetime.fromisoformat(created)

        if isinstance(updated, str):
            updated = datetime.fromisoformat(updated)

        return cls(

            symbol=data.get("symbol", ""),

            company_name=data.get("company_name", ""),

            sector=data.get("sector", ""),

            signal=data.get("signal", ""),

            pattern=data.get("pattern", ""),

            timeframe=data.get("timeframe", ""),

            entry=float(data.get("entry", 0)),

            stop_loss=float(data.get("stop_loss", 0)),

            target=float(data.get("target", 0)),

            risk_reward=float(data.get("risk_reward", 0)),

            ai_score=float(data.get("ai_score", 0)),

            confidence=float(data.get("confidence", 0)),

            probability=float(data.get("probability", 0)),

            volume_score=float(data.get("volume_score", 0)),

            momentum_score=float(data.get("momentum_score", 0)),

            trend_score=float(data.get("trend_score", 0)),

            delivery_score=float(data.get("delivery_score", 0)),

            relative_strength=float(
                data.get("relative_strength", 0)
            ),

            recommendation=data.get(
                "recommendation",
                "",
            ),

            reason=data.get(
                "reason",
                "",
            ),

            scanner_name=data.get(
                "scanner_name",
                "",
            ),

            strategy=data.get(
                "strategy",
                "",
            ),

            exchange=data.get(
                "exchange",
                "NSE",
            ),

            market_cap=float(
                data.get("market_cap", 0)
            ),

            price=float(
                data.get("price", 0)
            ),

            change_percent=float(
                data.get("change_percent", 0)
            ),

            created_at=created or datetime.now(),

            updated_at=updated or datetime.now(),

        )

    # -------------------------------------------------

    def clone(self):

        return Opportunity.from_dict(
            self.to_dict()
        )

    # -------------------------------------------------

    def update_timestamp(self):

        self.updated_at = datetime.now()

    # -------------------------------------------------

    def validate(self):

        if not self.symbol:

            return False

        if self.entry <= 0:

            return False

        if self.target <= 0:

            return False

        if self.stop_loss <= 0:

            return False

        if self.stop_loss >= self.entry:

            return False

        if self.target <= self.entry:

            return False

        return True

    # -------------------------------------------------

    def calculate_rr(self):

        risk = self.entry - self.stop_loss

        reward = self.target - self.entry

        if risk <= 0:

            self.risk_reward = 0

        else:

            self.risk_reward = round(
                reward / risk,
                2,
            )

        return self.risk_reward

    # -------------------------------------------------

    def update_price(

        self,

        latest_price,

    ):

        self.price = latest_price

        self.update_timestamp()

    # -------------------------------------------------

    def update_ai(

        self,

        ai_score,

        confidence,

        probability,

    ):

        self.ai_score = ai_score

        self.confidence = confidence

        self.probability = probability

        self.update_timestamp()

    # -------------------------------------------------

    def recommendation_color(self):

        signal = self.signal.upper()

        if signal == "BUY":

            return "#16A34A"

        if signal == "SELL":

            return "#DC2626"

        return "#F59E0B"

    # -------------------------------------------------

    def confidence_color(self):

        if self.confidence >= 90:

            return "#059669"

        if self.confidence >= 75:

            return "#10B981"

        if self.confidence >= 60:

            return "#F59E0B"

        return "#DC2626"

    # -------------------------------------------------

    def score_color(self):

        score = self.score()

        if score >= 90:

            return "#15803D"

        if score >= 80:

            return "#16A34A"

        if score >= 70:

            return "#65A30D"

        if score >= 60:

            return "#F59E0B"

        return "#DC2626"

    # -------------------------------------------------

    def quality_rank(self):

        score = self.score()

        if score >= 95:

            return "S+"

        if score >= 90:

            return "S"

        if score >= 85:

            return "A+"

        if score >= 80:

            return "A"

        if score >= 75:

            return "B+"

        if score >= 70:

            return "B"

        if score >= 60:

            return "C"

        return "D"

    # -------------------------------------------------

    def badge(self):

        if self.score() >= 90:

            return "🔥 High Conviction"

        if self.score() >= 80:

            return "⭐ Strong"

        if self.score() >= 70:

            return "✅ Good"

        if self.score() >= 60:

            return "⚠ Watch"

        return "❌ Weak"

    # -------------------------------------------------

    def sort_key(self):

        return (

            self.score(),

            self.ai_score,

            self.confidence,

            self.risk_reward,

            self.probability,

        )

    # -------------------------------------------------

    def __lt__(self, other):

        return self.sort_key() < other.sort_key()

    # -------------------------------------------------

    def __gt__(self, other):

        return self.sort_key() > other.sort_key()

    # -------------------------------------------------

    def __eq__(self, other):

        if not isinstance(other, Opportunity):

            return False

        return self.symbol == other.symbol

    # -------------------------------------------------

    def __hash__(self):

        return hash(self.symbol)
        # -------------------------------------------------

    def to_json(self):

        import json

        return json.dumps(
            self.to_dict(),
            indent=4,
            default=str,
        )

    # -------------------------------------------------

    @classmethod
    def from_json(
        cls,
        json_string,
    ):

        import json

        return cls.from_dict(
            json.loads(json_string)
        )

    # -------------------------------------------------

    def short_description(self):

        return (
            f"{self.symbol} | "
            f"{self.signal} | "
            f"{self.pattern}"
        )

    # -------------------------------------------------

    def full_description(self):

        return (
            f"{self.symbol} | "
            f"{self.company_name}\n"
            f"Signal : {self.signal}\n"
            f"Pattern : {self.pattern}\n"
            f"Entry : {self.entry:.2f}\n"
            f"Stop : {self.stop_loss:.2f}\n"
            f"Target : {self.target:.2f}\n"
            f"RR : {self.risk_reward:.2f}\n"
            f"AI Score : {self.ai_score:.2f}\n"
            f"Confidence : {self.confidence:.2f}%"
        )

    # -------------------------------------------------

    def dashboard_row(self):

        return [

            self.symbol,

            self.signal,

            self.pattern,

            self.timeframe,

            round(self.entry, 2),

            round(self.stop_loss, 2),

            round(self.target, 2),

            round(self.risk_reward, 2),

            round(self.ai_score, 2),

            round(self.confidence, 2),

            self.quality_rank(),

        ]

    # -------------------------------------------------

    def compact_dict(self):

        return {

            "symbol": self.symbol,

            "signal": self.signal,

            "pattern": self.pattern,

            "entry": self.entry,

            "target": self.target,

            "stop_loss": self.stop_loss,

            "rr": self.risk_reward,

            "score": self.score(),

            "confidence": self.confidence,

        }

    # -------------------------------------------------

    def update_from(
        self,
        other,
    ):

        if not isinstance(other, Opportunity):

            return

        self.company_name = other.company_name
        self.sector = other.sector
        self.signal = other.signal
        self.pattern = other.pattern
        self.timeframe = other.timeframe
        self.entry = other.entry
        self.stop_loss = other.stop_loss
        self.target = other.target
        self.risk_reward = other.risk_reward
        self.ai_score = other.ai_score
        self.confidence = other.confidence
        self.probability = other.probability
        self.volume_score = other.volume_score
        self.momentum_score = other.momentum_score
        self.trend_score = other.trend_score
        self.delivery_score = other.delivery_score
        self.relative_strength = other.relative_strength
        self.recommendation = other.recommendation
        self.reason = other.reason
        self.scanner_name = other.scanner_name
        self.strategy = other.strategy
        self.exchange = other.exchange
        self.market_cap = other.market_cap
        self.price = other.price
        self.change_percent = other.change_percent

        self.updated_at = datetime.now()

    # -------------------------------------------------

    @staticmethod
    def empty():

        return Opportunity(
            symbol="",
        )

    # -------------------------------------------------

    @staticmethod
    def buy(
        symbol,
        entry,
        stop_loss,
        target,
    ):

        obj = Opportunity(
            symbol=symbol,
            signal="BUY",
            entry=entry,
            stop_loss=stop_loss,
            target=target,
        )

        obj.calculate_rr()

        return obj

    # -------------------------------------------------

    @staticmethod
    def sell(
        symbol,
        entry,
        stop_loss,
        target,
    ):

        obj = Opportunity(
            symbol=symbol,
            signal="SELL",
            entry=entry,
            stop_loss=stop_loss,
            target=target,
        )

        obj.calculate_rr()

        return obj

    # -------------------------------------------------

    def __repr__(self):

        return (
            f"Opportunity("
            f"symbol='{self.symbol}', "
            f"signal='{self.signal}', "
            f"score={self.score():.2f})"
        )

    # -------------------------------------------------

    def __str__(self):

        return self.full_description()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Opportunity",

]
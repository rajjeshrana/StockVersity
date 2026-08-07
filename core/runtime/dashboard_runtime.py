"""
StockVersity Dashboard Runtime

Creates dashboard summary from scanner opportunities.

No UI code.
Pure business logic.
"""

from __future__ import annotations

from typing import Dict, List


class DashboardRuntime:

    def __init__(self):

        self.snapshot = {}

    # -------------------------------------------------

    def build_snapshot(
        self,
        opportunities: List[dict],
    ) -> Dict:

        opportunities = opportunities or []

        buy_count = 0
        sell_count = 0

        total_score = 0.0
        total_confidence = 0.0

        highest_score = 0.0

        top_opportunity = None

        for item in opportunities:

            signal = str(
                item.get(
                    "signal",
                    item.get(
                        "signal_type",
                        "",
                    ),
                )
            ).upper()

            if signal == "BUY":
                buy_count += 1

            elif signal == "SELL":
                sell_count += 1

            score = float(
                item.get(
                    "score",
                    0,
                )
                or 0
            )

            confidence = float(
                item.get(
                    "confidence",
                    0,
                )
                or 0
            )

            total_score += score
            total_confidence += confidence

            if score > highest_score:

                highest_score = score

                top_opportunity = item

        total = len(
            opportunities
        )

        average_score = (
            total_score / total
            if total
            else 0
        )

        average_confidence = (
            total_confidence / total
            if total
            else 0
        )

        self.snapshot = {

            "total":

                total,

            "buy":

                buy_count,

            "sell":

                sell_count,

            "average_score":

                round(
                    average_score,
                    2,
                ),

            "average_confidence":

                round(
                    average_confidence,
                    2,
                ),

            "highest_score":

                round(
                    highest_score,
                    2,
                ),

            "top":

                top_opportunity,

            "opportunities":

                opportunities,

        }

        return self.snapshot
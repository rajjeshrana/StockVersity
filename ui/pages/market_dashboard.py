from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QPieSlice,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from ui.widgets.info_card import InfoCard


class MarketDashboardPage(QWidget):

    def __init__(self, controller=None):
        super().__init__()

        self.controller = controller

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)

        self.build_ui()

        self.timer.start(60000)

        self.refresh_dashboard()

    # --------------------------------------------------

    def build_ui(self):

        root = QVBoxLayout(self)
        root.setContentsMargins(15,15,15,15)
        root.setSpacing(15)

        #
        # TITLE
        #

        title = QLabel("ðŸŒ Global Market Dashboard")
        title.setStyleSheet("""
            QLabel{
                font-size:28px;
                font-weight:bold;
            }
        """)

        root.addWidget(title)

        #
        # TOP ROW
        #

        top = QHBoxLayout()
        top.setSpacing(15)

        root.addLayout(top)

        ##################################################
        # LEFT
        ##################################################

        left = QVBoxLayout()

        top.addLayout(left,2)

        sentiment_frame = QFrame()
        sentiment_frame.setObjectName("Card")

        sentiment_layout = QVBoxLayout(sentiment_frame)

        lbl = QLabel("AI GLOBAL MARKET SENTIMENT")
        lbl.setAlignment(Qt.AlignCenter)

        lbl.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        sentiment_layout.addWidget(lbl)

        self.sentiment_chart = QChartView()

        self.sentiment_chart.setMinimumHeight(280)

        sentiment_layout.addWidget(self.sentiment_chart)

        self.sentiment_score = QLabel("Score : --")

        self.sentiment_score.setAlignment(Qt.AlignCenter)

        self.sentiment_score.setStyleSheet("""
        QLabel{
            font-size:22px;
            font-weight:bold;
        }
        """)

        sentiment_layout.addWidget(self.sentiment_score)

        self.sentiment_status = QLabel("--")

        self.sentiment_status.setAlignment(Qt.AlignCenter)

        self.sentiment_status.setStyleSheet("""
        QLabel{
            font-size:16px;
        }
        """)

        sentiment_layout.addWidget(self.sentiment_status)

        left.addWidget(sentiment_frame)
                ##################################################
        # RIGHT
        ##################################################

        right = QVBoxLayout()

        top.addLayout(right, 3)

        #
        # LIVE MARKET
        #

        market_title = QLabel("LIVE MARKET")
        market_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        right.addWidget(market_title)

        market_grid = QGridLayout()
        market_grid.setHorizontalSpacing(12)
        market_grid.setVerticalSpacing(12)

        right.addLayout(market_grid)

        #
        # NIFTY
        #

        self.card_nifty = InfoCard(
            title="NIFTY 50",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_nifty,0,0)

        #
        # BANK NIFTY
        #

        self.card_bank = InfoCard(
            title="BANK NIFTY",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_bank,0,1)

        #
        # GOLD
        #

        self.card_gold = InfoCard(
            title="XAU / USD",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_gold,1,0)

        #
        # USD INR
        #

        self.card_usd = InfoCard(
            title="USD / INR",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_usd,1,1)

        #
        # BRENT
        #

        self.card_brent = InfoCard(
            title="BRENT CRUDE",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_brent,2,0)

        #
        # INDIA VIX
        #

        self.card_vix = InfoCard(
            title="INDIA VIX",
            value="--",
            subtitle="Waiting..."
        )

        market_grid.addWidget(self.card_vix,2,1)

        #
        # LAST UPDATED
        #

        self.last_update = QLabel()

        self.last_update.setAlignment(Qt.AlignRight)

        self.last_update.setStyleSheet("""
        QLabel{
            color:gray;
            font-size:12px;
        }
        """)

        right.addWidget(self.last_update)

        ##################################################
        # MARKET BREADTH
        ##################################################

        breadth_frame = QFrame()
        breadth_frame.setObjectName("Card")

        root.addWidget(breadth_frame)

        breadth_layout = QVBoxLayout(breadth_frame)

        breadth_title = QLabel("MARKET BREADTH")

        breadth_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        breadth_layout.addWidget(breadth_title)

        breadth_grid = QGridLayout()

        breadth_layout.addLayout(breadth_grid)

        self.card_advances = InfoCard(
            title="Advances",
            value="0"
        )

        breadth_grid.addWidget(self.card_advances,0,0)

        self.card_declines = InfoCard(
            title="Declines",
            value="0"
        )

        breadth_grid.addWidget(self.card_declines,0,1)

        self.card_ratio = InfoCard(
            title="A/D Ratio",
            value="0"
        )

        breadth_grid.addWidget(self.card_ratio,0,2)

        self.card_above20 = InfoCard(
            title="Above 20 EMA",
            value="0%"
        )

        breadth_grid.addWidget(self.card_above20,1,0)

        self.card_above50 = InfoCard(
            title="Above 50 EMA",
            value="0%"
        )

        breadth_grid.addWidget(self.card_above50,1,1)

        self.card_above200 = InfoCard(
            title="Above 200 EMA",
            value="0%"
        )

        breadth_grid.addWidget(self.card_above200,1,2)
                ##################################################
        # FII / DII + OPTIONS ANALYTICS
        ##################################################

        analytics_layout = QHBoxLayout()
        analytics_layout.setSpacing(15)

        root.addLayout(analytics_layout)

        ##################################################
        # FII / DII PANEL
        ##################################################

        fii_frame = QFrame()
        fii_frame.setObjectName("Card")

        analytics_layout.addWidget(fii_frame)

        fii_layout = QVBoxLayout(fii_frame)

        fii_title = QLabel("INSTITUTIONAL ACTIVITY")
        fii_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        fii_layout.addWidget(fii_title)

        fii_grid = QGridLayout()

        fii_layout.addLayout(fii_grid)

        self.card_fii = InfoCard(
            title="FII Cash",
            value="â‚¹0 Cr",
            subtitle="Net"
        )

        fii_grid.addWidget(self.card_fii,0,0)

        self.card_dii = InfoCard(
            title="DII Cash",
            value="â‚¹0 Cr",
            subtitle="Net"
        )

        fii_grid.addWidget(self.card_dii,0,1)

        self.card_block = InfoCard(
            title="Block Deals",
            value="0",
            subtitle="Today"
        )

        fii_grid.addWidget(self.card_block,1,0)

        self.card_bulk = InfoCard(
            title="Bulk Deals",
            value="0",
            subtitle="Today"
        )

        fii_grid.addWidget(self.card_bulk,1,1)

        ##################################################
        # OPTIONS ANALYTICS
        ##################################################

        options_frame = QFrame()
        options_frame.setObjectName("Card")

        analytics_layout.addWidget(options_frame)

        options_layout = QVBoxLayout(options_frame)

        options_title = QLabel("OPTIONS ANALYTICS")
        options_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        options_layout.addWidget(options_title)

        option_grid = QGridLayout()

        options_layout.addLayout(option_grid)

        self.card_pcr = InfoCard(
            title="PCR",
            value="0.00",
            subtitle="NIFTY"
        )

        option_grid.addWidget(self.card_pcr,0,0)

        self.card_maxpain = InfoCard(
            title="Max Pain",
            value="--",
            subtitle="NIFTY"
        )

        option_grid.addWidget(self.card_maxpain,0,1)

        self.card_calloi = InfoCard(
            title="Highest Call OI",
            value="--",
            subtitle="Strike"
        )

        option_grid.addWidget(self.card_calloi,1,0)

        self.card_putoi = InfoCard(
            title="Highest Put OI",
            value="--",
            subtitle="Strike"
        )

        option_grid.addWidget(self.card_putoi,1,1)

        ##################################################
        # MARKET MOVERS
        ##################################################

        movers_frame = QFrame()
        movers_frame.setObjectName("Card")

        root.addWidget(movers_frame)

        movers_layout = QVBoxLayout(movers_frame)

        movers_title = QLabel("TOP MARKET MOVERS")
        movers_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        movers_layout.addWidget(movers_title)

        self.movers_table = QTableWidget()

        self.movers_table.setColumnCount(5)

        self.movers_table.setHorizontalHeaderLabels([
            "Symbol",
            "Price",
            "% Change",
            "Volume",
            "Signal"
        ])

        self.movers_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.movers_table.verticalHeader().setVisible(False)

        self.movers_table.setAlternatingRowColors(True)

        self.movers_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.movers_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.movers_table.setMinimumHeight(260)

        movers_layout.addWidget(self.movers_table)
                ##################################################
        # SECTOR HEATMAP + AI TRADES
        ##################################################

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        root.addLayout(bottom_layout)

        ##################################################
        # SECTOR HEATMAP
        ##################################################

        sector_frame = QFrame()
        sector_frame.setObjectName("Card")

        bottom_layout.addWidget(sector_frame, 3)

        sector_layout = QVBoxLayout(sector_frame)

        sector_title = QLabel("SECTOR HEATMAP")
        sector_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        sector_layout.addWidget(sector_title)

        sector_grid = QGridLayout()
        sector_grid.setHorizontalSpacing(12)
        sector_grid.setVerticalSpacing(12)

        sector_layout.addLayout(sector_grid)

        self.sector_cards = {}

        sectors = [
            "BANKING",
            "IT",
            "AUTO",
            "PHARMA",
            "FMCG",
            "METAL",
            "REALTY",
            "PSU",
            "ENERGY",
            "FINANCIAL"
        ]

        row = 0
        col = 0

        for sector in sectors:

            card = InfoCard(
                title=sector,
                value="0.00%",
                subtitle="Neutral"
            )

            self.sector_cards[sector] = card

            sector_grid.addWidget(card, row, col)

            col += 1

            if col > 1:
                col = 0
                row += 1

        ##################################################
        # AI BEST TRADES
        ##################################################

        ai_frame = QFrame()
        ai_frame.setObjectName("Card")

        bottom_layout.addWidget(ai_frame, 2)

        ai_layout = QVBoxLayout(ai_frame)

        ai_title = QLabel("TOP 5 AI TRADES")
        ai_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        ai_layout.addWidget(ai_title)

        self.ai_table = QTableWidget()

        self.ai_table.setColumnCount(6)

        self.ai_table.setHorizontalHeaderLabels([
            "Stock",
            "Strategy",
            "AI",
            "Entry",
            "SL",
            "Target"
        ])

        self.ai_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.ai_table.verticalHeader().setVisible(False)

        self.ai_table.setAlternatingRowColors(True)

        self.ai_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.ai_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.ai_table.setMinimumHeight(320)

        ai_layout.addWidget(self.ai_table)

        ##################################################
        # LIVE AI ALERTS
        ##################################################

        alerts_frame = QFrame()
        alerts_frame.setObjectName("Card")

        root.addWidget(alerts_frame)

        alerts_layout = QVBoxLayout(alerts_frame)

        alerts_title = QLabel("LIVE AI ALERTS")
        alerts_title.setStyleSheet("""
        QLabel{
            font-size:18px;
            font-weight:bold;
        }
        """)

        alerts_layout.addWidget(alerts_title)

        self.alerts_table = QTableWidget()

        self.alerts_table.setColumnCount(5)

        self.alerts_table.setHorizontalHeaderLabels([
            "Time",
            "Symbol",
            "Alert",
            "AI Score",
            "Action"
        ])

        self.alerts_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.alerts_table.verticalHeader().setVisible(False)

        self.alerts_table.setAlternatingRowColors(True)

        self.alerts_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.alerts_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.alerts_table.setMinimumHeight(220)

        alerts_layout.addWidget(self.alerts_table)
            # --------------------------------------------------
    # DASHBOARD REFRESH
    # --------------------------------------------------

    def refresh_dashboard(self):

        try:

            if self.controller:

                snapshot = self.controller.get_market_snapshot()

            else:

                snapshot = {}

        except Exception:

            snapshot = {}

        #
        # Update Live Markets
        #

        self.update_market_cards(snapshot)

        #
        # Update Sentiment
        #

        self.update_sentiment(snapshot)

        #
        # Update Time
        #

        self.last_update.setText(
            "Last Updated : "
            + datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
        )

    # --------------------------------------------------

    def update_market_cards(self, snapshot):

        cards = [

            (
                self.card_nifty,
                "nifty"
            ),

            (
                self.card_bank,
                "banknifty"
            ),

            (
                self.card_gold,
                "gold"
            ),

            (
                self.card_usd,
                "usdinr"
            ),

            (
                self.card_brent,
                "brent"
            ),

            (
                self.card_vix,
                "vix"
            )

        ]

        for card, key in cards:

            data = snapshot.get(key, {})

            price = data.get("price", "--")

            change = data.get("change", 0)

            percent = data.get("percent", 0)

            arrow = "â–²" if change >= 0 else "â–¼"

            subtitle = f"{arrow} {change:.2f} ({percent:.2f}%)"

            #
            # InfoCard API
            #

            if hasattr(card, "set_value"):

                card.set_value(str(price))

            if hasattr(card, "set_subtitle"):

                card.set_subtitle(subtitle)

            #
            # Colour
            #

            colour = "#16a34a" if change >= 0 else "#dc2626"

            try:

                card.setStyleSheet(f"""
                QFrame{{
                    border:1px solid #303030;
                    border-radius:10px;
                }}

                QLabel#value{{
                    color:{colour};
                    font-size:22px;
                    font-weight:bold;
                }}
                """)

            except Exception:

                pass

    # --------------------------------------------------

    def update_sentiment(self, snapshot):

        score = snapshot.get("ai_score", 50)

        score = max(0, min(100, score))

        greed = score

        fear = 100 - score

        series = QPieSeries()

        greed_slice = series.append("Greed", greed)

        fear_slice = series.append("Fear", fear)

        greed_slice.setLabelVisible(True)

        fear_slice.setLabelVisible(True)

        greed_slice.setBrush(QColor("#16a34a"))

        fear_slice.setBrush(QColor("#dc2626"))

        greed_slice.setExploded(True)

        greed_slice.setExplodeDistanceFactor(0.05)

        chart = QChart()

        chart.legend().setVisible(True)

        chart.addSeries(series)

        chart.setTitle("AI Fear & Greed")

        chart.setBackgroundVisible(False)

        chart.setAnimationOptions(QChart.SeriesAnimations)

        self.sentiment_chart.setChart(chart)

        self.sentiment_score.setText(f"{score} / 100")

        if score >= 80:

            text = "ðŸŸ¢ Extreme Greed"

        elif score >= 60:

            text = "ðŸŸ¢ Greed"

        elif score >= 40:

            text = "ðŸŸ¡ Neutral"

        elif score >= 20:

            text = "ðŸŸ  Fear"

        else:

            text = "ðŸ”´ Extreme Fear"

        self.sentiment_status.setText(text)
            # --------------------------------------------------
    # MARKET BREADTH
    # --------------------------------------------------

    def update_market_breadth(self, snapshot):

        breadth = snapshot.get("breadth", {})

        advances = breadth.get("advances", 0)
        declines = breadth.get("declines", 0)
        ratio = breadth.get("ratio", 0)

        above20 = breadth.get("above20", 0)
        above50 = breadth.get("above50", 0)
        above200 = breadth.get("above200", 0)

        #
        # Update Cards
        #

        if hasattr(self.card_advances, "set_value"):
            self.card_advances.set_value(str(advances))

        if hasattr(self.card_declines, "set_value"):
            self.card_declines.set_value(str(declines))

        if hasattr(self.card_ratio, "set_value"):
            self.card_ratio.set_value(f"{ratio:.2f}")

        if hasattr(self.card_above20, "set_value"):
            self.card_above20.set_value(f"{above20:.1f}%")

        if hasattr(self.card_above50, "set_value"):
            self.card_above50.set_value(f"{above50:.1f}%")

        if hasattr(self.card_above200, "set_value"):
            self.card_above200.set_value(f"{above200:.1f}%")

    # --------------------------------------------------
    # FII / DII
    # --------------------------------------------------

    def update_fii_dii(self, snapshot):

        fii = snapshot.get("institutional", {})

        fii_cash = fii.get("fii_cash", 0)
        dii_cash = fii.get("dii_cash", 0)

        block = fii.get("block_deals", 0)
        bulk = fii.get("bulk_deals", 0)

        if hasattr(self.card_fii, "set_value"):
            self.card_fii.set_value(f"â‚¹{fii_cash:,.0f} Cr")

        if hasattr(self.card_dii, "set_value"):
            self.card_dii.set_value(f"â‚¹{dii_cash:,.0f} Cr")

        if hasattr(self.card_block, "set_value"):
            self.card_block.set_value(str(block))

        if hasattr(self.card_bulk, "set_value"):
            self.card_bulk.set_value(str(bulk))

        #
        # Subtitle
        #

        if hasattr(self.card_fii, "set_subtitle"):
            self.card_fii.set_subtitle(
                "Buying" if fii_cash >= 0 else "Selling"
            )

        if hasattr(self.card_dii, "set_subtitle"):
            self.card_dii.set_subtitle(
                "Buying" if dii_cash >= 0 else "Selling"
            )

    # --------------------------------------------------
    # OPTIONS ANALYTICS
    # --------------------------------------------------

    def update_options(self, snapshot):

        option = snapshot.get("options", {})

        pcr = option.get("pcr", 1.0)

        maxpain = option.get("max_pain", "--")

        calloi = option.get("highest_call_oi", "--")

        putoi = option.get("highest_put_oi", "--")

        if hasattr(self.card_pcr, "set_value"):
            self.card_pcr.set_value(f"{pcr:.2f}")

        if hasattr(self.card_maxpain, "set_value"):
            self.card_maxpain.set_value(str(maxpain))

        if hasattr(self.card_calloi, "set_value"):
            self.card_calloi.set_value(str(calloi))

        if hasattr(self.card_putoi, "set_value"):
            self.card_putoi.set_value(str(putoi))

        #
        # PCR Meaning
        #

        if hasattr(self.card_pcr, "set_subtitle"):

            if pcr >= 1.30:
                text = "Bullish"

            elif pcr >= 0.90:
                text = "Neutral"

            else:
                text = "Bearish"

            self.card_pcr.set_subtitle(text)

    # --------------------------------------------------
    # UPDATE COMPLETE DASHBOARD
    # --------------------------------------------------

    def update_dashboard_sections(self, snapshot):

        self.update_market_breadth(snapshot)

        self.update_fii_dii(snapshot)

        self.update_options(snapshot)
            # --------------------------------------------------
    # SECTOR HEATMAP
    # --------------------------------------------------

    def update_sector_heatmap(self, snapshot):

        sectors = snapshot.get("sectors", {})

        for sector_name, card in self.sector_cards.items():

            data = sectors.get(sector_name.lower(), {})

            change = float(data.get("change", 0))
            strength = data.get("strength", "Neutral")

            if hasattr(card, "set_value"):
                card.set_value(f"{change:+.2f}%")

            if hasattr(card, "set_subtitle"):
                card.set_subtitle(str(strength))

            #
            # Professional Colour Theme
            #

            if change >= 1.50:
                colour = "#00C853"          # Strong Green

            elif change >= 0:
                colour = "#66BB6A"          # Light Green

            elif change <= -1.50:
                colour = "#D50000"          # Strong Red

            else:
                colour = "#EF5350"          # Light Red

            try:

                card.setStyleSheet(f"""
                QFrame {{
                    border:1px solid #404040;
                    border-radius:10px;
                    background:#1b1b1b;
                }}

                QLabel#value {{
                    color:{colour};
                    font-size:22px;
                    font-weight:bold;
                }}
                """)

            except Exception:
                pass

    # --------------------------------------------------
    # AI TOP TRADES
    # --------------------------------------------------

    def update_ai_trades(self, snapshot):

        trades = snapshot.get("ai_trades", [])

        self.ai_table.setRowCount(len(trades))

        for row, trade in enumerate(trades):

            values = [

                trade.get("symbol", ""),

                trade.get("strategy", ""),

                f'{trade.get("score",0):.0f}',

                str(trade.get("entry","")),

                str(trade.get("sl","")),

                str(trade.get("target",""))

            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignCenter)

                self.ai_table.setItem(row, col, item)

            #
            # AI Score Colour
            #

            score = float(trade.get("score", 0))

            score_item = self.ai_table.item(row, 2)

            if score_item:

                if score >= 90:
                    score_item.setForeground(QColor("#00E676"))

                elif score >= 75:
                    score_item.setForeground(QColor("#7CFC00"))

                elif score >= 60:
                    score_item.setForeground(QColor("#FFD54F"))

                else:
                    score_item.setForeground(QColor("#EF5350"))

    # --------------------------------------------------
    # LIVE AI ALERTS
    # --------------------------------------------------

    def update_alerts(self, snapshot):

        alerts = snapshot.get("alerts", [])

        self.alerts_table.setRowCount(len(alerts))

        for row, alert in enumerate(alerts):

            values = [

                alert.get("time", ""),

                alert.get("symbol", ""),

                alert.get("type", ""),

                str(alert.get("score", "")),

                alert.get("action", "")

            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(Qt.AlignCenter)

                self.alerts_table.setItem(row, col, item)

            #
            # Row Colours
            #

            action = alert.get("action", "").upper()

            if action == "BUY":

                colour = QColor("#00E676")

            elif action == "SELL":

                colour = QColor("#FF5252")

            elif action == "BREAKOUT":

                colour = QColor("#29B6F6")

            elif action == "BREAKDOWN":

                colour = QColor("#FF7043")

            else:

                colour = QColor("#FFD54F")

            for c in range(self.alerts_table.columnCount()):

                item = self.alerts_table.item(row, c)

                if item:
                    item.setForeground(colour)

    # --------------------------------------------------
    # UPDATE ALL TABLES
    # --------------------------------------------------

    def update_tables(self, snapshot):

        self.update_sector_heatmap(snapshot)

        self.update_ai_trades(snapshot)

        self.update_alerts(snapshot)
            # --------------------------------------------------
    # MARKET MOVERS
    # --------------------------------------------------

    def update_market_movers(self, snapshot):

        movers = snapshot.get("market_movers", {})

        #
        # Default View = Top Gainers
        #

        data = movers.get("gainers", [])

        self.load_market_table(data)

    # --------------------------------------------------

    def show_top_gainers(self):

        if not hasattr(self, "_snapshot"):
            return

        data = self._snapshot.get(
            "market_movers",
            {}
        ).get("gainers", [])

        self.load_market_table(data)

    # --------------------------------------------------

    def show_top_losers(self):

        if not hasattr(self, "_snapshot"):
            return

        data = self._snapshot.get(
            "market_movers",
            {}
        ).get("losers", [])

        self.load_market_table(data)

    # --------------------------------------------------

    def show_volume_shockers(self):

        if not hasattr(self, "_snapshot"):
            return

        data = self._snapshot.get(
            "market_movers",
            {}
        ).get("volume_shockers", [])

        self.load_market_table(data)

    # --------------------------------------------------

    def show_delivery_shockers(self):

        if not hasattr(self, "_snapshot"):
            return

        data = self._snapshot.get(
            "market_movers",
            {}
        ).get("delivery_shockers", [])

        self.load_market_table(data)

    # --------------------------------------------------

    def load_market_table(self, stocks):

        self.movers_table.setSortingEnabled(False)

        self.movers_table.setRowCount(len(stocks))

        for row, stock in enumerate(stocks):

            symbol = stock.get("symbol", "")

            price = stock.get("price", 0)

            change = stock.get("change_percent", 0)

            volume = stock.get("volume", 0)

            signal = stock.get("signal", "")

            values = [

                symbol,

                f"{price:.2f}",

                f"{change:+.2f}%",

                f"{volume:,}",

                signal

            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                item.setTextAlignment(Qt.AlignCenter)

                self.movers_table.setItem(
                    row,
                    col,
                    item
                )

            #
            # Price Colour
            #

            colour = QColor("#00E676") \
                if change >= 0 \
                else QColor("#FF5252")

            for c in range(
                self.movers_table.columnCount()
            ):

                item = self.movers_table.item(
                    row,
                    c
                )

                if item:

                    item.setForeground(colour)

        self.movers_table.setSortingEnabled(True)

    # --------------------------------------------------
    # DOUBLE CLICK
    # --------------------------------------------------

    def open_selected_stock(self, item):

        row = item.row()

        symbol_item = self.movers_table.item(row, 0)

        if symbol_item is None:
            return

        symbol = symbol_item.text()

        #
        # Controller Hook
        #

        if self.controller:

            if hasattr(
                self.controller,
                "open_stock_chart"
            ):

                self.controller.open_stock_chart(
                    symbol
                )

    # --------------------------------------------------
    # SNAPSHOT
    # --------------------------------------------------

    def process_snapshot(self, snapshot):

        self._snapshot = snapshot

        self.update_market_cards(snapshot)

        self.update_sentiment(snapshot)

        self.update_dashboard_sections(snapshot)

        self.update_tables(snapshot)

        self.update_market_movers(snapshot)

        self.last_update.setText(

            "Updated : "

            + datetime.now().strftime(

                "%d %b %Y  %I:%M:%S %p"

            )

        )
            # --------------------------------------------------
    # SIGNALS
    # --------------------------------------------------

    def connect_signals(self):

        #
        # Double Click on Market Movers
        #

        self.movers_table.itemDoubleClicked.connect(
            self.open_selected_stock
        )

        #
        # Double Click on AI Trades
        #

        self.ai_table.itemDoubleClicked.connect(
            self.open_ai_trade
        )

        #
        # Double Click on Alerts
        #

        self.alerts_table.itemDoubleClicked.connect(
            self.open_alert_stock
        )

    # --------------------------------------------------
    # AUTO REFRESH
    # --------------------------------------------------

    def start_auto_refresh(self):

        if self.timer.isActive():
            self.timer.stop()

        #
        # Refresh every 60 seconds
        #

        self.timer.start(60000)

    # --------------------------------------------------

    def stop_auto_refresh(self):

        if self.timer.isActive():

            self.timer.stop()

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    def load_dashboard(self):

        self.refresh_dashboard()

    # --------------------------------------------------
    # REFRESH
    # --------------------------------------------------

    def refresh_dashboard(self):

        try:

            if self.controller is None:
                return

            #
            # Professional Loader
            #

            self.setEnabled(False)

            snapshot = self.controller.get_market_snapshot()

            if snapshot:

                self.process_snapshot(snapshot)

        except Exception as e:

            print(
                "Market Dashboard Error :",
                e
            )

        finally:

            self.setEnabled(True)

    # --------------------------------------------------
    # OPEN AI TRADE
    # --------------------------------------------------

    def open_ai_trade(self, item):

        row = item.row()

        symbol_item = self.ai_table.item(row, 0)

        if symbol_item is None:
            return

        symbol = symbol_item.text()

        if self.controller:

            if hasattr(
                self.controller,
                "open_stock_chart"
            ):

                self.controller.open_stock_chart(
                    symbol
                )

    # --------------------------------------------------
    # OPEN ALERT STOCK
    # --------------------------------------------------

    def open_alert_stock(self, item):

        row = item.row()

        symbol_item = self.alerts_table.item(row, 1)

        if symbol_item is None:
            return

        symbol = symbol_item.text()

        if self.controller:

            if hasattr(
                self.controller,
                "open_stock_chart"
            ):

                self.controller.open_stock_chart(
                    symbol
                )

    # --------------------------------------------------
    # CLEAR TABLES
    # --------------------------------------------------

    def clear_tables(self):

        self.ai_table.setRowCount(0)

        self.movers_table.setRowCount(0)

        self.alerts_table.setRowCount(0)

    # --------------------------------------------------
    # RESET DASHBOARD
    # --------------------------------------------------

    def reset_dashboard(self):

        self.clear_tables()

        self.sentiment_score.setText("--")

        self.sentiment_status.setText("Waiting...")

        self.last_update.setText("")

        for card in [

            self.card_nifty,
            self.card_bank,
            self.card_gold,
            self.card_usd,
            self.card_brent,
            self.card_vix

        ]:

            if hasattr(card, "set_value"):
                card.set_value("--")

            if hasattr(card, "set_subtitle"):
                card.set_subtitle("Waiting...")

    # --------------------------------------------------
    # SHOW EVENT
    # --------------------------------------------------

    def showEvent(self, event):

        super().showEvent(event)

        self.start_auto_refresh()

        self.refresh_dashboard()

    # --------------------------------------------------
    # HIDE EVENT
    # --------------------------------------------------

    def hideEvent(self, event):

        super().hideEvent(event)

        self.stop_auto_refresh()
            # --------------------------------------------------
    # CLOSE EVENT
    # --------------------------------------------------

    def closeEvent(self, event):

        try:
            self.shutdown()

        finally:
            super().closeEvent(event)

    # --------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------

    def shutdown(self):

        #
        # Stop Timer
        #

        if hasattr(self, "timer"):

            if self.timer.isActive():

                self.timer.stop()

        #
        # Clear Tables
        #

        self.clear_tables()

        #
        # Clear Pie Chart
        #

        if hasattr(self, "sentiment_chart"):

            chart = self.sentiment_chart.chart()

            if chart is not None:

                chart.removeAllSeries()

        #
        # Disconnect Signals
        #

        try:
            self.movers_table.itemDoubleClicked.disconnect()
        except Exception:
            pass

        try:
            self.ai_table.itemDoubleClicked.disconnect()
        except Exception:
            pass

        try:
            self.alerts_table.itemDoubleClicked.disconnect()
        except Exception:
            pass

    # --------------------------------------------------
    # EXPORT DASHBOARD DATA
    # --------------------------------------------------

    def export_dashboard(self):

        if self.controller is None:
            return None

        if hasattr(self.controller, "export_market_dashboard"):

            return self.controller.export_market_dashboard()

        return None

    # --------------------------------------------------
    # REFRESH NOW
    # --------------------------------------------------

    def refresh_now(self):

        self.refresh_dashboard()

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def dashboard_status(self):

        return {

            "last_update": self.last_update.text(),

            "ai_score": self.sentiment_score.text(),

            "market_status": self.sentiment_status.text(),

            "auto_refresh": self.timer.isActive()

        }

    # --------------------------------------------------
    # REPR
    # --------------------------------------------------

    def __repr__(self):

        return (

            "<MarketDashboardPage "

            f"updated='{self.last_update.text()}'>"

        )

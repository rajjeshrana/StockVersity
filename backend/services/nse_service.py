"""
=========================================================
StockVersity Scanner Pro

NSE Service

Provides live NSE market data, indices,
gainers/losers, sector data and market statistics.
=========================================================
"""

from __future__ import annotations

import logging
import time
from datetime import datetime

import pandas as pd
import requests


class NseService:

    BASE_URL = "https://www.nseindia.com"

    API = "https://www.nseindia.com/api"

    HEADERS = {

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),

        "Accept":

            "application/json",

        "Accept-Language":

            "en-US,en;q=0.9",

        "Referer":

            "https://www.nseindia.com",

    }

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self):

        self.logger = logging.getLogger(__name__)

        self.session = requests.Session()

        self.session.headers.update(

            self.HEADERS

        )

        self.cookie_time = 0

        self.cookie_expiry = 300

        self.refresh_session()

    # =====================================================
    # SESSION
    # =====================================================

    def refresh_session(self):

        try:

            self.session.get(

                self.BASE_URL,

                timeout=10,

            )

            self.cookie_time = time.time()

        except Exception as e:

            self.logger.warning(e)

    # =====================================================
    # COOKIE CHECK
    # =====================================================

    def ensure_session(self):

        if (

            time.time()

            - self.cookie_time

            >

            self.cookie_expiry

        ):

            self.refresh_session()

    # =====================================================
    # GET JSON
    # =====================================================

    def get_json(

        self,

        endpoint,

        params=None,

    ):

        self.ensure_session()

        url = (

            self.API

            + endpoint

        )

        response = self.session.get(

            url,

            params=params,

            timeout=15,

        )

        if response.status_code == 401:

            self.refresh_session()

            response = self.session.get(

                url,

                params=params,

                timeout=15,

            )

        response.raise_for_status()

        return response.json()

    # =====================================================
    # MARKET STATUS
    # =====================================================

    def market_status(self):

        try:

            data = self.get_json(

                "/marketStatus"

            )

            return data

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # HOLIDAY LIST
    # =====================================================

    def holidays(self):

        try:

            return self.get_json(

                "/holiday-master"

            )

        except Exception:

            return {}

    # =====================================================
    # SERVER TIME
    # =====================================================

    def server_time(self):

        return datetime.now()

    # =====================================================
    # CONNECTION TEST
    # =====================================================

    def connection_status(self):

        try:

            self.market_status()

            return True

        except Exception:

            return False

    # =====================================================
    # INDEX LIST
    # =====================================================

    def available_indices(self):

        return [

            "NIFTY 50",

            "NIFTY NEXT 50",

            "NIFTY MIDCAP 100",

            "NIFTY SMALLCAP 100",

            "NIFTY BANK",

            "NIFTY FIN SERVICE",

            "NIFTY IT",

            "NIFTY AUTO",

            "NIFTY FMCG",

            "NIFTY PHARMA",

            "NIFTY METAL",

            "NIFTY REALTY",

            "NIFTY PSU BANK",

        ]
        # =====================================================
    # INDEX QUOTE
    # =====================================================

    def index_quote(
        self,
        index_name="NIFTY 50",
    ):

        try:

            data = self.get_json(
                "/equity-stockIndices",
                params={
                    "index": index_name,
                },
            )

            return data

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # INDEX SUMMARY
    # =====================================================

    def index_summary(
        self,
        index_name="NIFTY 50",
    ):

        data = self.index_quote(index_name)

        if not data:

            return {}

        summary = data.get("marketStatus", {})

        return {

            "index": index_name,

            "last": summary.get("last"),

            "change": summary.get("change"),

            "percent_change": summary.get("percentChange"),

            "open": summary.get("open"),

            "high": summary.get("high"),

            "low": summary.get("low"),

            "previous_close": summary.get("previousClose"),

        }

    # =====================================================
    # NIFTY
    # =====================================================

    def nifty(self):

        return self.index_summary(

            "NIFTY 50"

        )

    # =====================================================
    # BANKNIFTY
    # =====================================================

    def banknifty(self):

        return self.index_summary(

            "NIFTY BANK"

        )

    # =====================================================
    # FINNIFTY
    # =====================================================

    def finnifty(self):

        return self.index_summary(

            "NIFTY FIN SERVICE"

        )

    # =====================================================
    # MIDCAP
    # =====================================================

    def midcap(self):

        return self.index_summary(

            "NIFTY MIDCAP 100"

        )

    # =====================================================
    # SMALLCAP
    # =====================================================

    def smallcap(self):

        return self.index_summary(

            "NIFTY SMALLCAP 100"

        )

    # =====================================================
    # IT INDEX
    # =====================================================

    def it_index(self):

        return self.index_summary(

            "NIFTY IT"

        )

    # =====================================================
    # AUTO INDEX
    # =====================================================

    def auto_index(self):

        return self.index_summary(

            "NIFTY AUTO"

        )

    # =====================================================
    # PHARMA INDEX
    # =====================================================

    def pharma_index(self):

        return self.index_summary(

            "NIFTY PHARMA"

        )

    # =====================================================
    # FMCG INDEX
    # =====================================================

    def fmcg_index(self):

        return self.index_summary(

            "NIFTY FMCG"

        )

    # =====================================================
    # METAL INDEX
    # =====================================================

    def metal_index(self):

        return self.index_summary(

            "NIFTY METAL"

        )

    # =====================================================
    # REALTY INDEX
    # =====================================================

    def realty_index(self):

        return self.index_summary(

            "NIFTY REALTY"

        )

    # =====================================================
    # PSU BANK INDEX
    # =====================================================

    def psu_bank_index(self):

        return self.index_summary(

            "NIFTY PSU BANK"

        )

    # =====================================================
    # MARKET BREADTH
    # =====================================================

    def market_breadth(self):

        try:

            data = self.index_quote("NIFTY 50")

            stocks = data.get(

                "data",

                [],

            )

            advances = 0

            declines = 0

            unchanged = 0

            total = len(stocks)

            for stock in stocks:

                change = stock.get(

                    "pChange",

                    0,

                )

                if change > 0:

                    advances += 1

                elif change < 0:

                    declines += 1

                else:

                    unchanged += 1

            return {

                "advances": advances,

                "declines": declines,

                "unchanged": unchanged,

                "total": total,

                "advance_decline_ratio":

                    round(

                        advances /

                        max(declines, 1),

                        2,

                    ),

            }

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def market_snapshot(self):

        return {

            "nifty": self.nifty(),

            "banknifty": self.banknifty(),

            "finnifty": self.finnifty(),

            "midcap": self.midcap(),

            "smallcap": self.smallcap(),

            "breadth": self.market_breadth(),

        }
        # =====================================================
    # TOP GAINERS
    # =====================================================

    def top_gainers(self):

        try:

            data = self.get_json(

                "/live-analysis-variations",

                params={

                    "index": "gainers",

                },

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # TOP LOSERS
    # =====================================================

    def top_losers(self):

        try:

            data = self.get_json(

                "/live-analysis-variations",

                params={

                    "index": "losers",

                },

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # MOST ACTIVE BY VOLUME
    # =====================================================

    def most_active_volume(self):

        try:

            data = self.get_json(

                "/live-analysis-most-active-securities",

                params={

                    "index": "volume",

                },

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # MOST ACTIVE BY VALUE
    # =====================================================

    def most_active_value(self):

        try:

            data = self.get_json(

                "/live-analysis-most-active-securities",

                params={

                    "index": "value",

                },

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # VOLUME SHOCKERS
    # =====================================================

    def volume_shockers(self):

        try:

            data = self.get_json(

                "/live-analysis-volume-gainers"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # DELIVERY SHOCKERS
    # =====================================================

    def delivery_shockers(self):

        try:

            data = self.get_json(

                "/live-analysis-delivery-position"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # 52 WEEK HIGH
    # =====================================================

    def week52_high(self):

        try:

            data = self.get_json(

                "/live-analysis-52WeekHigh"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # 52 WEEK LOW
    # =====================================================

    def week52_low(self):

        try:

            data = self.get_json(

                "/live-analysis-52WeekLow"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # UPPER CIRCUIT
    # =====================================================

    def upper_circuit(self):

        try:

            data = self.get_json(

                "/live-analysis-upper-circuit"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # LOWER CIRCUIT
    # =====================================================

    def lower_circuit(self):

        try:

            data = self.get_json(

                "/live-analysis-lower-circuit"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # F&O SECURITIES
    # =====================================================

    def fno_securities(self):

        try:

            data = self.get_json(

                "/foSecStockWatch"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # LIVE MARKET MOVERS
    # =====================================================

    def market_movers(self):

        return {

            "gainers": self.top_gainers(),

            "losers": self.top_losers(),

            "most_active_volume": self.most_active_volume(),

            "most_active_value": self.most_active_value(),

            "volume_shockers": self.volume_shockers(),

            "delivery_shockers": self.delivery_shockers(),

            "week52_high": self.week52_high(),

            "week52_low": self.week52_low(),

            "upper_circuit": self.upper_circuit(),

            "lower_circuit": self.lower_circuit(),

            "fno": self.fno_securities(),

        }

    # =====================================================
    # MOVERS DATAFRAME
    # =====================================================

    def movers_dataframe(

        self,

        mover_type="gainers",

    ):

        mapping = {

            "gainers": self.top_gainers,

            "losers": self.top_losers,

            "volume": self.most_active_volume,

            "value": self.most_active_value,

            "high52": self.week52_high,

            "low52": self.week52_low,

        }

        if mover_type not in mapping:

            return pd.DataFrame()

        data = mapping[mover_type]()

        return pd.DataFrame(data)
        # =====================================================
    # STOCK QUOTE
    # =====================================================

    def quote(
        self,
        symbol,
    ):

        try:

            return self.get_json(

                "/quote-equity",

                params={

                    "symbol": symbol.upper(),

                },

            )

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # QUOTE SUMMARY
    # =====================================================

    def quote_summary(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        info = data.get("priceInfo", {})

        security = data.get("securityInfo", {})

        metadata = data.get("metadata", {})

        return {

            "symbol": symbol.upper(),

            "company": metadata.get("companyName"),

            "industry": metadata.get("industry"),

            "series": security.get("series"),

            "isin": security.get("isin"),

            "face_value": security.get("faceValue"),

            "last_price": info.get("lastPrice"),

            "previous_close": info.get("previousClose"),

            "open": info.get("open"),

            "high": info.get("intraDayHighLow", {}).get("max"),

            "low": info.get("intraDayHighLow", {}).get("min"),

            "change": info.get("change"),

            "percent_change": info.get("pChange"),

            "volume": info.get("totalTradedVolume"),

            "value": info.get("totalTradedValue"),

        }

    # =====================================================
    # OHLC
    # =====================================================

    def ohlc(
        self,
        symbol,
    ):

        summary = self.quote_summary(symbol)

        return {

            "open": summary.get("open"),

            "high": summary.get("high"),

            "low": summary.get("low"),

            "close": summary.get("last_price"),

        }

    # =====================================================
    # PRICE INFO
    # =====================================================

    def price_info(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "priceInfo",

            {},

        )

    # =====================================================
    # COMPANY INFO
    # =====================================================

    def company_info(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "metadata",

            {},

        )

    # =====================================================
    # SECURITY INFO
    # =====================================================

    def security_info(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "securityInfo",

            {},

        )

    # =====================================================
    # INDUSTRY
    # =====================================================

    def industry(
        self,
        symbol,
    ):

        return self.company_info(

            symbol

        ).get(

            "industry"

        )

    # =====================================================
    # DELIVERY DATA
    # =====================================================

    def delivery_data(
        self,
        symbol,
    ):

        try:

            data = self.get_json(

                "/quote-equity",

                params={

                    "symbol": symbol.upper(),

                    "section": "trade_info",

                },

            )

            return data.get(

                "securityWiseDP",

                {},

            )

        except Exception:

            return {}

    # =====================================================
    # DELIVERY PERCENTAGE
    # =====================================================

    def delivery_percentage(
        self,
        symbol,
    ):

        delivery = self.delivery_data(symbol)

        return delivery.get(

            "deliveryToTradedQuantity",

            None,

        )

    # =====================================================
    # CORPORATE ACTIONS
    # =====================================================

    def corporate_actions(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "corporateActions",

            [],

        )

    # =====================================================
    # SHAREHOLDING
    # =====================================================

    def shareholding_pattern(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "shareholdingPattern",

            [],

        )

    # =====================================================
    # FINANCIAL RATIOS
    # =====================================================

    def financial_ratios(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "financialResults",

            {},

        )

    # =====================================================
    # BOARD MEETINGS
    # =====================================================

    def board_meetings(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "boardMeetings",

            [],

        )

    # =====================================================
    # ANNOUNCEMENTS
    # =====================================================

    def announcements(
        self,
        symbol,
    ):

        data = self.quote(symbol)

        return data.get(

            "announcements",

            [],

        )

    # =====================================================
    # COMPLETE STOCK PROFILE
    # =====================================================

    def stock_profile(
        self,
        symbol,
    ):

        return {

            "summary": self.quote_summary(symbol),

            "company": self.company_info(symbol),

            "security": self.security_info(symbol),

            "delivery": self.delivery_data(symbol),

            "corporate_actions": self.corporate_actions(symbol),

            "shareholding": self.shareholding_pattern(symbol),

            "financials": self.financial_ratios(symbol),

            "board_meetings": self.board_meetings(symbol),

            "announcements": self.announcements(symbol),

        }
        # =====================================================
    # HISTORICAL DATA
    # =====================================================

    def historical_data(
        self,
        symbol,
    ):

        try:

            data = self.get_json(

                "/historical/cm/equity",

                params={

                    "symbol": symbol.upper(),

                },

            )

            records = data.get(

                "data",

                [],

            )

            if not records:

                return pd.DataFrame()

            df = pd.DataFrame(records)

            return df

        except Exception as e:

            self.logger.exception(e)

            return pd.DataFrame()

    # =====================================================
    # INTRADAY DATA
    # =====================================================

    def intraday_data(
        self,
        symbol,
    ):

        try:

            data = self.get_json(

                "/chart-databyindex",

                params={

                    "index": symbol.upper(),

                },

            )

            return data

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # OPTION CHAIN
    # =====================================================

    def option_chain(
        self,
        symbol,
    ):

        try:

            return self.get_json(

                "/option-chain-equities",

                params={

                    "symbol": symbol.upper(),

                },

            )

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # INDEX OPTION CHAIN
    # =====================================================

    def index_option_chain(
        self,
        index_name="NIFTY",
    ):

        try:

            return self.get_json(

                "/option-chain-indices",

                params={

                    "symbol": index_name,

                },

            )

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # FUTURES DATA
    # =====================================================

    def futures_data(
        self,
        symbol,
    ):

        try:

            data = self.get_json(

                "/quote-derivative",

                params={

                    "symbol": symbol.upper(),

                },

            )

            return data

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # OPEN INTEREST
    # =====================================================

    def open_interest(
        self,
        symbol,
    ):

        data = self.futures_data(

            symbol

        )

        return data.get(

            "stocks",

            [],

        )

    # =====================================================
    # PUT CALL RATIO
    # =====================================================

    def put_call_ratio(
        self,
        symbol="NIFTY",
    ):

        chain = self.index_option_chain(

            symbol

        )

        records = chain.get(

            "records",

            {},

        ).get(

            "data",

            [],

        )

        total_ce_oi = 0

        total_pe_oi = 0

        for row in records:

            ce = row.get(

                "CE"

            )

            pe = row.get(

                "PE"

            )

            if ce:

                total_ce_oi += ce.get(

                    "openInterest",

                    0,

                )

            if pe:

                total_pe_oi += pe.get(

                    "openInterest",

                    0,

                )

        if total_ce_oi == 0:

            return None

        return round(

            total_pe_oi

            / total_ce_oi,

            2,

        )

    # =====================================================
    # MAX PAIN
    # =====================================================

    def max_pain(
        self,
        symbol="NIFTY",
    ):

        chain = self.index_option_chain(

            symbol

        )

        records = chain.get(

            "records",

            {},

        ).get(

            "data",

            [],

        )

        if not records:

            return None

        pain = {}

        for row in records:

            strike = row.get(

                "strikePrice"

            )

            ce = row.get(

                "CE",

                {},

            )

            pe = row.get(

                "PE",

                {},

            )

            pain[strike] = (

                ce.get(

                    "openInterest",

                    0,

                )

                +

                pe.get(

                    "openInterest",

                    0,

                )

            )

        return min(

            pain,

            key=pain.get,

        )

    # =====================================================
    # HIGHEST OI STRIKES
    # =====================================================

    def highest_oi(
        self,
        symbol="NIFTY",
        top=5,
    ):

        chain = self.index_option_chain(

            symbol

        )

        rows = chain.get(

            "records",

            {},

        ).get(

            "data",

            [],

        )

        strikes = []

        for row in rows:

            ce = row.get(

                "CE"

            )

            pe = row.get(

                "PE"

            )

            if ce:

                strikes.append(

                    (

                        row["strikePrice"],

                        ce.get(

                            "openInterest",

                            0,

                        ),

                        "CE",

                    )

                )

            if pe:

                strikes.append(

                    (

                        row["strikePrice"],

                        pe.get(

                            "openInterest",

                            0,

                        ),

                        "PE",

                    )

                )

        strikes.sort(

            key=lambda x: x[1],

            reverse=True,

        )

        return strikes[:top]

    # =====================================================
    # DERIVATIVES SUMMARY
    # =====================================================

    def derivatives_summary(
        self,
        symbol="NIFTY",
    ):

        return {

            "pcr": self.put_call_ratio(

                symbol

            ),

            "max_pain": self.max_pain(

                symbol

            ),

            "highest_oi": self.highest_oi(

                symbol

            ),

        }
        # =====================================================
    # FII / DII ACTIVITY
    # =====================================================

    def fii_dii_activity(self):

        try:

            data = self.get_json(

                "/fiidiiTradeReact"

            )

            return data

        except Exception as e:

            self.logger.exception(e)

            return {}

    # =====================================================
    # FII SUMMARY
    # =====================================================

    def fii_summary(self):

        activity = self.fii_dii_activity()

        return activity.get(

            "FII",

            {},

        )

    # =====================================================
    # DII SUMMARY
    # =====================================================

    def dii_summary(self):

        activity = self.fii_dii_activity()

        return activity.get(

            "DII",

            {},

        )

    # =====================================================
    # BLOCK DEALS
    # =====================================================

    def block_deals(self):

        try:

            data = self.get_json(

                "/block-deal"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # BULK DEALS
    # =====================================================

    def bulk_deals(self):

        try:

            data = self.get_json(

                "/bulk-deal"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # INSIDER TRADING
    # =====================================================

    def insider_trading(self):

        try:

            data = self.get_json(

                "/corporates-pit"

            )

            return data.get(

                "data",

                [],

            )

        except Exception as e:

            self.logger.exception(e)

            return []

    # =====================================================
    # SHARE PLEDGE
    # =====================================================

    def share_pledge(

        self,

        symbol,

    ):

        try:

            quote = self.quote(

                symbol

            )

            return quote.get(

                "shareholdingPattern",

                [],

            )

        except Exception:

            return []

    # =====================================================
    # INSTITUTIONAL HOLDINGS
    # =====================================================

    def institutional_holdings(

        self,

        symbol,

    ):

        pattern = self.shareholding_pattern(

            symbol

        )

        result = []

        for row in pattern:

            holder = str(

                row.get(

                    "category",

                    "",

                )

            ).lower()

            if (

                "institution"

                in holder

                or

                "mutual"

                in holder

                or

                "foreign"

                in holder

            ):

                result.append(

                    row

                )

        return result

    # =====================================================
    # MUTUAL FUND HOLDINGS
    # =====================================================

    def mutual_fund_holdings(

        self,

        symbol,

    ):

        holdings = self.institutional_holdings(

            symbol

        )

        return [

            item

            for item in holdings

            if "mutual"

            in str(

                item.get(

                    "category",

                    "",

                )

            ).lower()

        ]

    # =====================================================
    # FOREIGN HOLDINGS
    # =====================================================

    def fii_holdings(

        self,

        symbol,

    ):

        holdings = self.institutional_holdings(

            symbol

        )

        return [

            item

            for item in holdings

            if (

                "foreign"

                in str(

                    item.get(

                        "category",

                        "",

                    )

                ).lower()

            )

        ]

    # =====================================================
    # PROMOTER HOLDINGS
    # =====================================================

    def promoter_holdings(

        self,

        symbol,

    ):

        pattern = self.shareholding_pattern(

            symbol

        )

        return [

            item

            for item in pattern

            if (

                "promoter"

                in str(

                    item.get(

                        "category",

                        "",

                    )

                ).lower()

            )

        ]

    # =====================================================
    # INSTITUTIONAL SCORE
    # =====================================================

    def institutional_score(

        self,

        symbol,

    ):

        score = 0

        if self.fii_holdings(symbol):

            score += 30

        if self.mutual_fund_holdings(symbol):

            score += 25

        if self.promoter_holdings(symbol):

            score += 20

        if self.bulk_deals():

            score += 15

        if self.block_deals():

            score += 10

        return min(

            score,

            100,

        )

    # =====================================================
    # SMART MONEY SUMMARY
    # =====================================================

    def smart_money_summary(

        self,

        symbol,

    ):

        return {

            "institutional_score":

                self.institutional_score(

                    symbol

                ),

            "fii_holdings":

                self.fii_holdings(

                    symbol

                ),

            "mutual_funds":

                self.mutual_fund_holdings(

                    symbol

                ),

            "promoters":

                self.promoter_holdings(

                    symbol

                ),

            "block_deals":

                self.block_deals(),

            "bulk_deals":

                self.bulk_deals(),

            "insider":

                self.insider_trading(),

        }
        # =====================================================
    # SECTOR PERFORMANCE
    # =====================================================

    def sector_performance(self):

        sectors = []

        for index_name in self.available_indices():

            try:

                summary = self.index_summary(

                    index_name

                )

                sectors.append(

                    {

                        "sector": index_name,

                        "change": float(

                            summary.get(

                                "percent_change",

                                0,

                            )

                            or 0

                        ),

                        "last": summary.get(

                            "last"

                        ),

                    }

                )

            except Exception:

                continue

        sectors.sort(

            key=lambda x: x["change"],

            reverse=True,

        )

        return sectors

    # =====================================================
    # TOP SECTORS
    # =====================================================

    def top_sectors(

        self,

        limit=5,

    ):

        return self.sector_performance()[:limit]

    # =====================================================
    # WORST SECTORS
    # =====================================================

    def worst_sectors(

        self,

        limit=5,

    ):

        sectors = self.sector_performance()

        sectors.sort(

            key=lambda x: x["change"]

        )

        return sectors[:limit]

    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    def sector_strength(

        self,

        sector_name,

    ):

        for sector in self.sector_performance():

            if (

                sector["sector"].upper()

                ==

                sector_name.upper()

            ):

                return sector["change"]

        return 0

    # =====================================================
    # AI SECTOR SCORE
    # =====================================================

    def sector_ai_score(

        self,

        sector_name,

    ):

        strength = self.sector_strength(

            sector_name

        )

        if strength >= 3:

            return 100

        if strength >= 2:

            return 90

        if strength >= 1:

            return 80

        if strength >= 0:

            return 65

        if strength >= -1:

            return 45

        return 25

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    def relative_strength(

        self,

        stock_change,

        sector_change,

    ):

        return round(

            stock_change

            -

            sector_change,

            2,

        )

    # =====================================================
    # ADVANCE DECLINE BY SECTOR
    # =====================================================

    def sector_breadth(

        self,

        sector_name,

    ):

        try:

            data = self.index_quote(

                sector_name

            )

            stocks = data.get(

                "data",

                [],

            )

            advances = 0

            declines = 0

            unchanged = 0

            for stock in stocks:

                change = float(

                    stock.get(

                        "pChange",

                        0,

                    )

                )

                if change > 0:

                    advances += 1

                elif change < 0:

                    declines += 1

                else:

                    unchanged += 1

            return {

                "advances": advances,

                "declines": declines,

                "unchanged": unchanged,

            }

        except Exception:

            return {}

    # =====================================================
    # SECTOR ROTATION
    # =====================================================

    def sector_rotation(self):

        performance = self.sector_performance()

        leaders = []

        laggards = []

        for sector in performance:

            if sector["change"] > 1:

                leaders.append(

                    sector["sector"]

                )

            elif sector["change"] < -1:

                laggards.append(

                    sector["sector"]

                )

        return {

            "leaders": leaders,

            "laggards": laggards,

        }

    # =====================================================
    # HEATMAP DATA
    # =====================================================

    def heatmap(self):

        heatmap = []

        for sector in self.sector_performance():

            score = self.sector_ai_score(

                sector["sector"]

            )

            heatmap.append(

                {

                    "sector":

                        sector["sector"],

                    "performance":

                        sector["change"],

                    "score":

                        score,

                }

            )

        return heatmap

    # =====================================================
    # INDUSTRY RANKING
    # =====================================================

    def industry_ranking(self):

        ranking = []

        for sector in self.sector_performance():

            ranking.append(

                {

                    "industry":

                        sector["sector"],

                    "performance":

                        sector["change"],

                    "ai_score":

                        self.sector_ai_score(

                            sector["sector"]

                        ),

                }

            )

        ranking.sort(

            key=lambda x: x["ai_score"],

            reverse=True,

        )

        return ranking

    # =====================================================
    # BEST SECTOR
    # =====================================================

    def best_sector(self):

        sectors = self.top_sectors(1)

        if sectors:

            return sectors[0]

        return None

    # =====================================================
    # WORST SECTOR
    # =====================================================

    def worst_sector(self):

        sectors = self.worst_sectors(1)

        if sectors:

            return sectors[0]

        return None

    # =====================================================
    # COMPLETE SECTOR ANALYSIS
    # =====================================================

    def sector_analysis(self):

        return {

            "leaders":

                self.top_sectors(),

            "laggards":

                self.worst_sectors(),

            "rotation":

                self.sector_rotation(),

            "heatmap":

                self.heatmap(),

            "ranking":

                self.industry_ranking(),

        }
        # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(self):

        if hasattr(self, "_quote_cache"):

            self._quote_cache.clear()

        if hasattr(self, "_cache_time"):

            self._cache_time.clear()

    # =====================================================
    # CACHE STATISTICS
    # =====================================================

    def cache_statistics(self):

        cache = getattr(

            self,

            "_quote_cache",

            {},

        )

        return {

            "cached_symbols": len(cache),

            "symbols": list(cache.keys()),

        }

    # =====================================================
    # REQUEST THROTTLE
    # =====================================================

    def throttle(

        self,

        seconds=0.25,

    ):

        time.sleep(seconds)

    # =====================================================
    # SAFE REQUEST
    # =====================================================

    def safe_request(

        self,

        endpoint,

        params=None,

        retries=3,

    ):

        last_exception = None

        for _ in range(retries):

            try:

                self.throttle()

                return self.get_json(

                    endpoint,

                    params,

                )

            except Exception as exc:

                last_exception = exc

                self.refresh_session()

                time.sleep(1)

        if last_exception:

            self.logger.exception(

                last_exception

            )

        return {}

    # =====================================================
    # EXPORT DATAFRAME
    # =====================================================

    def dataframe(

        self,

        records,

    ):

        if records is None:

            return pd.DataFrame()

        if isinstance(

            records,

            pd.DataFrame,

        ):

            return records.copy()

        return pd.DataFrame(records)

    # =====================================================
    # EXPORT CSV
    # =====================================================

    def export_csv(

        self,

        records,

        filename,

    ):

        df = self.dataframe(

            records

        )

        if df.empty:

            return False

        df.to_csv(

            filename,

            index=False,

        )

        return True

    # =====================================================
    # EXPORT EXCEL
    # =====================================================

    def export_excel(

        self,

        records,

        filename,

    ):

        df = self.dataframe(

            records

        )

        if df.empty:

            return False

        df.to_excel(

            filename,

            index=False,

        )

        return True

    # =====================================================
    # SERVICE STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "connected":

                self.connection_status(),

            "server_time":

                self.server_time(),

            "indices":

                len(

                    self.available_indices()

                ),

            "cache":

                self.cache_statistics(),

        }

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        report = {

            "connection": False,

            "market_status": False,

            "indices": False,

        }

        try:

            report["connection"] = (

                self.connection_status()

            )

        except Exception:

            pass

        try:

            report["market_status"] = bool(

                self.market_status()

            )

        except Exception:

            pass

        try:

            report["indices"] = (

                len(

                    self.available_indices()

                ) > 0

            )

        except Exception:

            pass

        report["overall"] = all(

            report.values()

        )

        return report

    # =====================================================
    # VERSION
    # =====================================================

    def version(self):

        return {

            "service": "NSE Service",

            "version": "1.0.0",

            "provider": "NSE India",

            "transport": "HTTPS",

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.clear_cache()

        self.refresh_session()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        try:

            self.session.close()

        except Exception:

            pass

        self.clear_cache()

        self.logger.info(

            "NseService shutdown complete."

        )

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<NseService "

            f"connected={self.connection_status()} "

            f"indices={len(self.available_indices())}>"

        )


# =====================================================
# END OF FILE
# =====================================================
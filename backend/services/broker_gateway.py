from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ==========================================================
# ORDER TYPES
# ==========================================================

class OrderType(Enum):

    MARKET = "MARKET"

    LIMIT = "LIMIT"

    SL = "SL"

    SLM = "SL-M"


# ==========================================================
# PRODUCT TYPES
# ==========================================================

class ProductType(Enum):

    CNC = "CNC"

    MIS = "MIS"

    NRML = "NRML"

    MTF = "MTF"


# ==========================================================
# TRANSACTION
# ==========================================================

class TransactionType(Enum):

    BUY = "BUY"

    SELL = "SELL"


# ==========================================================
# ORDER STATUS
# ==========================================================

class OrderStatus(Enum):

    PENDING = "PENDING"

    OPEN = "OPEN"

    COMPLETE = "COMPLETE"

    CANCELLED = "CANCELLED"

    REJECTED = "REJECTED"

    TRIGGER_PENDING = "TRIGGER_PENDING"


# ==========================================================
# ORDER
# ==========================================================

@dataclass(slots=True)
class Order:

    order_id: str

    symbol: str

    transaction: TransactionType

    quantity: int

    order_type: OrderType

    product: ProductType

    price: float = 0

    trigger_price: float = 0

    average_price: float = 0

    filled_quantity: int = 0

    pending_quantity: int = 0

    status: OrderStatus = OrderStatus.PENDING

    broker: str = ""

    exchange: str = "NSE"

    created_at: datetime = field(
        default_factory=datetime.now
    )


# ==========================================================
# POSITION
# ==========================================================

@dataclass(slots=True)
class Position:

    symbol: str

    quantity: int

    average_price: float

    ltp: float

    pnl: float

    product: ProductType

    broker: str = ""


# ==========================================================
# HOLDING
# ==========================================================

@dataclass(slots=True)
class Holding:

    symbol: str

    quantity: int

    average_price: float

    current_price: float

    investment: float

    current_value: float

    pnl: float

    broker: str = ""


# ==========================================================
# BROKER BASE
# ==========================================================

class BrokerAdapter(ABC):

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self):
        ...

    @abstractmethod
    def place_order(self, order: Order):
        ...

    @abstractmethod
    def modify_order(self, order_id: str, **kwargs):
        ...

    @abstractmethod
    def cancel_order(self, order_id: str):
        ...

    @abstractmethod
    def order_book(self):
        ...

    @abstractmethod
    def positions(self):
        ...

    @abstractmethod
    def holdings(self):
        ...

    @abstractmethod
    def funds(self):
        ...


# ==========================================================
# BROKER GATEWAY
# ==========================================================

class BrokerGateway:

    def __init__(self):

        self.lock = threading.RLock()

        self.adapters: Dict[
            str,
            BrokerAdapter
        ] = {}

        self.active_broker = None

        self.orders: Dict[
            str,
            Order
        ] = {}

        self.connected = False

        self.last_sync = None
            # ==========================================================
    # REGISTER BROKER
    # ==========================================================

    def register_broker(

        self,

        name: str,

        adapter: BrokerAdapter,

    ):

        with self.lock:

            self.adapters[

                name.upper()

            ] = adapter

            if self.active_broker is None:

                self.active_broker = (

                    name.upper()

                )

    # ==========================================================
    # REMOVE BROKER
    # ==========================================================

    def remove_broker(

        self,

        name: str,

    ):

        with self.lock:

            self.adapters.pop(

                name.upper(),

                None,

            )

            if (

                self.active_broker

                ==

                name.upper()

            ):

                self.active_broker = None

                if self.adapters:

                    self.active_broker = next(

                        iter(

                            self.adapters

                        )

                    )

    # ==========================================================
    # AVAILABLE BROKERS
    # ==========================================================

    def brokers(

        self,

    ) -> List[str]:

        return sorted(

            self.adapters.keys()

        )

    # ==========================================================
    # ACTIVE ADAPTER
    # ==========================================================

    def adapter(

        self,

    ) -> Optional[BrokerAdapter]:

        if self.active_broker is None:

            return None

        return self.adapters.get(

            self.active_broker

        )

    # ==========================================================
    # SWITCH BROKER
    # ==========================================================

    def switch_broker(

        self,

        broker: str,

    ) -> bool:

        broker = broker.upper()

        if broker not in self.adapters:

            return False

        self.active_broker = broker

        return True

    # ==========================================================
    # CONNECT
    # ==========================================================

    def connect(

        self,

    ) -> bool:

        adapter = self.adapter()

        if adapter is None:

            return False

        try:

            adapter.connect()

            self.connected = True

            self.last_sync = datetime.now()

            return True

        except Exception:

            self.connected = False

            return False

    # ==========================================================
    # DISCONNECT
    # ==========================================================

    def disconnect(

        self,

    ):

        adapter = self.adapter()

        if adapter is None:

            return

        try:

            adapter.disconnect()

        except Exception:

            pass

        self.connected = False

    # ==========================================================
    # RECONNECT
    # ==========================================================

    def reconnect(

        self,

    ) -> bool:

        self.disconnect()

        return self.connect()

    # ==========================================================
    # LOGIN
    # ==========================================================

    def login(

        self,

    ) -> bool:

        return self.connect()

    # ==========================================================
    # LOGOUT
    # ==========================================================

    def logout(

        self,

    ):

        self.disconnect()

    # ==========================================================
    # BROKER HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict:

        return {

            "connected": self.connected,

            "active_broker": self.active_broker,

            "registered_brokers": len(

                self.adapters

            ),

            "last_sync": self.last_sync,

        }

    # ==========================================================
    # AUTO CONNECT
    # ==========================================================

    def auto_connect(

        self,

    ) -> bool:

        if self.connected:

            return True

        return self.connect()

    # ==========================================================
    # IS CONNECTED
    # ==========================================================

    def is_connected(

        self,

    ) -> bool:

        return self.connected
        # ==========================================================
    # VALIDATE ORDER
    # ==========================================================

    def validate_order(

        self,

        order: Order,

    ) -> bool:

        if not order.symbol:

            return False

        if order.quantity <= 0:

            return False

        if (

            order.order_type == OrderType.LIMIT

            and

            order.price <= 0

        ):

            return False

        if (

            order.order_type in (

                OrderType.SL,

                OrderType.SLM,

            )

            and

            order.trigger_price <= 0

        ):

            return False

        return True

    # ==========================================================
    # PLACE ORDER
    # ==========================================================

    def place_order(

        self,

        order: Order,

    ):

        if not self.auto_connect():

            raise ConnectionError(

                "Broker not connected."

            )

        if not self.validate_order(

            order

        ):

            raise ValueError(

                "Invalid order."

            )

        adapter = self.adapter()

        if adapter is None:

            raise RuntimeError(

                "No active broker."

            )

        order_id = adapter.place_order(

            order

        )

        order.order_id = order_id

        order.broker = self.active_broker

        order.status = OrderStatus.PENDING

        self.orders[

            order_id

        ] = order

        self.last_sync = datetime.now()

        return order_id

    # ==========================================================
    # MARKET ORDER
    # ==========================================================

    def market_order(

        self,

        symbol: str,

        transaction: TransactionType,

        quantity: int,

        product: ProductType = ProductType.MIS,

    ):

        order = Order(

            order_id="",

            symbol=symbol,

            transaction=transaction,

            quantity=quantity,

            order_type=OrderType.MARKET,

            product=product,

        )

        return self.place_order(

            order

        )

    # ==========================================================
    # LIMIT ORDER
    # ==========================================================

    def limit_order(

        self,

        symbol: str,

        transaction: TransactionType,

        quantity: int,

        price: float,

        product: ProductType = ProductType.MIS,

    ):

        order = Order(

            order_id="",

            symbol=symbol,

            transaction=transaction,

            quantity=quantity,

            order_type=OrderType.LIMIT,

            product=product,

            price=price,

        )

        return self.place_order(

            order

        )

    # ==========================================================
    # STOP LOSS ORDER
    # ==========================================================

    def stop_loss_order(

        self,

        symbol: str,

        transaction: TransactionType,

        quantity: int,

        trigger: float,

        limit_price: float,

        product: ProductType = ProductType.MIS,

    ):

        order = Order(

            order_id="",

            symbol=symbol,

            transaction=transaction,

            quantity=quantity,

            order_type=OrderType.SL,

            product=product,

            price=limit_price,

            trigger_price=trigger,

        )

        return self.place_order(

            order

        )

    # ==========================================================
    # STOP LOSS MARKET ORDER
    # ==========================================================

    def slm_order(

        self,

        symbol: str,

        transaction: TransactionType,

        quantity: int,

        trigger: float,

        product: ProductType = ProductType.MIS,

    ):

        order = Order(

            order_id="",

            symbol=symbol,

            transaction=transaction,

            quantity=quantity,

            order_type=OrderType.SLM,

            product=product,

            trigger_price=trigger,

        )

        return self.place_order(

            order

        )

    # ==========================================================
    # MODIFY ORDER
    # ==========================================================

    def modify_order(

        self,

        order_id: str,

        **kwargs,

    ):

        adapter = self.adapter()

        if adapter is None:

            return False

        result = adapter.modify_order(

            order_id,

            **kwargs,

        )

        if (

            result

            and

            order_id in self.orders

        ):

            order = self.orders[

                order_id

            ]

            for key, value in kwargs.items():

                if hasattr(

                    order,

                    key,

                ):

                    setattr(

                        order,

                        key,

                        value,

                    )

        self.last_sync = datetime.now()

        return result

    # ==========================================================
    # CANCEL ORDER
    # ==========================================================

    def cancel_order(

        self,

        order_id: str,

    ):

        adapter = self.adapter()

        if adapter is None:

            return False

        result = adapter.cancel_order(

            order_id

        )

        if (

            result

            and

            order_id in self.orders

        ):

            self.orders[

                order_id

            ].status = (

                OrderStatus.CANCELLED

            )

        self.last_sync = datetime.now()

        return result

    # ==========================================================
    # GET LOCAL ORDER
    # ==========================================================

    def order(

        self,

        order_id: str,

    ) -> Optional[Order]:

        return self.orders.get(

            order_id

        )
        # ==========================================================
    # SYNC ORDER BOOK
    # ==========================================================

    def sync_order_book(

        self,

    ) -> List[Order]:

        adapter = self.adapter()

        if adapter is None:

            return []

        try:

            broker_orders = adapter.order_book()

        except Exception:

            return []

        for order in broker_orders:

            self.orders[

                order.order_id

            ] = order

        self.last_sync = datetime.now()

        return broker_orders

    # ==========================================================
    # ORDER BOOK
    # ==========================================================

    def order_book(

        self,

        refresh: bool = True,

    ) -> List[Order]:

        if refresh:

            return self.sync_order_book()

        return list(

            self.orders.values()

        )

    # ==========================================================
    # OPEN ORDERS
    # ==========================================================

    def open_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status in (

                OrderStatus.OPEN,

                OrderStatus.PENDING,

                OrderStatus.TRIGGER_PENDING,

            )

        ]

    # ==========================================================
    # COMPLETED ORDERS
    # ==========================================================

    def completed_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status ==

            OrderStatus.COMPLETE

        ]

    # ==========================================================
    # CANCELLED ORDERS
    # ==========================================================

    def cancelled_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status ==

            OrderStatus.CANCELLED

        ]

    # ==========================================================
    # REJECTED ORDERS
    # ==========================================================

    def rejected_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status ==

            OrderStatus.REJECTED

        ]

    # ==========================================================
    # PENDING ORDERS
    # ==========================================================

    def pending_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status ==

            OrderStatus.PENDING

        ]

    # ==========================================================
    # TRIGGER PENDING ORDERS
    # ==========================================================

    def trigger_pending_orders(

        self,

    ) -> List[Order]:

        return [

            order

            for order in

            self.order_book(

                refresh=False

            )

            if order.status ==

            OrderStatus.TRIGGER_PENDING

        ]

    # ==========================================================
    # ORDER HISTORY
    # ==========================================================

    def order_history(

        self,

    ) -> List[Order]:

        return sorted(

            self.order_book(

                refresh=False

            ),

            key=lambda x: (

                x.created_at

            ),

            reverse=True,

        )

    # ==========================================================
    # GET ORDER STATUS
    # ==========================================================

    def order_status(

        self,

        order_id: str,

    ) -> Optional[OrderStatus]:

        order = self.orders.get(

            order_id

        )

        if order is None:

            return None

        return order.status

    # ==========================================================
    # REFRESH ORDERS
    # ==========================================================

    def refresh_orders(

        self,

    ) -> List[Order]:

        return self.sync_order_book()

    # ==========================================================
    # ORDER SUMMARY
    # ==========================================================

    def order_summary(

        self,

    ) -> Dict:

        return {

            "total": len(

                self.orders

            ),

            "open": len(

                self.open_orders()

            ),

            "completed": len(

                self.completed_orders()

            ),

            "pending": len(

                self.pending_orders()

            ),

            "cancelled": len(

                self.cancelled_orders()

            ),

            "rejected": len(

                self.rejected_orders()

            ),

            "trigger_pending": len(

                self.trigger_pending_orders()

            ),

        }
        # ==========================================================
    # SYNC POSITIONS
    # ==========================================================

    def sync_positions(

        self,

    ) -> List[Position]:

        adapter = self.adapter()

        if adapter is None:

            return []

        try:

            self._positions = adapter.positions()

        except Exception:

            self._positions = []

        self.last_sync = datetime.now()

        return self._positions

    # ==========================================================
    # POSITIONS
    # ==========================================================

    def positions(

        self,

        refresh: bool = True,

    ) -> List[Position]:

        if refresh:

            return self.sync_positions()

        return list(

            getattr(

                self,

                "_positions",

                [],

            )

        )

    # ==========================================================
    # OPEN POSITIONS
    # ==========================================================

    def open_positions(

        self,

    ) -> List[Position]:

        return [

            position

            for position in

            self.positions(

                refresh=False

            )

            if position.quantity != 0

        ]

    # ==========================================================
    # SYNC HOLDINGS
    # ==========================================================

    def sync_holdings(

        self,

    ) -> List[Holding]:

        adapter = self.adapter()

        if adapter is None:

            return []

        try:

            self._holdings = adapter.holdings()

        except Exception:

            self._holdings = []

        self.last_sync = datetime.now()

        return self._holdings

    # ==========================================================
    # HOLDINGS
    # ==========================================================

    def holdings(

        self,

        refresh: bool = True,

    ) -> List[Holding]:

        if refresh:

            return self.sync_holdings()

        return list(

            getattr(

                self,

                "_holdings",

                [],

            )

        )

    # ==========================================================
    # AVAILABLE FUNDS
    # ==========================================================

    def funds(

        self,

    ) -> Dict:

        adapter = self.adapter()

        if adapter is None:

            return {}

        try:

            return adapter.funds()

        except Exception:

            return {}

    # ==========================================================
    # USED MARGIN
    # ==========================================================

    def used_margin(

        self,

    ) -> float:

        data = self.funds()

        return float(

            data.get(

                "used_margin",

                0.0,

            )

        )

    # ==========================================================
    # AVAILABLE MARGIN
    # ==========================================================

    def available_margin(

        self,

    ) -> float:

        data = self.funds()

        return float(

            data.get(

                "available_margin",

                0.0,

            )

        )

    # ==========================================================
    # TOTAL EQUITY
    # ==========================================================

    def total_equity(

        self,

    ) -> float:

        data = self.funds()

        return float(

            data.get(

                "equity",

                0.0,

            )

        )

    # ==========================================================
    # TOTAL HOLDINGS VALUE
    # ==========================================================

    def holdings_value(

        self,

    ) -> float:

        return sum(

            holding.current_value

            for holding in

            self.holdings(

                refresh=False

            )

        )

    # ==========================================================
    # TOTAL POSITION PNL
    # ==========================================================

    def positions_pnl(

        self,

    ) -> float:

        return sum(

            position.pnl

            for position in

            self.positions(

                refresh=False

            )

        )

    # ==========================================================
    # TOTAL PORTFOLIO PNL
    # ==========================================================

    def portfolio_pnl(

        self,

    ) -> float:

        holdings_pnl = sum(

            holding.pnl

            for holding in

            self.holdings(

                refresh=False

            )

        )

        return (

            holdings_pnl

            +

            self.positions_pnl()

        )

    # ==========================================================
    # PORTFOLIO SUMMARY
    # ==========================================================

    def portfolio_summary(

        self,

    ) -> Dict:

        return {

            "positions": len(

                self.positions(

                    refresh=False

                )

            ),

            "holdings": len(

                self.holdings(

                    refresh=False

                )

            ),

            "holdings_value": self.holdings_value(),

            "positions_pnl": self.positions_pnl(),

            "portfolio_pnl": self.portfolio_pnl(),

            "available_margin": self.available_margin(),

            "used_margin": self.used_margin(),

            "equity": self.total_equity(),

            "last_sync": self.last_sync,

        }
        # ==========================================================
    # SYNC TRADE BOOK
    # ==========================================================

    def sync_trade_book(

        self,

    ) -> List[Dict]:

        adapter = self.adapter()

        if adapter is None:

            return []

        try:

            if hasattr(

                adapter,

                "trade_book",

            ):

                self._trade_book = (

                    adapter.trade_book()

                )

            else:

                self._trade_book = []

        except Exception:

            self._trade_book = []

        self.last_sync = datetime.now()

        return self._trade_book

    # ==========================================================
    # TRADE BOOK
    # ==========================================================

    def trade_book(

        self,

        refresh: bool = True,

    ) -> List[Dict]:

        if refresh:

            return self.sync_trade_book()

        return list(

            getattr(

                self,

                "_trade_book",

                [],

            )

        )

    # ==========================================================
    # TODAY TRADES
    # ==========================================================

    def today_trades(

        self,

    ) -> List[Dict]:

        today = datetime.now().date()

        trades = []

        for trade in self.trade_book(

            refresh=False,

        ):

            trade_time = trade.get(

                "timestamp",

            )

            if isinstance(

                trade_time,

                datetime,

            ):

                if (

                    trade_time.date()

                    == today

                ):

                    trades.append(

                        trade

                    )

        return trades

    # ==========================================================
    # SEARCH TRADES
    # ==========================================================

    def search_trades(

        self,

        symbol: str,

    ) -> List[Dict]:

        symbol = symbol.upper()

        return [

            trade

            for trade in

            self.trade_book(

                refresh=False,

            )

            if trade.get(

                "symbol",

                "",

            ).upper() == symbol

        ]

    # ==========================================================
    # ESTIMATE BROKERAGE
    # ==========================================================

    def estimate_brokerage(

        self,

        turnover: float,

        brokerage_percent: float = 0.03,

        max_brokerage: float = 20.0,

    ) -> float:

        brokerage = (

            turnover

            *

            brokerage_percent

            /

            100

        )

        return min(

            brokerage,

            max_brokerage,

        )

    # ==========================================================
    # ESTIMATE CHARGES
    # ==========================================================

    def estimate_charges(

        self,

        turnover: float,

    ) -> Dict:

        brokerage = (

            self.estimate_brokerage(

                turnover,

            )

        )

        stt = turnover * 0.001

        exchange = turnover * 0.0000345

        sebi = turnover * 0.000001

        gst = (

            brokerage

            +

            exchange

        ) * 0.18

        stamp = turnover * 0.00003

        total = (

            brokerage

            + stt

            + exchange

            + sebi

            + gst

            + stamp

        )

        return {

            "brokerage": brokerage,

            "stt": stt,

            "exchange": exchange,

            "sebi": sebi,

            "gst": gst,

            "stamp_duty": stamp,

            "total_charges": total,

        }

    # ==========================================================
    # NET PNL
    # ==========================================================

    def net_pnl(

        self,

        gross_pnl: float,

        turnover: float,

    ) -> float:

        charges = (

            self.estimate_charges(

                turnover,

            )

        )

        return (

            gross_pnl

            -

            charges[

                "total_charges"

            ]

        )

    # ==========================================================
    # WINNING TRADES
    # ==========================================================

    def winning_trades(

        self,

    ) -> List[Dict]:

        return [

            trade

            for trade in

            self.trade_book(

                refresh=False,

            )

            if trade.get(

                "pnl",

                0,

            ) > 0

        ]

    # ==========================================================
    # LOSING TRADES
    # ==========================================================

    def losing_trades(

        self,

    ) -> List[Dict]:

        return [

            trade

            for trade in

            self.trade_book(

                refresh=False,

            )

            if trade.get(

                "pnl",

                0,

            ) < 0

        ]

    # ==========================================================
    # WIN RATE
    # ==========================================================

    def win_rate(

        self,

    ) -> float:

        total = len(

            self.trade_book(

                refresh=False,

            )

        )

        if total == 0:

            return 0.0

        return (

            len(

                self.winning_trades()

            )

            /

            total

        ) * 100

    # ==========================================================
    # TRADE ANALYTICS
    # ==========================================================

    def trade_analytics(

        self,

    ) -> Dict:

        trades = self.trade_book(

            refresh=False,

        )

        gross_pnl = sum(

            trade.get(

                "pnl",

                0,

            )

            for trade in trades

        )

        turnover = sum(

            trade.get(

                "turnover",

                0,

            )

            for trade in trades

        )

        charges = self.estimate_charges(

            turnover,

        )

        return {

            "total_trades": len(

                trades,

            ),

            "winning_trades": len(

                self.winning_trades(),

            ),

            "losing_trades": len(

                self.losing_trades(),

            ),

            "win_rate": self.win_rate(),

            "gross_pnl": gross_pnl,

            "turnover": turnover,

            "charges": charges,

            "net_pnl": self.net_pnl(

                gross_pnl,

                turnover,

            ),

        }
        # ==========================================================
    # MAX ORDER VALUE
    # ==========================================================

    def max_order_value(

        self,

    ) -> float:

        return getattr(

            self,

            "_max_order_value",

            500000.0,

        )

    # ==========================================================
    # SET MAX ORDER VALUE
    # ==========================================================

    def set_max_order_value(

        self,

        value: float,

    ):

        self._max_order_value = max(

            0.0,

            value,

        )

    # ==========================================================
    # DAILY LOSS LIMIT
    # ==========================================================

    def daily_loss_limit(

        self,

    ) -> float:

        return getattr(

            self,

            "_daily_loss_limit",

            10000.0,

        )

    # ==========================================================
    # SET DAILY LOSS LIMIT
    # ==========================================================

    def set_daily_loss_limit(

        self,

        value: float,

    ):

        self._daily_loss_limit = max(

            0.0,

            value,

        )

    # ==========================================================
    # CURRENT DAILY LOSS
    # ==========================================================

    def current_daily_loss(

        self,

    ) -> float:

        pnl = self.trade_analytics()[

            "net_pnl"

        ]

        return abs(

            min(

                pnl,

                0,

            )

        )

    # ==========================================================
    # LOSS LIMIT BREACHED
    # ==========================================================

    def loss_limit_breached(

        self,

    ) -> bool:

        return (

            self.current_daily_loss()

            >=

            self.daily_loss_limit()

        )

    # ==========================================================
    # POSITION SIZE
    # ==========================================================

    def position_size(

        self,

        capital: float,

        risk_percent: float,

        stop_loss_points: float,

    ) -> int:

        if (

            capital <= 0

            or

            stop_loss_points <= 0

        ):

            return 0

        risk_amount = (

            capital

            *

            risk_percent

            /

            100

        )

        qty = int(

            risk_amount

            /

            stop_loss_points

        )

        return max(

            qty,

            0,

        )

    # ==========================================================
    # MARGIN CHECK
    # ==========================================================

    def validate_margin(

        self,

        required_margin: float,

    ) -> bool:

        return (

            self.available_margin()

            >=

            required_margin

        )

    # ==========================================================
    # EXPOSURE CHECK
    # ==========================================================

    def validate_exposure(

        self,

        order_value: float,

    ) -> bool:

        return (

            order_value

            <=

            self.max_order_value()

        )

    # ==========================================================
    # CIRCUIT LIMIT CHECK
    # ==========================================================

    def validate_circuit(

        self,

        ltp: float,

        price: float,

        upper_circuit: float,

        lower_circuit: float,

    ) -> bool:

        if price >= upper_circuit:

            return False

        if price <= lower_circuit:

            return False

        return True

    # ==========================================================
    # PRE TRADE RISK CHECK
    # ==========================================================

    def risk_check(

        self,

        order: Order,

        order_value: float,

        required_margin: float,

        ltp: float = 0,

        upper_circuit: float = float("inf"),

        lower_circuit: float = 0,

    ) -> Dict:

        if not self.validate_order(

            order,

        ):

            return {

                "success": False,

                "reason": "Invalid order",

            }

        if self.loss_limit_breached():

            return {

                "success": False,

                "reason": "Daily loss limit exceeded",

            }

        if not self.validate_margin(

            required_margin,

        ):

            return {

                "success": False,

                "reason": "Insufficient margin",

            }

        if not self.validate_exposure(

            order_value,

        ):

            return {

                "success": False,

                "reason": "Maximum exposure exceeded",

            }

        if ltp > 0:

            if not self.validate_circuit(

                ltp,

                order.price if order.price > 0 else ltp,

                upper_circuit,

                lower_circuit,

            ):

                return {

                    "success": False,

                    "reason": "Circuit limit violation",

                }

        return {

            "success": True,

            "reason": "Risk validation passed",

        }

    # ==========================================================
    # SAFE PLACE ORDER
    # ==========================================================

    def safe_place_order(

        self,

        order: Order,

        order_value: float,

        required_margin: float,

        **kwargs,

    ):

        result = self.risk_check(

            order,

            order_value,

            required_margin,

            **kwargs,

        )

        if not result["success"]:

            raise ValueError(

                result["reason"]

            )

        return self.place_order(

            order,

        )

    # ==========================================================
    # RISK DASHBOARD
    # ==========================================================

    def risk_dashboard(

        self,

    ) -> Dict:

        return {

            "daily_loss": self.current_daily_loss(),

            "daily_limit": self.daily_loss_limit(),

            "loss_limit_breached": self.loss_limit_breached(),

            "available_margin": self.available_margin(),

            "used_margin": self.used_margin(),

            "max_order_value": self.max_order_value(),

            "portfolio_pnl": self.portfolio_pnl(),

        }
        # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict:

        return {

            "registered_brokers": len(

                self.adapters

            ),

            "active_broker": self.active_broker,

            "connected": self.connected,

            "orders": len(

                self.orders

            ),

            "positions": len(

                getattr(

                    self,

                    "_positions",

                    [],

                )

            ),

            "holdings": len(

                getattr(

                    self,

                    "_holdings",

                    [],

                )

            ),

            "trades": len(

                getattr(

                    self,

                    "_trade_book",

                    [],

                )

            ),

            "last_sync": self.last_sync,

        }

    # ==========================================================
    # HEALTH
    # ==========================================================

    def gateway_health(

        self,

    ) -> Dict:

        return {

            "status": (

                "healthy"

                if self.connected

                else "disconnected"

            ),

            "statistics": self.statistics(),

            "portfolio": self.portfolio_summary(),

            "risk": self.risk_dashboard(),

        }

    # ==========================================================
    # AUTO SYNC
    # ==========================================================

    def sync(

        self,

    ):

        if not self.connected:

            return

        try:

            self.refresh_orders()

        except Exception:

            pass

        try:

            self.sync_positions()

        except Exception:

            pass

        try:

            self.sync_holdings()

        except Exception:

            pass

        try:

            self.sync_trade_book()

        except Exception:

            pass

        self.last_sync = datetime.now()

    # ==========================================================
    # REFRESH
    # ==========================================================

    def refresh(

        self,

    ):

        self.sync()

        return self.gateway_health()

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ) -> Dict:

        self.connect()

        self.sync()

        return self.gateway_health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ):

        self.disconnect()

        self.orders.clear()

        self._positions = []

        self._holdings = []

        self._trade_book = []

        self.last_sync = None

        return {

            "status": "shutdown",

        }

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        self.shutdown()

        self.adapters.clear()

        self.active_broker = None

        self.connected = False

    # ==========================================================
    # VERSION
    # ==========================================================

    @property

    def version(

        self,

    ) -> str:

        return "4.0"

    # ==========================================================
    # NAME
    # ==========================================================

    @property

    def name(

        self,

    ) -> str:

        return "Broker Gateway"

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ):

        return (

            "BrokerGateway("

            f"broker={self.active_broker}, "

            f"connected={self.connected}, "

            f"orders={len(self.orders)}"

            ")"

        )

    # ==========================================================
    # STR
    # ==========================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Broker Gateway\n"

            f"Version              : {self.version}\n"

            f"Registered Brokers   : {stats['registered_brokers']}\n"

            f"Active Broker        : {stats['active_broker']}\n"

            f"Connected            : {stats['connected']}\n"

            f"Orders               : {stats['orders']}\n"

            f"Positions            : {stats['positions']}\n"

            f"Holdings             : {stats['holdings']}\n"

            f"Trades               : {stats['trades']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

broker_gateway = BrokerGateway()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "OrderType",

    "ProductType",

    "TransactionType",

    "OrderStatus",

    "Order",

    "Position",

    "Holding",

    "BrokerAdapter",

    "BrokerGateway",

    "broker_gateway",

]
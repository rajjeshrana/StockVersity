from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional

import pandas as pd


# ==========================================================
# BACKTEST MODE
# ==========================================================

class BacktestMode(Enum):

    BAR_CLOSE = "BAR_CLOSE"

    EVERY_TICK = "EVERY_TICK"


# ==========================================================
# POSITION SIDE
# ==========================================================

class PositionSide(Enum):

    LONG = "LONG"

    SHORT = "SHORT"


# ==========================================================
# EXIT REASON
# ==========================================================

class ExitReason(Enum):

    TARGET = "TARGET"

    STOPLOSS = "STOPLOSS"

    TRAILING_STOP = "TRAILING_STOP"

    MANUAL = "MANUAL"

    STRATEGY_EXIT = "STRATEGY_EXIT"

    END_OF_TEST = "END_OF_TEST"


# ==========================================================
# ORDER RESULT
# ==========================================================

class OrderResult(Enum):

    FILLED = "FILLED"

    REJECTED = "REJECTED"

    CANCELLED = "CANCELLED"


# ==========================================================
# TRADE
# ==========================================================

@dataclass(slots=True)
class Trade:

    symbol: str

    side: PositionSide

    quantity: int

    entry_time: datetime

    entry_price: float

    stop_loss: float

    target: float

    exit_time: Optional[datetime] = None

    exit_price: float = 0.0

    pnl: float = 0.0

    brokerage: float = 0.0

    charges: float = 0.0

    net_pnl: float = 0.0

    exit_reason: ExitReason = ExitReason.END_OF_TEST

    bars_held: int = 0


# ==========================================================
# EQUITY POINT
# ==========================================================

@dataclass(slots=True)
class EquityPoint:

    timestamp: datetime

    equity: float

    drawdown: float


# ==========================================================
# BACKTEST CONFIG
# ==========================================================

@dataclass(slots=True)
class BacktestConfig:

    initial_capital: float = 100000.0

    brokerage_percent: float = 0.03

    max_brokerage: float = 20.0

    slippage_percent: float = 0.02

    mode: BacktestMode = BacktestMode.BAR_CLOSE

    allow_short: bool = True

    pyramiding: int = 1

    risk_per_trade: float = 1.0


# ==========================================================
# BACKTEST RESULT
# ==========================================================

@dataclass(slots=True)
class BacktestResult:

    initial_capital: float

    final_capital: float

    total_return: float

    trades: List[Trade]

    equity_curve: List[EquityPoint]

    statistics: Dict


# ==========================================================
# BACKTEST ENGINE
# ==========================================================

class BacktestingEngine:

    def __init__(self):

        self.lock = threading.RLock()

        self.config = BacktestConfig()

        self.data: Optional[pd.DataFrame] = None

        self.strategy = None

        self.symbol = ""

        self.current_trade: Optional[
            Trade
        ] = None

        self.completed_trades: List[
            Trade
        ] = []

        self.equity_curve: List[
            EquityPoint
        ] = []

        self.initial_capital = (
            self.config.initial_capital
        )

        self.current_capital = (
            self.initial_capital
        )

        self.max_equity = (
            self.initial_capital
        )

        self.running = False

        self.current_bar = 0
            # ==========================================================
    # CONFIGURATION
    # ==========================================================

    def configure(

        self,

        config: BacktestConfig,

    ):

        with self.lock:

            self.config = config

            self.initial_capital = (

                config.initial_capital

            )

            self.current_capital = (

                config.initial_capital

            )

            self.max_equity = (

                config.initial_capital

            )

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load_data(

        self,

        symbol: str,

        dataframe: pd.DataFrame,

    ):

        if dataframe is None:

            raise ValueError(

                "Historical data cannot be None."

            )

        if dataframe.empty:

            raise ValueError(

                "Historical data is empty."

            )

        required_columns = [

            "Open",

            "High",

            "Low",

            "Close",

        ]

        for column in required_columns:

            if column not in dataframe.columns:

                raise ValueError(

                    f"Missing column: {column}"

                )

        self.symbol = symbol.upper()

        self.data = (

            dataframe

            .copy()

            .reset_index(

                drop=True

            )

        )

    # ==========================================================
    # APPEND DATA
    # ==========================================================

    def append_data(

        self,

        dataframe: pd.DataFrame,

    ):

        if dataframe is None:

            return

        if dataframe.empty:

            return

        if self.data is None:

            self.data = (

                dataframe.copy()

            )

        else:

            self.data = pd.concat(

                [

                    self.data,

                    dataframe,

                ],

                ignore_index=True,

            )

    # ==========================================================
    # SET STRATEGY
    # ==========================================================

    def set_strategy(

        self,

        strategy: Callable,

    ):

        self.strategy = strategy

    # ==========================================================
    # GET STRATEGY
    # ==========================================================

    def get_strategy(

        self,

    ):

        return self.strategy

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
    # HAS STRATEGY
    # ==========================================================

    def has_strategy(

        self,

    ) -> bool:

        return (

            self.strategy

            is not None

        )

    # ==========================================================
    # VALIDATE ENGINE
    # ==========================================================

    def validate(

        self,

    ):

        if not self.has_data():

            raise RuntimeError(

                "Historical data not loaded."

            )

        if not self.has_strategy():

            raise RuntimeError(

                "Strategy not assigned."

            )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(

        self,

    ):

        self.current_trade = None

        self.completed_trades.clear()

        self.equity_curve.clear()

        self.current_bar = 0

        self.current_capital = (

            self.config.initial_capital

        )

        self.max_equity = (

            self.current_capital

        )

        self.running = False

    # ==========================================================
    # INITIALIZE
    # ==========================================================

    def initialize(

        self,

    ):

        self.validate()

        self.reset()

        self.running = True

    # ==========================================================
    # STOP
    # ==========================================================

    def stop(

        self,

    ):

        self.running = False

    # ==========================================================
    # TOTAL BARS
    # ==========================================================

    @property

    def total_bars(

        self,

    ) -> int:

        if self.data is None:

            return 0

        return len(

            self.data

        )

    # ==========================================================
    # CURRENT CANDLE
    # ==========================================================

    def candle(

        self,

        index: int,

    ) -> pd.Series:

        return self.data.iloc[

            index

        ]
        # ==========================================================
    # SLIPPAGE
    # ==========================================================

    def apply_slippage(

        self,

        price: float,

        side: PositionSide,

    ) -> float:

        slippage = (

            price

            *

            self.config.slippage_percent

            /

            100

        )

        if side == PositionSide.LONG:

            return price + slippage

        return price - slippage

    # ==========================================================
    # BROKERAGE
    # ==========================================================

    def brokerage(

        self,

        turnover: float,

    ) -> float:

        brokerage = (

            turnover

            *

            self.config.brokerage_percent

            /

            100

        )

        return min(

            brokerage,

            self.config.max_brokerage,

        )

    # ==========================================================
    # POSITION SIZE
    # ==========================================================

    def position_size(

        self,

        entry: float,

        stop_loss: float,

    ) -> int:

        risk_per_share = abs(

            entry

            -

            stop_loss

        )

        if risk_per_share <= 0:

            return 0

        risk_amount = (

            self.current_capital

            *

            self.config.risk_per_trade

            /

            100

        )

        qty = int(

            risk_amount

            /

            risk_per_share

        )

        return max(

            qty,

            1,

        )

    # ==========================================================
    # CAN ENTER
    # ==========================================================

    def can_enter(

        self,

    ) -> bool:

        if self.current_trade is not None:

            return False

        return True

    # ==========================================================
    # CREATE TRADE
    # ==========================================================

    def create_trade(

        self,

        side: PositionSide,

        price: float,

        stop_loss: float,

        target: float,

        quantity: Optional[int] = None,

    ) -> Optional[Trade]:

        if not self.can_enter():

            return None

        if quantity is None:

            quantity = self.position_size(

                price,

                stop_loss,

            )

        if quantity <= 0:

            return None

        entry_price = self.apply_slippage(

            price,

            side,

        )

        trade = Trade(

            symbol=self.symbol,

            side=side,

            quantity=quantity,

            entry_time=datetime.now(),

            entry_price=entry_price,

            stop_loss=stop_loss,

            target=target,

        )

        turnover = (

            quantity

            *

            entry_price

        )

        trade.brokerage = self.brokerage(

            turnover,

        )

        self.current_trade = trade

        return trade

    # ==========================================================
    # LONG ENTRY
    # ==========================================================

    def buy(

        self,

        price: float,

        stop_loss: float,

        target: float,

        quantity: Optional[int] = None,

    ) -> Optional[Trade]:

        return self.create_trade(

            PositionSide.LONG,

            price,

            stop_loss,

            target,

            quantity,

        )

    # ==========================================================
    # SHORT ENTRY
    # ==========================================================

    def sell(

        self,

        price: float,

        stop_loss: float,

        target: float,

        quantity: Optional[int] = None,

    ) -> Optional[Trade]:

        if not self.config.allow_short:

            return None

        return self.create_trade(

            PositionSide.SHORT,

            price,

            stop_loss,

            target,

            quantity,

        )

    # ==========================================================
    # HAS OPEN TRADE
    # ==========================================================

    def has_position(

        self,

    ) -> bool:

        return (

            self.current_trade

            is not None

        )

    # ==========================================================
    # CURRENT TRADE
    # ==========================================================

    def active_trade(

        self,

    ) -> Optional[Trade]:

        return self.current_trade

    # ==========================================================
    # RESERVED CAPITAL
    # ==========================================================

    def reserved_capital(

        self,

    ) -> float:

        if self.current_trade is None:

            return 0.0

        return (

            self.current_trade.entry_price

            *

            self.current_trade.quantity

        )

    # ==========================================================
    # AVAILABLE CAPITAL
    # ==========================================================

    def available_capital(

        self,

    ) -> float:

        return max(

            0.0,

            self.current_capital

            -

            self.reserved_capital(),

        )
        # ==========================================================
    # CALCULATE EXIT PRICE
    # ==========================================================

    def exit_price(

        self,

        price: float,

        side: PositionSide,

    ) -> float:

        slippage = (

            price

            *

            self.config.slippage_percent

            /

            100

        )

        if side == PositionSide.LONG:

            return price - slippage

        return price + slippage

    # ==========================================================
    # CALCULATE PNL
    # ==========================================================

    def calculate_pnl(

        self,

        trade: Trade,

        exit_price: float,

    ) -> float:

        if trade.side == PositionSide.LONG:

            return (

                exit_price

                -

                trade.entry_price

            ) * trade.quantity

        return (

            trade.entry_price

            -

            exit_price

        ) * trade.quantity

    # ==========================================================
    # COMPLETE TRADE
    # ==========================================================

    def close_trade(

        self,

        price: float,

        reason: ExitReason,

    ) -> Optional[Trade]:

        if self.current_trade is None:

            return None

        trade = self.current_trade

        trade.exit_time = datetime.now()

        trade.exit_reason = reason

        trade.exit_price = self.exit_price(

            price,

            trade.side,

        )

        turnover = (

            trade.entry_price

            +

            trade.exit_price

        ) * trade.quantity

        exit_brokerage = self.brokerage(

            turnover,

        )

        trade.pnl = self.calculate_pnl(

            trade,

            trade.exit_price,

        )

        trade.brokerage += exit_brokerage

        trade.charges = trade.brokerage

        trade.net_pnl = (

            trade.pnl

            -

            trade.charges

        )

        self.current_capital += (

            trade.net_pnl

        )

        self.max_equity = max(

            self.max_equity,

            self.current_capital,

        )

        self.completed_trades.append(

            trade

        )

        self.current_trade = None

        return trade

    # ==========================================================
    # TARGET EXIT
    # ==========================================================

    def target_exit(

        self,

    ) -> Optional[Trade]:

        if self.current_trade is None:

            return None

        return self.close_trade(

            self.current_trade.target,

            ExitReason.TARGET,

        )

    # ==========================================================
    # STOP LOSS EXIT
    # ==========================================================

    def stop_loss_exit(

        self,

    ) -> Optional[Trade]:

        if self.current_trade is None:

            return None

        return self.close_trade(

            self.current_trade.stop_loss,

            ExitReason.STOPLOSS,

        )

    # ==========================================================
    # MANUAL EXIT
    # ==========================================================

    def manual_exit(

        self,

        price: float,

    ) -> Optional[Trade]:

        return self.close_trade(

            price,

            ExitReason.MANUAL,

        )

    # ==========================================================
    # STRATEGY EXIT
    # ==========================================================

    def strategy_exit(

        self,

        price: float,

    ) -> Optional[Trade]:

        return self.close_trade(

            price,

            ExitReason.STRATEGY_EXIT,

        )

    # ==========================================================
    # END OF TEST EXIT
    # ==========================================================

    def end_of_test_exit(

        self,

        price: float,

    ) -> Optional[Trade]:

        return self.close_trade(

            price,

            ExitReason.END_OF_TEST,

        )

    # ==========================================================
    # TRAILING STOP UPDATE
    # ==========================================================

    def update_trailing_stop(

        self,

        new_stop: float,

    ):

        if self.current_trade is None:

            return

        trade = self.current_trade

        if trade.side == PositionSide.LONG:

            trade.stop_loss = max(

                trade.stop_loss,

                new_stop,

            )

        else:

            trade.stop_loss = min(

                trade.stop_loss,

                new_stop,

            )

    # ==========================================================
    # CHECK STOP LOSS
    # ==========================================================

    def stop_hit(

        self,

        low: float,

        high: float,

    ) -> bool:

        if self.current_trade is None:

            return False

        trade = self.current_trade

        if trade.side == PositionSide.LONG:

            return low <= trade.stop_loss

        return high >= trade.stop_loss

    # ==========================================================
    # CHECK TARGET
    # ==========================================================

    def target_hit(

        self,

        low: float,

        high: float,

    ) -> bool:

        if self.current_trade is None:

            return False

        trade = self.current_trade

        if trade.side == PositionSide.LONG:

            return high >= trade.target

        return low <= trade.target

    # ==========================================================
    # UPDATE BARS HELD
    # ==========================================================

    def update_trade_duration(

        self,

    ):

        if self.current_trade is not None:

            self.current_trade.bars_held += 1
                # ==========================================================
    # PROCESS BAR
    # ==========================================================

    def process_bar(

        self,

        index: int,

    ):

        candle = self.candle(

            index,

        )

        if self.strategy is None:

            return

        signal = self.strategy(

            self.data.iloc[: index + 1]

        )

        self.execute_signal(

            signal,

            candle,

        )

        self.update_trade_duration()

        self.update_equity_curve(

            candle,

        )

    # ==========================================================
    # EXECUTE SIGNAL
    # ==========================================================

    def execute_signal(

        self,

        signal,

        candle,

    ):

        if signal is None:

            return

        close = float(

            candle["Close"]

        )

        high = float(

            candle["High"]

        )

        low = float(

            candle["Low"]

        )

        # -----------------------------
        # Existing Position
        # -----------------------------

        if self.has_position():

            if self.stop_hit(

                low,

                high,

            ):

                self.stop_loss_exit()

                return

            if self.target_hit(

                low,

                high,

            ):

                self.target_exit()

                return

        # -----------------------------
        # Strategy Signals
        # -----------------------------

        action = str(

            signal.get(

                "action",

                "",

            )

        ).upper()

        if action == "BUY":

            self.buy(

                price=close,

                stop_loss=signal[

                    "stop_loss"

                ],

                target=signal[

                    "target"

                ],

                quantity=signal.get(

                    "quantity"

                ),

            )

        elif action == "SELL":

            self.sell(

                price=close,

                stop_loss=signal[

                    "stop_loss"

                ],

                target=signal[

                    "target"

                ],

                quantity=signal.get(

                    "quantity"

                ),

            )

        elif action == "EXIT":

            self.strategy_exit(

                close,

            )

        elif action == "TRAIL":

            self.update_trailing_stop(

                signal[

                    "stop_loss"

                ]

            )

    # ==========================================================
    # UPDATE EQUITY CURVE
    # ==========================================================

    def update_equity_curve(

        self,

        candle,

    ):

        equity = self.current_capital

        if self.current_trade is not None:

            close = float(

                candle["Close"]

            )

            unrealized = self.calculate_pnl(

                self.current_trade,

                close,

            )

            equity += unrealized

        self.max_equity = max(

            self.max_equity,

            equity,

        )

        drawdown = (

            self.max_equity

            -

            equity

        )

        timestamp = (

            candle.name

            if hasattr(

                candle,

                "name",

            )

            else datetime.now()

        )

        self.equity_curve.append(

            EquityPoint(

                timestamp=timestamp,

                equity=equity,

                drawdown=drawdown,

            )

        )

    # ==========================================================
    # MAIN BACKTEST LOOP
    # ==========================================================

    def run(

        self,

    ):

        self.initialize()

        for index in range(

            self.total_bars

        ):

            if not self.running:

                break

            self.current_bar = index

            self.process_bar(

                index,

            )

        if self.current_trade:

            last_close = float(

                self.data.iloc[-1][

                    "Close"

                ]

            )

            self.end_of_test_exit(

                last_close,

            )

        self.running = False

        return self.results()

    # ==========================================================
    # STEP FORWARD
    # ==========================================================

    def step(

        self,

    ):

        if (

            self.current_bar

            >=

            self.total_bars

        ):

            return False

        self.process_bar(

            self.current_bar,

        )

        self.current_bar += 1

        return True

    # ==========================================================
    # PLAY
    # ==========================================================

    def play(

        self,

    ):

        self.initialize()

        while self.step():

            pass

        if self.current_trade:

            last_close = float(

                self.data.iloc[-1][

                    "Close"

                ]

            )

            self.end_of_test_exit(

                last_close,

            )

        return self.results()

    # ==========================================================
    # PAUSE
    # ==========================================================

    def pause(

        self,

    ):

        self.running = False

    # ==========================================================
    # RESUME
    # ==========================================================

    def resume(

        self,

    ):

        self.running = True

        while (

            self.running

            and

            self.current_bar

            <

            self.total_bars

        ):

            self.step()
                # ==========================================================
    # TOTAL TRADES
    # ==========================================================

    def total_trades(

        self,

    ) -> int:

        return len(

            self.completed_trades

        )

    # ==========================================================
    # WINNING TRADES
    # ==========================================================

    def winning_trades(

        self,

    ) -> List[Trade]:

        return [

            trade

            for trade in

            self.completed_trades

            if trade.net_pnl > 0

        ]

    # ==========================================================
    # LOSING TRADES
    # ==========================================================

    def losing_trades(

        self,

    ) -> List[Trade]:

        return [

            trade

            for trade in

            self.completed_trades

            if trade.net_pnl < 0

        ]

    # ==========================================================
    # WIN RATE
    # ==========================================================

    def win_rate(

        self,

    ) -> float:

        total = self.total_trades()

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
    # GROSS PROFIT
    # ==========================================================

    def gross_profit(

        self,

    ) -> float:

        return sum(

            trade.net_pnl

            for trade in

            self.winning_trades()

        )

    # ==========================================================
    # GROSS LOSS
    # ==========================================================

    def gross_loss(

        self,

    ) -> float:

        return abs(

            sum(

                trade.net_pnl

                for trade in

                self.losing_trades()

            )

        )

    # ==========================================================
    # PROFIT FACTOR
    # ==========================================================

    def profit_factor(

        self,

    ) -> float:

        loss = self.gross_loss()

        if loss == 0:

            return float("inf")

        return (

            self.gross_profit()

            /

            loss

        )

    # ==========================================================
    # AVERAGE WIN
    # ==========================================================

    def average_win(

        self,

    ) -> float:

        wins = self.winning_trades()

        if not wins:

            return 0.0

        return (

            self.gross_profit()

            /

            len(

                wins

            )

        )

    # ==========================================================
    # AVERAGE LOSS
    # ==========================================================

    def average_loss(

        self,

    ) -> float:

        losses = self.losing_trades()

        if not losses:

            return 0.0

        return (

            self.gross_loss()

            /

            len(

                losses

            )

        )

    # ==========================================================
    # EXPECTANCY
    # ==========================================================

    def expectancy(

        self,

    ) -> float:

        win_rate = (

            self.win_rate()

            /

            100

        )

        loss_rate = (

            1

            -

            win_rate

        )

        return (

            win_rate

            *

            self.average_win()

        ) - (

            loss_rate

            *

            self.average_loss()

        )

    # ==========================================================
    # MAX DRAWDOWN
    # ==========================================================

    def max_drawdown(

        self,

    ) -> float:

        if not self.equity_curve:

            return 0.0

        return max(

            point.drawdown

            for point in

            self.equity_curve

        )

    # ==========================================================
    # TOTAL RETURN
    # ==========================================================

    def total_return(

        self,

    ) -> float:

        return (

            (

                self.current_capital

                -

                self.initial_capital

            )

            /

            self.initial_capital

        ) * 100

    # ==========================================================
    # CAGR
    # ==========================================================

    def cagr(

        self,

    ) -> float:

        if self.data is None:

            return 0.0

        years = max(

            len(

                self.data

            )

            /

            252,

            1 / 252,

        )

        ratio = (

            self.current_capital

            /

            self.initial_capital

        )

        return (

            (

                ratio

                ** (

                    1 / years

                )

            )

            -

            1

        ) * 100

    # ==========================================================
    # SHARPE RATIO
    # ==========================================================

    def sharpe_ratio(

        self,

        risk_free_rate: float = 0.0,

    ) -> float:

        if len(

            self.completed_trades

        ) < 2:

            return 0.0

        returns = pd.Series(

            [

                trade.net_pnl

                for trade in

                self.completed_trades

            ]

        )

        std = returns.std()

        if std == 0:

            return 0.0

        return (

            (

                returns.mean()

                -

                risk_free_rate

            )

            /

            std

        )

    # ==========================================================
    # SORTINO RATIO
    # ==========================================================

    def sortino_ratio(

        self,

        risk_free_rate: float = 0.0,

    ) -> float:

        if len(

            self.completed_trades

        ) < 2:

            return 0.0

        returns = pd.Series(

            [

                trade.net_pnl

                for trade in

                self.completed_trades

            ]

        )

        downside = returns[

            returns < 0

        ]

        if downside.empty:

            return float("inf")

        downside_std = downside.std()

        if downside_std == 0:

            return 0.0

        return (

            (

                returns.mean()

                -

                risk_free_rate

            )

            /

            downside_std

        )

    # ==========================================================
    # RECOVERY FACTOR
    # ==========================================================

    def recovery_factor(

        self,

    ) -> float:

        drawdown = self.max_drawdown()

        if drawdown == 0:

            return float("inf")

        net_profit = (

            self.current_capital

            -

            self.initial_capital

        )

        return (

            net_profit

            /

            drawdown

        )
        # ==========================================================
    # MONTHLY RETURNS
    # ==========================================================

    def monthly_returns(

        self,

    ) -> Dict[str, float]:

        monthly = {}

        for trade in self.completed_trades:

            if trade.exit_time is None:

                continue

            key = trade.exit_time.strftime(

                "%Y-%m"

            )

            monthly.setdefault(

                key,

                0.0,

            )

            monthly[key] += trade.net_pnl

        return dict(

            sorted(

                monthly.items()

            )

        )

    # ==========================================================
    # YEARLY RETURNS
    # ==========================================================

    def yearly_returns(

        self,

    ) -> Dict[str, float]:

        yearly = {}

        for trade in self.completed_trades:

            if trade.exit_time is None:

                continue

            key = str(

                trade.exit_time.year

            )

            yearly.setdefault(

                key,

                0.0,

            )

            yearly[key] += trade.net_pnl

        return dict(

            sorted(

                yearly.items()

            )

        )

    # ==========================================================
    # LONG TRADES
    # ==========================================================

    def long_trades(

        self,

    ) -> List[Trade]:

        return [

            trade

            for trade in

            self.completed_trades

            if trade.side == PositionSide.LONG

        ]

    # ==========================================================
    # SHORT TRADES
    # ==========================================================

    def short_trades(

        self,

    ) -> List[Trade]:

        return [

            trade

            for trade in

            self.completed_trades

            if trade.side == PositionSide.SHORT

        ]

    # ==========================================================
    # BEST TRADE
    # ==========================================================

    def best_trade(

        self,

    ) -> Optional[Trade]:

        if not self.completed_trades:

            return None

        return max(

            self.completed_trades,

            key=lambda t: t.net_pnl,

        )

    # ==========================================================
    # WORST TRADE
    # ==========================================================

    def worst_trade(

        self,

    ) -> Optional[Trade]:

        if not self.completed_trades:

            return None

        return min(

            self.completed_trades,

            key=lambda t: t.net_pnl,

        )

    # ==========================================================
    # CONSECUTIVE WINS
    # ==========================================================

    def max_consecutive_wins(

        self,

    ) -> int:

        streak = 0

        maximum = 0

        for trade in self.completed_trades:

            if trade.net_pnl > 0:

                streak += 1

                maximum = max(

                    maximum,

                    streak,

                )

            else:

                streak = 0

        return maximum

    # ==========================================================
    # CONSECUTIVE LOSSES
    # ==========================================================

    def max_consecutive_losses(

        self,

    ) -> int:

        streak = 0

        maximum = 0

        for trade in self.completed_trades:

            if trade.net_pnl < 0:

                streak += 1

                maximum = max(

                    maximum,

                    streak,

                )

            else:

                streak = 0

        return maximum

    # ==========================================================
    # AVERAGE HOLDING PERIOD
    # ==========================================================

    def average_holding_period(

        self,

    ) -> float:

        if not self.completed_trades:

            return 0.0

        total = sum(

            trade.bars_held

            for trade in

            self.completed_trades

        )

        return (

            total

            /

            len(

                self.completed_trades

            )

        )

    # ==========================================================
    # EQUITY STATISTICS
    # ==========================================================

    def equity_statistics(

        self,

    ) -> Dict:

        if not self.equity_curve:

            return {}

        values = [

            point.equity

            for point in

            self.equity_curve

        ]

        return {

            "start_equity": values[0],

            "end_equity": values[-1],

            "highest_equity": max(

                values

            ),

            "lowest_equity": min(

                values

            ),

            "max_drawdown": self.max_drawdown(),

        }

    # ==========================================================
    # PERFORMANCE DASHBOARD
    # ==========================================================

    def performance_dashboard(

        self,

    ) -> Dict:

        return {

            "total_trades": self.total_trades(),

            "win_rate": self.win_rate(),

            "profit_factor": self.profit_factor(),

            "expectancy": self.expectancy(),

            "cagr": self.cagr(),

            "total_return": self.total_return(),

            "max_drawdown": self.max_drawdown(),

            "recovery_factor": self.recovery_factor(),

            "sharpe_ratio": self.sharpe_ratio(),

            "sortino_ratio": self.sortino_ratio(),

            "average_win": self.average_win(),

            "average_loss": self.average_loss(),

            "best_trade": self.best_trade(),

            "worst_trade": self.worst_trade(),

            "long_trades": len(

                self.long_trades()

            ),

            "short_trades": len(

                self.short_trades()

            ),

            "max_consecutive_wins":

                self.max_consecutive_wins(),

            "max_consecutive_losses":

                self.max_consecutive_losses(),

            "average_holding_period":

                self.average_holding_period(),

            "equity":

                self.equity_statistics(),

            "monthly_returns":

                self.monthly_returns(),

            "yearly_returns":

                self.yearly_returns(),

        }
        # ==========================================================
    # EXPORT TRADES
    # ==========================================================

    def export_trades(

        self,

    ) -> pd.DataFrame:

        rows = []

        for trade in self.completed_trades:

            rows.append(

                {

                    "Symbol": trade.symbol,

                    "Side": trade.side.value,

                    "Entry Time": trade.entry_time,

                    "Exit Time": trade.exit_time,

                    "Entry Price": trade.entry_price,

                    "Exit Price": trade.exit_price,

                    "Quantity": trade.quantity,

                    "PnL": trade.pnl,

                    "Charges": trade.charges,

                    "Net PnL": trade.net_pnl,

                    "Bars Held": trade.bars_held,

                    "Exit Reason": trade.exit_reason.value,

                }

            )

        return pd.DataFrame(

            rows

        )

    # ==========================================================
    # EXPORT EQUITY CURVE
    # ==========================================================

    def export_equity_curve(

        self,

    ) -> pd.DataFrame:

        rows = []

        for point in self.equity_curve:

            rows.append(

                {

                    "Timestamp": point.timestamp,

                    "Equity": point.equity,

                    "Drawdown": point.drawdown,

                }

            )

        return pd.DataFrame(

            rows

        )

    # ==========================================================
    # EXPORT SUMMARY
    # ==========================================================

    def export_summary(

        self,

    ) -> pd.DataFrame:

        dashboard = (

            self.performance_dashboard()

        )

        rows = []

        for key, value in dashboard.items():

            if isinstance(

                value,

                (

                    dict,

                    list,

                    Trade,

                ),

            ):

                continue

            rows.append(

                {

                    "Metric": key,

                    "Value": value,

                }

            )

        return pd.DataFrame(

            rows

        )

    # ==========================================================
    # EXPORT CSV
    # ==========================================================

    def export_csv(

        self,

        directory: str,

    ):

        self.export_trades().to_csv(

            f"{directory}/trades.csv",

            index=False,

        )

        self.export_equity_curve().to_csv(

            f"{directory}/equity_curve.csv",

            index=False,

        )

        self.export_summary().to_csv(

            f"{directory}/summary.csv",

            index=False,

        )

    # ==========================================================
    # EXPORT EXCEL
    # ==========================================================

    def export_excel(

        self,

        filename: str,

    ):

        with pd.ExcelWriter(

            filename,

        ) as writer:

            self.export_trades().to_excel(

                writer,

                sheet_name="Trades",

                index=False,

            )

            self.export_equity_curve().to_excel(

                writer,

                sheet_name="Equity Curve",

                index=False,

            )

            self.export_summary().to_excel(

                writer,

                sheet_name="Summary",

                index=False,

            )

    # ==========================================================
    # EXPORT JSON
    # ==========================================================

    def export_json(

        self,

    ) -> Dict:

        return {

            "statistics":

                self.performance_dashboard(),

            "trades":

                self.export_trades().to_dict(

                    orient="records",

                ),

            "equity_curve":

                self.export_equity_curve().to_dict(

                    orient="records",

                ),

        }

    # ==========================================================
    # IMPORT JSON
    # ==========================================================

    def import_json(

        self,

        data: Dict,

    ):

        self.imported_statistics = data.get(

            "statistics",

            {},

        )

        self.imported_trades = data.get(

            "trades",

            [],

        )

        self.imported_equity_curve = data.get(

            "equity_curve",

            [],

        )

    # ==========================================================
    # COMPARE STRATEGIES
    # ==========================================================

    def compare(

        self,

        other: "BacktestingEngine",

    ) -> Dict:

        return {

            "strategy_1":

                self.performance_dashboard(),

            "strategy_2":

                other.performance_dashboard(),

            "winner":

                "Strategy 1"

                if self.total_return()

                >

                other.total_return()

                else "Strategy 2",

        }

    # ==========================================================
    # BATCH BACKTEST
    # ==========================================================

    def batch_backtest(

        self,

        strategies: Dict[str, Callable],

    ) -> Dict:

        results = {}

        original = self.strategy

        for name, strategy in strategies.items():

            self.set_strategy(

                strategy,

            )

            self.run()

            results[name] = (

                self.performance_dashboard()

            )

        self.set_strategy(

            original,

        )

        return results

    # ==========================================================
    # PORTFOLIO BACKTEST
    # ==========================================================

    def portfolio_backtest(

        self,

        datasets: Dict[str, pd.DataFrame],

        strategy: Callable,

    ) -> Dict:

        portfolio = {}

        for symbol, dataframe in datasets.items():

            self.load_data(

                symbol,

                dataframe,

            )

            self.set_strategy(

                strategy,

            )

            self.run()

            portfolio[symbol] = (

                self.performance_dashboard()

            )

        return portfolio
        # ==========================================================
    # WALK FORWARD TEST
    # ==========================================================

    def walk_forward_test(

        self,

        train_ratio: float = 0.70,

    ) -> Dict:

        self.validate()

        split = int(

            len(self.data)

            * train_ratio

        )

        train = self.data.iloc[:split].copy()

        test = self.data.iloc[split:].copy()

        original = self.data

        # -------------------------
        # Training
        # -------------------------

        self.load_data(

            self.symbol,

            train,

        )

        self.run()

        train_stats = (

            self.performance_dashboard()

        )

        # -------------------------
        # Testing
        # -------------------------

        self.load_data(

            self.symbol,

            test,

        )

        self.run()

        test_stats = (

            self.performance_dashboard()

        )

        self.data = original

        return {

            "train": train_stats,

            "test": test_stats,

        }

    # ==========================================================
    # MONTE CARLO SIMULATION
    # ==========================================================

    def monte_carlo(

        self,

        simulations: int = 1000,

    ) -> Dict:

        import random

        if not self.completed_trades:

            return {}

        final_equities = []

        trade_returns = [

            t.net_pnl

            for t in self.completed_trades

        ]

        for _ in range(

            simulations

        ):

            equity = self.initial_capital

            sequence = random.sample(

                trade_returns,

                len(trade_returns),

            )

            for pnl in sequence:

                equity += pnl

            final_equities.append(

                equity

            )

        return {

            "simulations": simulations,

            "best_equity": max(

                final_equities

            ),

            "worst_equity": min(

                final_equities

            ),

            "average_equity": sum(

                final_equities

            ) / len(

                final_equities

            ),

        }

    # ==========================================================
    # GRID SEARCH
    # ==========================================================

    def optimize(

        self,

        parameter_grid: Dict,

        strategy_factory: Callable,

    ) -> List[Dict]:

        import itertools

        keys = list(

            parameter_grid.keys()

        )

        values = [

            parameter_grid[k]

            for k in keys

        ]

        original_strategy = (

            self.strategy

        )

        results = []

        for combination in itertools.product(

            *values

        ):

            params = dict(

                zip(

                    keys,

                    combination,

                )

            )

            strategy = strategy_factory(

                **params

            )

            self.set_strategy(

                strategy

            )

            self.run()

            results.append(

                {

                    "parameters": params,

                    "return": self.total_return(),

                    "profit_factor": self.profit_factor(),

                    "win_rate": self.win_rate(),

                }

            )

        self.set_strategy(

            original_strategy

        )

        results.sort(

            key=lambda x: x["return"],

            reverse=True,

        )

        return results

    # ==========================================================
    # MULTI TIMEFRAME TEST
    # ==========================================================

    def multi_timeframe(

        self,

        datasets: Dict[str, pd.DataFrame],

    ) -> Dict:

        original = self.data

        results = {}

        for timeframe, df in datasets.items():

            self.load_data(

                self.symbol,

                df,

            )

            self.run()

            results[

                timeframe

            ] = (

                self.performance_dashboard()

            )

        self.data = original

        return results

    # ==========================================================
    # BUY & HOLD BENCHMARK
    # ==========================================================

    def benchmark_buy_hold(

        self,

    ) -> float:

        if self.data is None:

            return 0.0

        first = float(

            self.data.iloc[0]["Close"]

        )

        last = float(

            self.data.iloc[-1]["Close"]

        )

        return (

            (

                last

                -

                first

            )

            /

            first

        ) * 100

    # ==========================================================
    # OUT OF SAMPLE SCORE
    # ==========================================================

    def out_of_sample_score(

        self,

    ) -> Dict:

        wf = self.walk_forward_test()

        train_return = wf["train"][

            "total_return"

        ]

        test_return = wf["test"][

            "total_return"

        ]

        stability = 0.0

        if train_return != 0:

            stability = (

                test_return

                /

                train_return

            ) * 100

        return {

            "train_return": train_return,

            "test_return": test_return,

            "stability": stability,

        }

    # ==========================================================
    # ROBUSTNESS SCORE
    # ==========================================================

    def robustness_score(

        self,

    ) -> float:

        score = 0.0

        score += min(

            self.win_rate(),

            100,

        ) * 0.25

        score += min(

            self.profit_factor(),

            5,

        ) * 10

        score += max(

            0,

            100

            -

            self.max_drawdown(),

        ) * 0.25

        score += min(

            self.total_return(),

            100,

        ) * 0.25

        return round(

            score,

            2,

        )

    # ==========================================================
    # AI OPTIMIZATION HOOK
    # ==========================================================

    def optimization_features(

        self,

    ) -> Dict:

        return {

            "win_rate": self.win_rate(),

            "profit_factor": self.profit_factor(),

            "expectancy": self.expectancy(),

            "drawdown": self.max_drawdown(),

            "return": self.total_return(),

            "sharpe": self.sharpe_ratio(),

            "sortino": self.sortino_ratio(),

            "recovery": self.recovery_factor(),

            "robustness": self.robustness_score(),

        }
        # ==========================================================
    # RESULTS
    # ==========================================================

    def results(

        self,

    ) -> BacktestResult:

        statistics = self.performance_dashboard()

        return BacktestResult(

            initial_capital=self.initial_capital,

            final_capital=self.current_capital,

            total_return=self.total_return(),

            trades=list(

                self.completed_trades

            ),

            equity_curve=list(

                self.equity_curve

            ),

            statistics=statistics,

        )

    # ==========================================================
    # ENGINE STATISTICS
    # ==========================================================

    def statistics(

        self,

    ) -> Dict:

        return {

            "symbol": self.symbol,

            "bars_processed": self.current_bar,

            "total_bars": self.total_bars,

            "running": self.running,

            "current_capital": self.current_capital,

            "initial_capital": self.initial_capital,

            "completed_trades": len(

                self.completed_trades

            ),

            "open_trade": (

                self.current_trade

                is not None

            ),

            "equity_points": len(

                self.equity_curve

            ),

        }

    # ==========================================================
    # ENGINE HEALTH
    # ==========================================================

    def health(

        self,

    ) -> Dict:

        return {

            "status": (

                "running"

                if self.running

                else "idle"

            ),

            "statistics": self.statistics(),

            "performance": (

                self.performance_dashboard()

            ),

        }

    # ==========================================================
    # STARTUP
    # ==========================================================

    def startup(

        self,

    ) -> Dict:

        self.initialize()

        return self.health()

    # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(

        self,

    ) -> Dict:

        self.stop()

        self.current_trade = None

        return {

            "status": "shutdown",

        }

    # ==========================================================
    # CLEAR RESULTS
    # ==========================================================

    def clear_results(

        self,

    ):

        self.completed_trades.clear()

        self.equity_curve.clear()

        self.current_trade = None

        self.current_capital = (

            self.initial_capital

        )

        self.max_equity = (

            self.initial_capital

        )

        self.current_bar = 0

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

        return "Backtesting Engine"

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(

        self,

    ):

        return (

            "BacktestingEngine("

            f"symbol='{self.symbol}', "

            f"capital={self.current_capital:.2f}, "

            f"trades={len(self.completed_trades)}, "

            f"running={self.running}"

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

            "Backtesting Engine\n"

            f"Version             : {self.version}\n"

            f"Symbol              : {stats['symbol']}\n"

            f"Bars Processed      : {stats['bars_processed']}/{stats['total_bars']}\n"

            f"Capital             : {stats['current_capital']:.2f}\n"

            f"Completed Trades    : {stats['completed_trades']}\n"

            f"Running             : {stats['running']}"

        )


# ==========================================================
# GLOBAL SINGLETON
# ==========================================================

backtesting_engine = BacktestingEngine()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "BacktestMode",

    "PositionSide",

    "ExitReason",

    "OrderResult",

    "Trade",

    "EquityPoint",

    "BacktestConfig",

    "BacktestResult",

    "BacktestingEngine",

    "backtesting_engine",

]
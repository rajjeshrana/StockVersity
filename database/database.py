"""
=========================================================
StockVersity Scanner Pro
Database Manager

Professional SQLite Database Layer
=========================================================
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime


class DatabaseManager:

    def __init__(self):

        self.database_folder = Path("database")

        self.database_folder.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.database_path = (

            self.database_folder

            / "stockversity.db"

        )

        self.connection = sqlite3.connect(

            self.database_path,

            check_same_thread=False,

        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.create_tables()

    # =====================================================
    # CREATE ALL TABLES
    # =====================================================

    def create_tables(self):

        self.create_opportunity_table()

        self.create_watchlist_table()

        self.create_scan_history_table()

        self.create_settings_table()

        self.create_alert_table()

        self.create_portfolio_table()

        self.connection.commit()

    # =====================================================
    # OPPORTUNITY TABLE
    # =====================================================

    def create_opportunity_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS opportunities(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT,

            company TEXT,

            sector TEXT,

            timeframe TEXT,

            signal TEXT,

            pattern TEXT,

            entry REAL,

            stoploss REAL,

            target REAL,

            rr REAL,

            ai_score REAL,

            priority TEXT,

            confidence TEXT,

            volume_ratio REAL,

            rsi REAL,

            adx REAL,

            created_at TEXT

        )

        """)

    # =====================================================
    # WATCHLIST
    # =====================================================

    def create_watchlist_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS watchlist(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT UNIQUE,

            added_on TEXT

        )

        """)

    # =====================================================
    # SCAN HISTORY
    # =====================================================

    def create_scan_history_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS scan_history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            scan_time TEXT,

            total INTEGER,

            average_score REAL

        )

        """)

    # =====================================================
    # SETTINGS
    # =====================================================

    def create_settings_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS settings(

            key TEXT PRIMARY KEY,

            value TEXT

        )

        """)

    # =====================================================
    # ALERTS
    # =====================================================

    def create_alert_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS alerts(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT,

            condition TEXT,

            target REAL,

            active INTEGER

        )

        """)

    # =====================================================
    # PORTFOLIO
    # =====================================================

    def create_portfolio_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS portfolio(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT,

            quantity INTEGER,

            buy_price REAL,

            current_price REAL,

            pnl REAL,

            created_at TEXT

        )

        """)

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    def close(self):

        self.connection.commit()

        self.connection.close()
            # =====================================================
    # INSERT OPPORTUNITY
    # =====================================================

    def insert_opportunity(
        self,
        opportunity,
    ):

        self.cursor.execute(
            """
            INSERT INTO opportunities(
                symbol,
                company,
                sector,
                timeframe,
                signal,
                pattern,
                entry,
                stoploss,
                target,
                rr,
                ai_score,
                priority,
                confidence,
                volume_ratio,
                rsi,
                adx,
                created_at
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                opportunity.symbol,
                opportunity.company,
                opportunity.sector,
                opportunity.timeframe,
                opportunity.signal,
                opportunity.pattern,
                opportunity.entry,
                opportunity.stoploss,
                opportunity.target,
                opportunity.risk_reward,
                opportunity.ai_score,
                getattr(opportunity, "priority", ""),
                getattr(opportunity, "confidence", ""),
                opportunity.volume_ratio,
                opportunity.rsi,
                opportunity.adx,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
        )

        self.connection.commit()

    # =====================================================
    # BULK INSERT
    # =====================================================

    def insert_many(
        self,
        opportunities,
    ):

        self.clear_opportunities()

        for opportunity in opportunities:

            self.insert_opportunity(
                opportunity
            )

    # =====================================================
    # LOAD ALL
    # =====================================================

    def opportunities(self):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            ORDER BY
            ai_score DESC,
            rr DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # SEARCH SYMBOL
    # =====================================================

    def search_symbol(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE symbol=?
            """,
            (symbol,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # SEARCH PATTERN
    # =====================================================

    def search_pattern(
        self,
        pattern,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE pattern=?
            ORDER BY ai_score DESC
            """,
            (pattern,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # FILTER TIMEFRAME
    # =====================================================

    def timeframe(
        self,
        timeframe,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE timeframe=?
            ORDER BY ai_score DESC
            """,
            (timeframe,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # FILTER AI SCORE
    # =====================================================

    def minimum_score(
        self,
        score,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE ai_score>=?
            ORDER BY ai_score DESC
            """,
            (score,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # TOP TRADES
    # =====================================================

    def top_trades(
        self,
        limit=20,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            ORDER BY
                ai_score DESC,
                rr DESC
            LIMIT ?
            """,
            (limit,),
        )

        return self.cursor.fetchall()

    # =====================================================
    # UPDATE OPPORTUNITY
    # =====================================================

    def update_score(
        self,
        symbol,
        score,
    ):

        self.cursor.execute(
            """
            UPDATE opportunities
            SET ai_score=?
            WHERE symbol=?
            """,
            (
                score,
                symbol,
            ),
        )

        self.connection.commit()

    # =====================================================
    # DELETE
    # =====================================================

    def delete_opportunity(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            DELETE
            FROM opportunities
            WHERE symbol=?
            """,
            (symbol,),
        )

        self.connection.commit()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_opportunities(self):

        self.cursor.execute(
            """
            DELETE FROM opportunities
            """
        )

        self.connection.commit()

    # =====================================================
    # COUNT
    # =====================================================

    def opportunity_count(self):

        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM opportunities
            """
        )

        return self.cursor.fetchone()[0]
        # =====================================================
    # WATCHLIST
    # =====================================================

    def add_to_watchlist(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO watchlist(
                symbol,
                added_on
            )
            VALUES(?,?)
            """,
            (
                symbol.upper(),
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
        )

        self.connection.commit()

    # =====================================================
    # REMOVE WATCHLIST
    # =====================================================

    def remove_from_watchlist(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            DELETE FROM watchlist
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

        self.connection.commit()

    # =====================================================
    # LOAD WATCHLIST
    # =====================================================

    def watchlist(self):

        self.cursor.execute(
            """
            SELECT *
            FROM watchlist
            ORDER BY added_on DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # WATCHLIST COUNT
    # =====================================================

    def watchlist_count(self):

        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM watchlist
            """
        )

        return self.cursor.fetchone()[0]

    # =====================================================
    # SYMBOL EXISTS
    # =====================================================

    def in_watchlist(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            SELECT 1
            FROM watchlist
            WHERE symbol=?
            LIMIT 1
            """,
            (
                symbol.upper(),
            ),
        )

        return self.cursor.fetchone() is not None

    # =====================================================
    # CLEAR WATCHLIST
    # =====================================================

    def clear_watchlist(self):

        self.cursor.execute(
            """
            DELETE FROM watchlist
            """
        )

        self.connection.commit()

    # =====================================================
    # SCAN HISTORY
    # =====================================================

    def add_scan_history(
        self,
        total,
        average_score,
    ):

        self.cursor.execute(
            """
            INSERT INTO scan_history(
                scan_time,
                total,
                average_score
            )
            VALUES(?,?,?)
            """,
            (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                total,
                average_score,
            ),
        )

        self.connection.commit()

    # =====================================================
    # LOAD SCAN HISTORY
    # =====================================================

    def scan_history(self):

        self.cursor.execute(
            """
            SELECT *
            FROM scan_history
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # LAST SCAN
    # =====================================================

    def last_scan(self):

        self.cursor.execute(
            """
            SELECT *
            FROM scan_history
            ORDER BY id DESC
            LIMIT 1
            """
        )

        return self.cursor.fetchone()

    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    def clear_scan_history(self):

        self.cursor.execute(
            """
            DELETE FROM scan_history
            """
        )

        self.connection.commit()

    # =====================================================
    # PORTFOLIO
    # =====================================================

    def add_holding(
        self,
        symbol,
        quantity,
        buy_price,
    ):

        self.cursor.execute(
            """
            INSERT INTO portfolio(
                symbol,
                quantity,
                buy_price,
                current_price,
                pnl,
                created_at
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                symbol.upper(),
                quantity,
                buy_price,
                buy_price,
                0.0,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
        )

        self.connection.commit()

    # =====================================================
    # UPDATE MARKET PRICE
    # =====================================================

    def update_market_price(
        self,
        symbol,
        current_price,
    ):

        self.cursor.execute(
            """
            SELECT
                quantity,
                buy_price
            FROM portfolio
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

        row = self.cursor.fetchone()

        if row is None:
            return

        pnl = (
            current_price
            - row["buy_price"]
        ) * row["quantity"]

        self.cursor.execute(
            """
            UPDATE portfolio
            SET
                current_price=?,
                pnl=?
            WHERE symbol=?
            """,
            (
                current_price,
                pnl,
                symbol.upper(),
            ),
        )

        self.connection.commit()

    # =====================================================
    # LOAD PORTFOLIO
    # =====================================================

    def portfolio(self):

        self.cursor.execute(
            """
            SELECT *
            FROM portfolio
            ORDER BY created_at DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # DELETE HOLDING
    # =====================================================

    def remove_holding(
        self,
        symbol,
    ):

        self.cursor.execute(
            """
            DELETE FROM portfolio
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

        self.connection.commit()

    # =====================================================
    # TOTAL PORTFOLIO PNL
    # =====================================================

    def total_portfolio_pnl(self):

        self.cursor.execute(
            """
            SELECT
                COALESCE(SUM(pnl),0)
            FROM portfolio
            """
        )

        return self.cursor.fetchone()[0]
        # =====================================================
    # ALERT MANAGEMENT
    # =====================================================

    def create_alert(
        self,
        symbol,
        condition,
        target,
        active=True,
    ):

        self.cursor.execute(
            """
            INSERT INTO alerts(
                symbol,
                condition,
                target,
                active
            )
            VALUES(?,?,?,?)
            """,
            (
                symbol.upper(),
                condition,
                target,
                1 if active else 0,
            ),
        )

        self.connection.commit()

        return self.cursor.lastrowid

    # =====================================================
    # GET ALERTS
    # =====================================================

    def alerts(self):

        self.cursor.execute(
            """
            SELECT *
            FROM alerts
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # ACTIVE ALERTS
    # =====================================================

    def active_alerts(self):

        self.cursor.execute(
            """
            SELECT *
            FROM alerts
            WHERE active=1
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # UPDATE ALERT
    # =====================================================

    def update_alert(
        self,
        alert_id,
        symbol,
        condition,
        target,
        active,
    ):

        self.cursor.execute(
            """
            UPDATE alerts
            SET
                symbol=?,
                condition=?,
                target=?,
                active=?
            WHERE id=?
            """,
            (
                symbol.upper(),
                condition,
                target,
                1 if active else 0,
                alert_id,
            ),
        )

        self.connection.commit()

    # =====================================================
    # ENABLE ALERT
    # =====================================================

    def enable_alert(
        self,
        alert_id,
    ):

        self.cursor.execute(
            """
            UPDATE alerts
            SET active=1
            WHERE id=?
            """,
            (
                alert_id,
            ),
        )

        self.connection.commit()

    # =====================================================
    # DISABLE ALERT
    # =====================================================

    def disable_alert(
        self,
        alert_id,
    ):

        self.cursor.execute(
            """
            UPDATE alerts
            SET active=0
            WHERE id=?
            """,
            (
                alert_id,
            ),
        )

        self.connection.commit()

    # =====================================================
    # DELETE ALERT
    # =====================================================

    def delete_alert(
        self,
        alert_id,
    ):

        self.cursor.execute(
            """
            DELETE FROM alerts
            WHERE id=?
            """,
            (
                alert_id,
            ),
        )

        self.connection.commit()

    # =====================================================
    # CLEAR ALERTS
    # =====================================================

    def clear_alerts(self):

        self.cursor.execute(
            """
            DELETE FROM alerts
            """
        )

        self.connection.commit()

    # =====================================================
    # SETTINGS
    # =====================================================

    def set_setting(
        self,
        key,
        value,
    ):

        self.cursor.execute(
            """
            INSERT OR REPLACE INTO settings(
                key,
                value
            )
            VALUES(?,?)
            """,
            (
                key,
                str(value),
            ),
        )

        self.connection.commit()

    # =====================================================
    # GET SETTING
    # =====================================================

    def get_setting(
        self,
        key,
        default=None,
    ):

        self.cursor.execute(
            """
            SELECT value
            FROM settings
            WHERE key=?
            """,
            (
                key,
            ),
        )

        row = self.cursor.fetchone()

        if row is None:
            return default

        return row["value"]

    # =====================================================
    # LOAD SETTINGS
    # =====================================================

    def all_settings(self):

        self.cursor.execute(
            """
            SELECT *
            FROM settings
            """
        )

        rows = self.cursor.fetchall()

        return {
            row["key"]: row["value"]
            for row in rows
        }

    # =====================================================
    # DELETE SETTING
    # =====================================================

    def delete_setting(
        self,
        key,
    ):

        self.cursor.execute(
            """
            DELETE FROM settings
            WHERE key=?
            """,
            (
                key,
            ),
        )

        self.connection.commit()

    # =====================================================
    # DEFAULT SETTINGS
    # =====================================================

    def initialize_default_settings(self):

        defaults = {

            "theme": "dark",

            "scanner_interval": "15m",

            "scanner_market": "NIFTY500",

            "risk_percent": "1",

            "reward_ratio": "2",

            "capital": "100000",

            "broker": "Paper",

            "auto_refresh": "True",

            "refresh_interval": "60",

            "max_results": "50",

            "notifications": "True",

        }

        for key, value in defaults.items():

            if self.get_setting(key) is None:

                self.set_setting(
                    key,
                    value,
                )

    # =====================================================
    # RESET SETTINGS
    # =====================================================

    def reset_settings(self):

        self.cursor.execute(
            """
            DELETE FROM settings
            """
        )

        self.connection.commit()

        self.initialize_default_settings()
            # =====================================================
    # DATABASE BACKUP
    # =====================================================

    def backup_database(
        self,
        destination,
    ):

        destination = Path(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup = sqlite3.connect(destination)

        self.connection.backup(backup)

        backup.close()

        return destination

    # =====================================================
    # RESTORE DATABASE
    # =====================================================

    def restore_database(
        self,
        source,
    ):

        source = Path(source)

        if not source.exists():

            raise FileNotFoundError(source)

        self.connection.close()

        self.database_path.write_bytes(
            source.read_bytes()
        )

        self.connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

    # =====================================================
    # VACUUM DATABASE
    # =====================================================

    def vacuum(self):

        self.cursor.execute("VACUUM")

        self.connection.commit()

    # =====================================================
    # ANALYZE DATABASE
    # =====================================================

    def analyze(self):

        self.cursor.execute("ANALYZE")

        self.connection.commit()

    # =====================================================
    # DATABASE SIZE
    # =====================================================

    def database_size_mb(self):

        if not self.database_path.exists():

            return 0

        size = self.database_path.stat().st_size

        return round(

            size / (1024 * 1024),

            2,

        )

    # =====================================================
    # DATABASE STATISTICS
    # =====================================================

    def statistics(self):

        return {

            "opportunities": self.opportunity_count(),

            "watchlist": self.watchlist_count(),

            "alerts": len(self.alerts()),

            "portfolio": len(self.portfolio()),

            "history": len(self.scan_history()),

            "database_size_mb": self.database_size_mb(),

        }

    # =====================================================
    # BEST OPPORTUNITY
    # =====================================================

    def best_opportunity(self):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            ORDER BY ai_score DESC
            LIMIT 1
            """
        )

        return self.cursor.fetchone()

    # =====================================================
    # HIGH RR TRADES
    # =====================================================

    def high_rr_trades(
        self,
        minimum_rr=2,
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE rr>=?
            ORDER BY rr DESC
            """,
            (
                minimum_rr,
            ),
        )

        return self.cursor.fetchall()

    # =====================================================
    # TODAY OPPORTUNITIES
    # =====================================================

    def today_opportunities(self):

        today = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            """
            SELECT *
            FROM opportunities
            WHERE DATE(created_at)=?
            ORDER BY ai_score DESC
            """,
            (
                today,
            ),
        )

        return self.cursor.fetchall()

    # =====================================================
    # SECTOR SUMMARY
    # =====================================================

    def sector_summary(self):

        self.cursor.execute(
            """
            SELECT
                sector,
                COUNT(*) AS total,
                AVG(ai_score) AS average_score
            FROM opportunities
            GROUP BY sector
            ORDER BY average_score DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # SIGNAL SUMMARY
    # =====================================================

    def signal_summary(self):

        self.cursor.execute(
            """
            SELECT
                signal,
                COUNT(*) AS total
            FROM opportunities
            GROUP BY signal
            ORDER BY total DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # PATTERN SUMMARY
    # =====================================================

    def pattern_summary(self):

        self.cursor.execute(
            """
            SELECT
                pattern,
                COUNT(*) AS total
            FROM opportunities
            GROUP BY pattern
            ORDER BY total DESC
            """
        )

        return self.cursor.fetchall()

    # =====================================================
    # PORTFOLIO VALUE
    # =====================================================

    def portfolio_value(self):

        self.cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(
                        quantity * current_price
                    ),
                    0
                )
            FROM portfolio
            """
        )

        return self.cursor.fetchone()[0]

    # =====================================================
    # INVESTED VALUE
    # =====================================================

    def invested_value(self):

        self.cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(
                        quantity * buy_price
                    ),
                    0
                )
            FROM portfolio
            """
        )

        return self.cursor.fetchone()[0]

    # =====================================================
    # PROFIT PERCENT
    # =====================================================

    def portfolio_return_percent(self):

        invested = self.invested_value()

        if invested == 0:

            return 0.0

        pnl = self.total_portfolio_pnl()

        return round(

            pnl * 100 / invested,

            2,

        )
        # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health_check(self):

        try:

            self.cursor.execute("SELECT 1")

            self.cursor.fetchone()

            return True

        except sqlite3.Error:

            return False

    # =====================================================
    # BEGIN TRANSACTION
    # =====================================================

    def begin_transaction(self):

        self.connection.execute("BEGIN")

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self):

        self.connection.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self):

        self.connection.rollback()

    # =====================================================
    # EXECUTE QUERY
    # =====================================================

    def execute(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        self.cursor.execute(

            query,

            parameters,

        )

        self.connection.commit()

        return self.cursor

    # =====================================================
    # FETCH ALL
    # =====================================================

    def fetchall(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        self.cursor.execute(

            query,

            parameters,

        )

        return self.cursor.fetchall()

    # =====================================================
    # FETCH ONE
    # =====================================================

    def fetchone(
        self,
        query,
        parameters=None,
    ):

        if parameters is None:

            parameters = ()

        self.cursor.execute(

            query,

            parameters,

        )

        return self.cursor.fetchone()

    # =====================================================
    # RESET DATABASE
    # =====================================================

    def reset_database(self):

        tables = [

            "opportunities",

            "watchlist",

            "scan_history",

            "alerts",

            "portfolio",

            "settings",

        ]

        for table in tables:

            self.cursor.execute(

                f"DELETE FROM {table}"

            )

        self.connection.commit()

        self.initialize_default_settings()

    # =====================================================
    # EXPORT OPPORTUNITIES
    # =====================================================

    def export_opportunities(self):

        rows = self.opportunities()

        return [

            dict(row)

            for row in rows

        ]

    # =====================================================
    # IMPORT OPPORTUNITIES
    # =====================================================

    def import_opportunities(
        self,
        opportunities,
    ):

        self.clear_opportunities()

        for row in opportunities:

            self.cursor.execute(
                """
                INSERT INTO opportunities(
                    symbol,
                    company,
                    sector,
                    timeframe,
                    signal,
                    pattern,
                    entry,
                    stoploss,
                    target,
                    rr,
                    ai_score,
                    priority,
                    confidence,
                    volume_ratio,
                    rsi,
                    adx,
                    created_at
                )
                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?
                )
                """,
                (
                    row.get("symbol"),
                    row.get("company"),
                    row.get("sector"),
                    row.get("timeframe"),
                    row.get("signal"),
                    row.get("pattern"),
                    row.get("entry"),
                    row.get("stoploss"),
                    row.get("target"),
                    row.get("rr"),
                    row.get("ai_score"),
                    row.get("priority"),
                    row.get("confidence"),
                    row.get("volume_ratio"),
                    row.get("rsi"),
                    row.get("adx"),
                    row.get("created_at"),
                ),
            )

        self.connection.commit()

    # =====================================================
    # DATABASE VERSION
    # =====================================================

    def database_version(self):

        self.cursor.execute(

            "SELECT sqlite_version()"

        )

        return self.cursor.fetchone()[0]

    # =====================================================
    # CONNECTION INFO
    # =====================================================

    def info(self):

        return {

            "database": str(self.database_path),

            "sqlite_version": self.database_version(),

            "size_mb": self.database_size_mb(),

            "healthy": self.health_check(),

            "statistics": self.statistics(),

        }

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        if exc_type is None:

            self.connection.commit()

        else:

            self.connection.rollback()

        self.close()

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            f"<DatabaseManager "

            f"path='{self.database_path}' "

            f"healthy={self.health_check()} "

            f"opportunities={self.opportunity_count()} "

            f"watchlist={self.watchlist_count()}>"

        )


# ==========================================================
# END OF FILE
# ==========================================================
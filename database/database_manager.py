"""
=========================================================
        StockVersity Scanner Pro
              Powered by AI
=========================================================

Database Manager

Features
--------
✓ SQLite Database
✓ Thread Safe
✓ Auto Table Creation
✓ Scan History
✓ Portfolio
✓ Favorites
✓ Trade Journal
✓ AI History
✓ Alerts
✓ Market Snapshot
✓ User Settings
✓ Backup & Restore
✓ Database Statistics

Version : 4.0
"""

from __future__ import annotations

import sqlite3
import threading
import json
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager


class DatabaseManager:

    DATABASE_NAME = "stockversity.db"
    DATABASE_VERSION = "4.0"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self, database_path: str | None = None):

        self.lock = threading.RLock()

        if database_path:

            self.database_path = Path(database_path)

        else:

            self.database_path = (
                Path(__file__).resolve().parent
                / self.DATABASE_NAME
            )

        self.connection = None

        self.connect()

        self.initialize_database()

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(self):

        if self.connection is None:

            self.connection = sqlite3.connect(

                self.database_path,

                check_same_thread=False,

            )

            self.connection.row_factory = sqlite3.Row

            self.connection.execute(

                "PRAGMA foreign_keys = ON"

            )

            self.connection.execute(

                "PRAGMA journal_mode=WAL"

            )

            self.connection.execute(

                "PRAGMA synchronous=NORMAL"

            )

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    @contextmanager
    def cursor(self):

        with self.lock:

            cur = self.connection.cursor()

            try:

                yield cur

                self.connection.commit()

            except Exception:

                self.connection.rollback()

                raise

            finally:

                cur.close()

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        sql,

        params=(),

    ):

        with self.cursor() as cur:

            cur.execute(

                sql,

                params,

            )

            return cur

    # =====================================================
    # FETCH ONE
    # =====================================================

    def fetchone(

        self,

        sql,

        params=(),

    ):

        with self.cursor() as cur:

            cur.execute(

                sql,

                params,

            )

            row = cur.fetchone()

        return dict(row) if row else None

    # =====================================================
    # FETCH ALL
    # =====================================================

    def fetchall(

        self,

        sql,

        params=(),

    ):

        with self.cursor() as cur:

            cur.execute(

                sql,

                params,

            )

            rows = cur.fetchall()

        return [

            dict(row)

            for row in rows

        ]

    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    def initialize_database(self):

        self.create_metadata_table()

        self.create_scan_history_table()

        self.create_scan_profiles_table()

        self.create_favorites_table()

        self.create_portfolio_table()

        self.create_trade_journal_table()

        self.create_ai_history_table()

        self.create_alerts_table()

        self.create_market_snapshot_table()

        self.create_settings_table()

        self.save_database_version()

    # =====================================================
    # METADATA TABLE
    # =====================================================

    def create_metadata_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata(

                id INTEGER PRIMARY KEY,

                database_version TEXT,

                created_at TEXT,

                updated_at TEXT

            )
            """
        )

    # =====================================================
    # SAVE VERSION
    # =====================================================

    def save_database_version(self):

        version = self.fetchone(

            "SELECT * FROM metadata LIMIT 1"

        )

        now = datetime.now().isoformat()

        if version:

            self.execute(
                """
                UPDATE metadata
                SET database_version=?,
                    updated_at=?
                """,
                (

                    self.DATABASE_VERSION,

                    now,

                ),
            )

        else:

            self.execute(
                """
                INSERT INTO metadata(

                    database_version,

                    created_at,

                    updated_at

                )
                VALUES(?,?,?)
                """,
                (

                    self.DATABASE_VERSION,

                    now,

                    now,

                ),
            )

    # =====================================================
    # DATABASE VERSION
    # =====================================================

    def database_version(self):

        row = self.fetchone(

            "SELECT database_version FROM metadata LIMIT 1"

        )

        if row:

            return row["database_version"]

        return "Unknown"

    # =====================================================
    # DATABASE EXISTS
    # =====================================================

    def exists(self):

        return self.database_path.exists()

    # =====================================================
    # DATABASE SIZE
    # =====================================================

    def size_mb(self):

        if not self.exists():

            return 0

        size = self.database_path.stat().st_size

        return round(size / 1024 / 1024, 2)

    # =====================================================
    # BACKUP
    # =====================================================

    def backup(self, destination):

        shutil.copy2(

            self.database_path,

            destination,

        )

        return destination

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(self, backup_file):

        self.close()

        shutil.copy2(

            backup_file,

            self.database_path,

        )

        self.connect()

        return True

    # =====================================================
    # VACUUM
    # =====================================================

    def vacuum(self):

        self.execute("VACUUM")

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(self):

        self.execute("ANALYZE")
            # =====================================================
    # SCAN HISTORY
    # =====================================================

    def create_scan_history_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT NOT NULL,

                scan_type TEXT,

                signal TEXT,

                ai_score REAL,

                confidence REAL,

                entry_price REAL,

                stop_loss REAL,

                target_price REAL,

                rr REAL,

                timeframe TEXT,

                sector TEXT,

                strategy TEXT,

                remarks TEXT,

                created_at TEXT NOT NULL

            )
            """
        )

        self.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_scan_symbol
            ON scan_history(symbol)
            """
        )

        self.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_scan_created
            ON scan_history(created_at)
            """
        )

    # =====================================================
    # SCAN PROFILES
    # =====================================================

    def create_scan_profiles_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_profiles(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                profile_name TEXT UNIQUE,

                scan_type TEXT,

                settings_json TEXT,

                created_at TEXT,

                updated_at TEXT

            )
            """
        )

    # =====================================================
    # FAVORITES
    # =====================================================

    def create_favorites_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT UNIQUE,

                company_name TEXT,

                sector TEXT,

                notes TEXT,

                created_at TEXT

            )
            """
        )

    # =====================================================
    # PORTFOLIO
    # =====================================================

    def create_portfolio_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                quantity INTEGER,

                buy_price REAL,

                current_price REAL,

                average_price REAL,

                target_price REAL,

                stop_loss REAL,

                investment REAL,

                current_value REAL,

                pnl REAL,

                pnl_percent REAL,

                ai_score REAL,

                sector TEXT,

                created_at TEXT,

                updated_at TEXT

            )
            """
        )

        self.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_portfolio_symbol
            ON portfolio(symbol)
            """
        )

    # =====================================================
    # TRADE JOURNAL
    # =====================================================

    def create_trade_journal_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_journal(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                trade_type TEXT,

                quantity INTEGER,

                entry_price REAL,

                exit_price REAL,

                stop_loss REAL,

                target_price REAL,

                pnl REAL,

                rr REAL,

                result TEXT,

                emotion TEXT,

                notes TEXT,

                screenshot TEXT,

                entry_time TEXT,

                exit_time TEXT

            )
            """
        )

    # =====================================================
    # AI HISTORY
    # =====================================================

    def create_ai_history_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_history(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                ai_score REAL,

                confidence REAL,

                signal TEXT,

                recommendation TEXT,

                reason TEXT,

                timeframe TEXT,

                created_at TEXT

            )
            """
        )

        self.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_symbol
            ON ai_history(symbol)
            """
        )

    # =====================================================
    # ALERTS
    # =====================================================

    def create_alerts_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                symbol TEXT,

                alert_type TEXT,

                condition TEXT,

                trigger_price REAL,

                status TEXT,

                message TEXT,

                created_at TEXT,

                triggered_at TEXT

            )
            """
        )

    # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def create_market_snapshot_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS market_snapshot(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                nifty REAL,

                banknifty REAL,

                finnifty REAL,

                midcap REAL,

                sensex REAL,

                india_vix REAL,

                pcr REAL,

                fii REAL,

                dii REAL,

                advances INTEGER,

                declines INTEGER,

                sentiment TEXT,

                created_at TEXT

            )
            """
        )

    # =====================================================
    # SETTINGS
    # =====================================================

    def create_settings_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS settings(

                setting_key TEXT PRIMARY KEY,

                setting_value TEXT,

                updated_at TEXT

            )
            """
        )

    # =====================================================
    # DATABASE INFORMATION
    # =====================================================

    def database_information(self):

        return {

            "database": self.DATABASE_NAME,

            "version": self.database_version(),

            "path": str(self.database_path),

            "size_mb": self.size_mb(),

            "created": self.fetchone(
                "SELECT created_at FROM metadata LIMIT 1"
            ),

        }

    # =====================================================
    # TABLE LIST
    # =====================================================

    def tables(self):

        rows = self.fetchall(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        )

        return [row["name"] for row in rows]
        # =====================================================
    # SCAN HISTORY CRUD
    # =====================================================

    def add_scan_history(
        self,
        symbol,
        scan_type,
        signal,
        ai_score,
        confidence,
        entry_price,
        stop_loss,
        target_price,
        rr,
        timeframe="",
        sector="",
        strategy="",
        remarks="",
    ):

        self.execute(
            """
            INSERT INTO scan_history(

                symbol,
                scan_type,
                signal,
                ai_score,
                confidence,
                entry_price,
                stop_loss,
                target_price,
                rr,
                timeframe,
                sector,
                strategy,
                remarks,
                created_at

            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                symbol.upper(),
                scan_type,
                signal,
                ai_score,
                confidence,
                entry_price,
                stop_loss,
                target_price,
                rr,
                timeframe,
                sector,
                strategy,
                remarks,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def get_scan_history(
        self,
        limit=100,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

    # -----------------------------------------------------

    def get_scan_history_by_symbol(
        self,
        symbol,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM scan_history
            WHERE symbol=?
            ORDER BY id DESC
            """,
            (
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def delete_scan_history(
        self,
        history_id,
    ):

        self.execute(
            """
            DELETE
            FROM scan_history
            WHERE id=?
            """,
            (
                history_id,
            ),
        )

    # -----------------------------------------------------

    def clear_scan_history(self):

        self.execute(
            "DELETE FROM scan_history"
        )

    # -----------------------------------------------------

    def bulk_insert_scan_history(
        self,
        rows,
    ):

        with self.cursor() as cur:

            cur.executemany(
                """
                INSERT INTO scan_history(

                    symbol,
                    scan_type,
                    signal,
                    ai_score,
                    confidence,
                    entry_price,
                    stop_loss,
                    target_price,
                    rr,
                    timeframe,
                    sector,
                    strategy,
                    remarks,
                    created_at

                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                rows,
            )

    # =====================================================
    # SCAN PROFILE CRUD
    # =====================================================

    def save_scan_profile(
        self,
        profile_name,
        settings,
        scan_type="Custom",
    ):

        now = datetime.now().isoformat()

        self.execute(
            """
            INSERT OR REPLACE
            INTO scan_profiles(

                profile_name,
                scan_type,
                settings_json,
                created_at,
                updated_at

            )
            VALUES(
                ?,
                ?,
                ?,
                COALESCE(
                    (
                        SELECT created_at
                        FROM scan_profiles
                        WHERE profile_name=?
                    ),
                    ?
                ),
                ?
            )
            """,
            (
                profile_name,
                scan_type,
                json.dumps(settings),
                profile_name,
                now,
                now,
            ),
        )

    # -----------------------------------------------------

    def get_scan_profiles(self):

        rows = self.fetchall(
            """
            SELECT *
            FROM scan_profiles
            ORDER BY profile_name
            """
        )

        for row in rows:

            row["settings_json"] = json.loads(
                row["settings_json"]
            )

        return rows

    # -----------------------------------------------------

    def load_scan_profile(
        self,
        profile_name,
    ):

        row = self.fetchone(
            """
            SELECT *
            FROM scan_profiles
            WHERE profile_name=?
            """,
            (
                profile_name,
            ),
        )

        if row:

            row["settings_json"] = json.loads(
                row["settings_json"]
            )

        return row

    # -----------------------------------------------------

    def delete_scan_profile(
        self,
        profile_name,
    ):

        self.execute(
            """
            DELETE
            FROM scan_profiles
            WHERE profile_name=?
            """,
            (
                profile_name,
            ),
        )

    # =====================================================
    # FAVORITES CRUD
    # =====================================================

    def add_favorite(
        self,
        symbol,
        company_name="",
        sector="",
        notes="",
    ):

        self.execute(
            """
            INSERT OR IGNORE
            INTO favorites(

                symbol,
                company_name,
                sector,
                notes,
                created_at

            )
            VALUES(?,?,?,?,?)
            """,
            (
                symbol.upper(),
                company_name,
                sector,
                notes,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def update_favorite_notes(
        self,
        symbol,
        notes,
    ):

        self.execute(
            """
            UPDATE favorites
            SET notes=?
            WHERE symbol=?
            """,
            (
                notes,
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def favorite_exists(
        self,
        symbol,
    ):

        row = self.fetchone(
            """
            SELECT id
            FROM favorites
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

        return row is not None

    # -----------------------------------------------------

    def get_favorites(self):

        return self.fetchall(
            """
            SELECT *
            FROM favorites
            ORDER BY symbol
            """
        )

    # -----------------------------------------------------

    def search_favorites(
        self,
        keyword,
    ):

        keyword = f"%{keyword}%"

        return self.fetchall(
            """
            SELECT *
            FROM favorites
            WHERE symbol LIKE ?
               OR company_name LIKE ?
               OR sector LIKE ?
            ORDER BY symbol
            """,
            (
                keyword,
                keyword,
                keyword,
            ),
        )

    # -----------------------------------------------------

    def remove_favorite(
        self,
        symbol,
    ):

        self.execute(
            """
            DELETE
            FROM favorites
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def clear_favorites(self):

        self.execute(
            "DELETE FROM favorites"
        )

    # -----------------------------------------------------

    def favorite_count(self):

        row = self.fetchone(
            """
            SELECT COUNT(*) AS total
            FROM favorites
            """
        )

        return row["total"]
        # =====================================================
    # PORTFOLIO CRUD
    # =====================================================

    def add_portfolio_position(
        self,
        symbol,
        quantity,
        buy_price,
        current_price=None,
        target_price=None,
        stop_loss=None,
        ai_score=0,
        sector="",
    ):

        symbol = symbol.upper()

        if current_price is None:
            current_price = buy_price

        investment = quantity * buy_price
        current_value = quantity * current_price

        pnl = current_value - investment

        pnl_percent = (
            (pnl / investment) * 100
            if investment
            else 0
        )

        now = datetime.now().isoformat()

        self.execute(
            """
            INSERT INTO portfolio(

                symbol,
                quantity,
                buy_price,
                current_price,
                average_price,
                target_price,
                stop_loss,
                investment,
                current_value,
                pnl,
                pnl_percent,
                ai_score,
                sector,
                created_at,
                updated_at

            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                symbol,
                quantity,
                buy_price,
                current_price,
                buy_price,
                target_price,
                stop_loss,
                investment,
                current_value,
                pnl,
                pnl_percent,
                ai_score,
                sector,
                now,
                now,
            ),
        )

    # -----------------------------------------------------

    def update_portfolio_price(
        self,
        symbol,
        current_price,
    ):

        position = self.fetchone(
            """
            SELECT *
            FROM portfolio
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

        if not position:
            return False

        quantity = position["quantity"]
        investment = position["investment"]

        current_value = quantity * current_price

        pnl = current_value - investment

        pnl_percent = (
            (pnl / investment) * 100
            if investment
            else 0
        )

        self.execute(
            """
            UPDATE portfolio
            SET

                current_price=?,
                current_value=?,
                pnl=?,
                pnl_percent=?,
                updated_at=?

            WHERE symbol=?
            """,
            (
                current_price,
                current_value,
                pnl,
                pnl_percent,
                datetime.now().isoformat(),
                symbol.upper(),
            ),
        )

        return True

    # -----------------------------------------------------

    def get_portfolio(self):

        return self.fetchall(
            """
            SELECT *
            FROM portfolio
            ORDER BY symbol
            """
        )

    # -----------------------------------------------------

    def get_portfolio_position(
        self,
        symbol,
    ):

        return self.fetchone(
            """
            SELECT *
            FROM portfolio
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def delete_portfolio_position(
        self,
        symbol,
    ):

        self.execute(
            """
            DELETE
            FROM portfolio
            WHERE symbol=?
            """,
            (
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def clear_portfolio(self):

        self.execute(
            "DELETE FROM portfolio"
        )

    # =====================================================
    # PORTFOLIO SUMMARY
    # =====================================================

    def portfolio_summary(self):

        rows = self.get_portfolio()

        investment = sum(
            row["investment"]
            for row in rows
        )

        current_value = sum(
            row["current_value"]
            for row in rows
        )

        pnl = current_value - investment

        pnl_percent = (
            (pnl / investment) * 100
            if investment
            else 0
        )

        return {

            "positions": len(rows),

            "investment": round(
                investment,
                2,
            ),

            "current_value": round(
                current_value,
                2,
            ),

            "profit_loss": round(
                pnl,
                2,
            ),

            "profit_percent": round(
                pnl_percent,
                2,
            ),

        }

    # =====================================================
    # TRADE JOURNAL
    # =====================================================

    def add_trade(

        self,

        symbol,

        trade_type,

        quantity,

        entry_price,

        exit_price,

        stop_loss,

        target_price,

        emotion="",

        notes="",

        screenshot="",

    ):

        investment = quantity * entry_price

        exit_value = quantity * exit_price

        pnl = exit_value - investment

        risk = abs(
            entry_price - stop_loss
        )

        reward = abs(
            exit_price - entry_price
        )

        rr = (
            reward / risk
            if risk
            else 0
        )

        result = (

            "WIN"

            if pnl > 0

            else "LOSS"

        )

        self.execute(
            """
            INSERT INTO trade_journal(

                symbol,
                trade_type,
                quantity,
                entry_price,
                exit_price,
                stop_loss,
                target_price,
                pnl,
                rr,
                result,
                emotion,
                notes,
                screenshot,
                entry_time,
                exit_time

            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                symbol.upper(),
                trade_type,
                quantity,
                entry_price,
                exit_price,
                stop_loss,
                target_price,
                pnl,
                rr,
                result,
                emotion,
                notes,
                screenshot,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def get_trade_history(
        self,
        limit=100,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM trade_journal
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        )

    # -----------------------------------------------------

    def delete_trade(
        self,
        trade_id,
    ):

        self.execute(
            """
            DELETE
            FROM trade_journal
            WHERE id=?
            """,
            (
                trade_id,
            ),
        )

    # -----------------------------------------------------

    def clear_trade_history(self):

        self.execute(
            "DELETE FROM trade_journal"
        )

    # =====================================================
    # TRADE STATISTICS
    # =====================================================

    def trade_statistics(self):

        trades = self.get_trade_history(
            limit=100000
        )

        if not trades:

            return {

                "total": 0,

            }

        wins = [

            t

            for t in trades

            if t["result"] == "WIN"

        ]

        losses = [

            t

            for t in trades

            if t["result"] == "LOSS"

        ]

        total_pnl = sum(

            t["pnl"]

            for t in trades

        )

        average_rr = (

            sum(

                t["rr"]

                for t in trades

            )

            / len(trades)

        )

        return {

            "total_trades":

                len(trades),

            "wins":

                len(wins),

            "losses":

                len(losses),

            "win_rate":

                round(

                    len(wins)

                    * 100

                    / len(trades),

                    2,

                ),

            "total_pnl":

                round(

                    total_pnl,

                    2,

                ),

            "average_rr":

                round(

                    average_rr,

                    2,

                ),

        }
        # =====================================================
    # AI HISTORY CRUD
    # =====================================================

    def add_ai_history(
        self,
        symbol,
        ai_score,
        confidence,
        signal,
        recommendation="",
        reason="",
        timeframe="",
    ):

        self.execute(
            """
            INSERT INTO ai_history(

                symbol,
                ai_score,
                confidence,
                signal,
                recommendation,
                reason,
                timeframe,
                created_at

            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                symbol.upper(),
                ai_score,
                confidence,
                signal,
                recommendation,
                reason,
                timeframe,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def get_ai_history(
        self,
        limit=100,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM ai_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        )

    # -----------------------------------------------------

    def get_ai_history_by_symbol(
        self,
        symbol,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM ai_history
            WHERE symbol=?
            ORDER BY id DESC
            """,
            (
                symbol.upper(),
            ),
        )

    # -----------------------------------------------------

    def clear_ai_history(self):

        self.execute(
            "DELETE FROM ai_history"
        )

    # =====================================================
    # ALERTS CRUD
    # =====================================================

    def add_alert(
        self,
        symbol,
        alert_type,
        condition,
        trigger_price,
        status="ACTIVE",
        message="",
    ):

        self.execute(
            """
            INSERT INTO alerts(

                symbol,
                alert_type,
                condition,
                trigger_price,
                status,
                message,
                created_at

            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                symbol.upper(),
                alert_type,
                condition,
                trigger_price,
                status,
                message,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def update_alert_status(
        self,
        alert_id,
        status,
    ):

        triggered = None

        if status.upper() == "TRIGGERED":
            triggered = datetime.now().isoformat()

        self.execute(
            """
            UPDATE alerts
            SET

                status=?,
                triggered_at=?

            WHERE id=?
            """,
            (
                status,
                triggered,
                alert_id,
            ),
        )

    # -----------------------------------------------------

    def get_alerts(
        self,
        status=None,
    ):

        if status:

            return self.fetchall(
                """
                SELECT *
                FROM alerts
                WHERE status=?
                ORDER BY id DESC
                """,
                (
                    status,
                ),
            )

        return self.fetchall(
            """
            SELECT *
            FROM alerts
            ORDER BY id DESC
            """
        )

    # -----------------------------------------------------

    def delete_alert(
        self,
        alert_id,
    ):

        self.execute(
            """
            DELETE
            FROM alerts
            WHERE id=?
            """,
            (
                alert_id,
            ),
        )

    # -----------------------------------------------------

    def clear_alerts(self):

        self.execute(
            "DELETE FROM alerts"
        )

    # =====================================================
    # MARKET SNAPSHOT
    # =====================================================

    def save_market_snapshot(
        self,
        data,
    ):

        self.execute(
            """
            INSERT INTO market_snapshot(

                nifty,
                banknifty,
                finnifty,
                midcap,
                sensex,
                india_vix,
                pcr,
                fii,
                dii,
                advances,
                declines,
                sentiment,
                created_at

            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                data.get("nifty"),
                data.get("banknifty"),
                data.get("finnifty"),
                data.get("midcap"),
                data.get("sensex"),
                data.get("india_vix"),
                data.get("pcr"),
                data.get("fii"),
                data.get("dii"),
                data.get("advances"),
                data.get("declines"),
                data.get("sentiment"),
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def latest_market_snapshot(self):

        return self.fetchone(
            """
            SELECT *
            FROM market_snapshot
            ORDER BY id DESC
            LIMIT 1
            """
        )

    # -----------------------------------------------------

    def market_snapshot_history(
        self,
        limit=100,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM market_snapshot
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        )

    # -----------------------------------------------------

    def clear_market_snapshot(self):

        self.execute(
            "DELETE FROM market_snapshot"
        )

    # =====================================================
    # SETTINGS CRUD
    # =====================================================

    def set_setting(
        self,
        key,
        value,
    ):

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        self.execute(
            """
            INSERT OR REPLACE
            INTO settings(

                setting_key,
                setting_value,
                updated_at

            )
            VALUES(?,?,?)
            """,
            (
                key,
                value,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def get_setting(
        self,
        key,
        default=None,
    ):

        row = self.fetchone(
            """
            SELECT setting_value
            FROM settings
            WHERE setting_key=?
            """,
            (
                key,
            ),
        )

        if not row:
            return default

        value = row["setting_value"]

        try:
            return json.loads(value)
        except Exception:
            return value

    # -----------------------------------------------------

    def get_all_settings(self):

        rows = self.fetchall(
            """
            SELECT *
            FROM settings
            ORDER BY setting_key
            """
        )

        settings = {}

        for row in rows:

            value = row["setting_value"]

            try:
                value = json.loads(value)
            except Exception:
                pass

            settings[row["setting_key"]] = value

        return settings

    # -----------------------------------------------------

    def delete_setting(
        self,
        key,
    ):

        self.execute(
            """
            DELETE
            FROM settings
            WHERE setting_key=?
            """,
            (
                key,
            ),
        )

    # -----------------------------------------------------

    def clear_settings(self):

        self.execute(
            "DELETE FROM settings"
        )

    # =====================================================
    # BULK INSERT UTILITIES
    # =====================================================

    def bulk_insert_ai_history(
        self,
        rows,
    ):

        with self.cursor() as cur:

            cur.executemany(
                """
                INSERT INTO ai_history(

                    symbol,
                    ai_score,
                    confidence,
                    signal,
                    recommendation,
                    reason,
                    timeframe,
                    created_at

                )
                VALUES(?,?,?,?,?,?,?,?)
                """,
                rows,
            )

    # -----------------------------------------------------

    def bulk_insert_market_snapshot(
        self,
        rows,
    ):

        with self.cursor() as cur:

            cur.executemany(
                """
                INSERT INTO market_snapshot(

                    nifty,
                    banknifty,
                    finnifty,
                    midcap,
                    sensex,
                    india_vix,
                    pcr,
                    fii,
                    dii,
                    advances,
                    declines,
                    sentiment,
                    created_at

                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                rows,
            )
                # =====================================================
    # SEARCH UTILITIES
    # =====================================================

    def search_scan_history(
        self,
        keyword,
        limit=100,
    ):

        keyword = f"%{keyword.upper()}%"

        return self.fetchall(
            """
            SELECT *
            FROM scan_history
            WHERE UPPER(symbol) LIKE ?
               OR UPPER(scan_type) LIKE ?
               OR UPPER(signal) LIKE ?
               OR UPPER(strategy) LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                limit,
            ),
        )

    # -----------------------------------------------------

    def search_portfolio(
        self,
        keyword,
    ):

        keyword = f"%{keyword.upper()}%"

        return self.fetchall(
            """
            SELECT *
            FROM portfolio
            WHERE UPPER(symbol) LIKE ?
               OR UPPER(sector) LIKE ?
            ORDER BY symbol
            """,
            (
                keyword,
                keyword,
            ),
        )

    # -----------------------------------------------------

    def search_trade_journal(
        self,
        keyword,
    ):

        keyword = f"%{keyword.upper()}%"

        return self.fetchall(
            """
            SELECT *
            FROM trade_journal
            WHERE UPPER(symbol) LIKE ?
               OR UPPER(notes) LIKE ?
               OR UPPER(emotion) LIKE ?
            ORDER BY entry_time DESC
            """,
            (
                keyword,
                keyword,
                keyword,
            ),
        )

    # =====================================================
    # PAGINATION
    # =====================================================

    def paginate(
        self,
        table,
        page=1,
        page_size=50,
        order_by="id DESC",
    ):

        offset = max(
            page - 1,
            0,
        ) * page_size

        query = f"""
            SELECT *
            FROM {table}
            ORDER BY {order_by}
            LIMIT ?
            OFFSET ?
        """

        return self.fetchall(
            query,
            (
                page_size,
                offset,
            ),
        )

    # =====================================================
    # TABLE COUNTS
    # =====================================================

    def table_count(
        self,
        table,
    ):

        row = self.fetchone(
            f"""
            SELECT COUNT(*) AS total
            FROM {table}
            """
        )

        return row["total"]

    # -----------------------------------------------------

    def all_table_counts(self):

        tables = [

            "scan_history",
            "scan_profiles",
            "favorites",
            "portfolio",
            "trade_journal",
            "ai_history",
            "alerts",
            "market_snapshot",
            "settings",

        ]

        result = {}

        for table in tables:

            result[table] = self.table_count(
                table
            )

        return result

    # =====================================================
    # DATABASE STATISTICS
    # =====================================================

    def database_statistics(self):

        counts = self.all_table_counts()

        total_records = sum(
            counts.values()
        )

        return {

            "database": self.DATABASE_NAME,

            "version": self.database_version(),

            "path": str(
                self.database_path
            ),

            "size_mb": self.size_mb(),

            "tables": counts,

            "total_records": total_records,

            "generated": datetime.now(),

        }

    # =====================================================
    # EXPORT TABLE
    # =====================================================

    def export_table(
        self,
        table,
    ):

        return self.fetchall(
            f"""
            SELECT *
            FROM {table}
            """
        )

    # =====================================================
    # IMPORT TABLE
    # =====================================================

    def import_table(
        self,
        table,
        rows,
    ):

        if not rows:

            return 0

        columns = list(
            rows[0].keys()
        )

        placeholders = ",".join(
            "?"
            for _ in columns
        )

        sql = f"""
            INSERT INTO {table}
            (
                {",".join(columns)}
            )
            VALUES
            (
                {placeholders}
            )
        """

        with self.cursor() as cur:

            cur.executemany(

                sql,

                [

                    tuple(

                        row[col]

                        for col in columns

                    )

                    for row in rows

                ],

            )

        return len(rows)

    # =====================================================
    # DATABASE INTEGRITY
    # =====================================================

    def integrity_check(self):

        row = self.fetchone(

            "PRAGMA integrity_check"

        )

        if not row:

            return False

        value = list(

            row.values()

        )[0]

        return value == "ok"

    # =====================================================
    # OPTIMIZE
    # =====================================================

    def optimize_database(self):

        self.execute(
            "VACUUM"
        )

        self.execute(
            "ANALYZE"
        )

        return True

    # =====================================================
    # CLEAN OLD DATA
    # =====================================================

    def cleanup_old_data(
        self,
        days=365,
    ):

        cutoff = datetime.now().timestamp()

        cutoff -= (

            days
            * 24
            * 60
            * 60

        )

        cutoff = datetime.fromtimestamp(
            cutoff
        ).isoformat()

        tables = [

            "scan_history",
            "ai_history",
            "market_snapshot",

        ]

        for table in tables:

            self.execute(
                f"""
                DELETE
                FROM {table}
                WHERE created_at < ?
                """,
                (
                    cutoff,
                ),
            )

    # =====================================================
    # RESET DATABASE
    # =====================================================

    def reset_database(self):

        tables = [

            "scan_history",
            "scan_profiles",
            "favorites",
            "portfolio",
            "trade_journal",
            "ai_history",
            "alerts",
            "market_snapshot",
            "settings",

        ]

        for table in tables:

            self.execute(
                f"DELETE FROM {table}"
            )

        self.save_database_version()

    # =====================================================
    # DATABASE HEALTH
    # =====================================================

    def health_check(self):

        return {

            "database_exists":

                self.exists(),

            "connected":

                self.connection
                is not None,

            "integrity":

                self.integrity_check(),

            "version":

                self.database_version(),

            "size_mb":

                self.size_mb(),

            "overall":

                self.exists()
                and self.connection
                is not None
                and self.integrity_check(),

        }
        # =====================================================
    # TRANSACTION MANAGEMENT
    # =====================================================

    @contextmanager
    def transaction(self):

        with self._lock:

            try:

                yield self.connection

                self.connection.commit()

            except Exception:

                self.connection.rollback()

                raise

    # -----------------------------------------------------

    def begin_transaction(self):

        self.connection.execute("BEGIN")

    # -----------------------------------------------------

    def commit(self):

        self.connection.commit()

    # -----------------------------------------------------

    def rollback(self):

        self.connection.rollback()

    # =====================================================
    # AUDIT LOG
    # =====================================================

    def create_audit_log_table(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                action TEXT,

                table_name TEXT,

                record_id TEXT,

                description TEXT,

                created_at TEXT

            )
            """
        )

    # -----------------------------------------------------

    def log_action(

        self,

        action,

        table_name,

        record_id="",

        description="",

    ):

        self.execute(
            """
            INSERT INTO audit_log(

                action,
                table_name,
                record_id,
                description,
                created_at

            )
            VALUES(?,?,?,?,?)
            """,
            (
                action,
                table_name,
                str(record_id),
                description,
                datetime.now().isoformat(),
            ),
        )

    # -----------------------------------------------------

    def audit_history(
        self,
        limit=500,
    ):

        return self.fetchall(
            """
            SELECT *
            FROM audit_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                limit,
            ),
        )

    # -----------------------------------------------------

    def clear_audit_log(self):

        self.execute(
            "DELETE FROM audit_log"
        )

    # =====================================================
    # DATABASE MIGRATIONS
    # =====================================================

    def migrate(self):

        version = self.database_version()

        if version == self.DATABASE_VERSION:
            return

        migrations = {

            "4.0": self._migration_40,

        }

        migration = migrations.get(
            self.DATABASE_VERSION
        )

        if migration:

            migration()

            self.save_database_version()

    # -----------------------------------------------------

    def _migration_40(self):

        self.create_metadata_table()

        self.create_scan_history_table()

        self.create_scan_profiles_table()

        self.create_favorites_table()

        self.create_portfolio_table()

        self.create_trade_journal_table()

        self.create_ai_history_table()

        self.create_alerts_table()

        self.create_market_snapshot_table()

        self.create_settings_table()

        self.create_audit_log_table()

    # =====================================================
    # SCHEMA VERSION
    # =====================================================

    def schema_version(self):

        return self.database_version()

    # -----------------------------------------------------

    def upgrade_database(self):

        self.migrate()

        self.optimize_database()

        return True

    # =====================================================
    # AUTOMATIC BACKUP
    # =====================================================

    def auto_backup(

        self,

        folder="backups",

    ):

        folder = Path(folder)

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = datetime.now().strftime(
            "stockversity_%Y%m%d_%H%M%S.db"
        )

        backup_path = folder / filename

        shutil.copy2(
            self.database_path,
            backup_path,
        )

        return backup_path

    # -----------------------------------------------------

    def latest_backup(

        self,

        folder="backups",

    ):

        folder = Path(folder)

        if not folder.exists():

            return None

        backups = sorted(

            folder.glob("*.db"),

            reverse=True,

        )

        if backups:

            return backups[0]

        return None

    # -----------------------------------------------------

    def restore_latest_backup(

        self,

        folder="backups",

    ):

        latest = self.latest_backup(folder)

        if latest is None:

            return False

        self.close()

        shutil.copy2(

            latest,

            self.database_path,

        )

        self.connect()

        return True

    # =====================================================
    # BACKUP MANAGEMENT
    # =====================================================

    def backup_count(

        self,

        folder="backups",

    ):

        folder = Path(folder)

        if not folder.exists():

            return 0

        return len(
            list(
                folder.glob("*.db")
            )
        )

    # -----------------------------------------------------

    def cleanup_backups(

        self,

        keep_last=20,

        folder="backups",

    ):

        folder = Path(folder)

        if not folder.exists():

            return

        backups = sorted(

            folder.glob("*.db"),

            reverse=True,

        )

        for backup in backups[keep_last:]:

            backup.unlink(
                missing_ok=True
            )

    # =====================================================
    # THREAD SAFE BULK EXECUTION
    # =====================================================

    def execute_many(

        self,

        sql,

        rows,

    ):

        with self.cursor() as cur:

            cur.executemany(

                sql,

                rows,

            )

    # =====================================================
    # SQL SCRIPT
    # =====================================================

    def execute_script(

        self,

        script,

    ):

        with self.cursor() as cur:

            cur.executescript(script)

    # =====================================================
    # LAST INSERT ID
    # =====================================================

    def last_insert_id(self):

        row = self.fetchone(

            "SELECT last_insert_rowid() AS id"

        )

        return row["id"]
        # =====================================================
    # PERFORMANCE MONITORING
    # =====================================================

    def initialize_performance_monitor(self):

        self._query_count = 0
        self._total_query_time = 0.0
        self._last_query_time = 0.0
        self._cache = {}
        self._hooks = []

    # -----------------------------------------------------

    def record_query_time(self, elapsed_seconds):

        self._query_count += 1
        self._last_query_time = elapsed_seconds
        self._total_query_time += elapsed_seconds

    # -----------------------------------------------------

    def performance_statistics(self):

        average = (
            self._total_query_time / self._query_count
            if self._query_count
            else 0
        )

        return {

            "query_count": self._query_count,

            "last_query_ms": round(
                self._last_query_time * 1000,
                3,
            ),

            "average_query_ms": round(
                average * 1000,
                3,
            ),

            "total_query_time": round(
                self._total_query_time,
                3,
            ),

        }

    # =====================================================
    # CACHE
    # =====================================================

    def cache_set(
        self,
        key,
        value,
    ):

        self._cache[key] = value

    # -----------------------------------------------------

    def cache_get(
        self,
        key,
        default=None,
    ):

        return self._cache.get(
            key,
            default,
        )

    # -----------------------------------------------------

    def cache_exists(
        self,
        key,
    ):

        return key in self._cache

    # -----------------------------------------------------

    def cache_remove(
        self,
        key,
    ):

        self._cache.pop(
            key,
            None,
        )

    # -----------------------------------------------------

    def clear_cache(self):

        self._cache.clear()

    # -----------------------------------------------------

    def cache_size(self):

        return len(self._cache)

    # =====================================================
    # EVENT HOOKS
    # =====================================================

    def register_hook(
        self,
        callback,
    ):

        if callback not in self._hooks:
            self._hooks.append(callback)

    # -----------------------------------------------------

    def unregister_hook(
        self,
        callback,
    ):

        if callback in self._hooks:
            self._hooks.remove(callback)

    # -----------------------------------------------------

    def notify_hooks(
        self,
        event,
        **kwargs,
    ):

        for hook in list(self._hooks):

            try:

                hook(
                    event,
                    **kwargs,
                )

            except Exception:

                pass

    # =====================================================
    # DATA VALIDATION
    # =====================================================

    def validate_symbol(
        self,
        symbol,
    ):

        if not symbol:
            return False

        symbol = symbol.strip().upper()

        if len(symbol) > 30:
            return False

        allowed = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
            "-&_"
        )

        return all(
            c in allowed
            for c in symbol
        )

    # -----------------------------------------------------

    def validate_price(
        self,
        price,
    ):

        try:

            value = float(price)

            return value >= 0

        except Exception:

            return False

    # -----------------------------------------------------

    def validate_quantity(
        self,
        quantity,
    ):

        try:

            return int(quantity) > 0

        except Exception:

            return False

    # -----------------------------------------------------

    def validate_percentage(
        self,
        value,
    ):

        try:

            value = float(value)

            return -100 <= value <= 1000

        except Exception:

            return False

    # =====================================================
    # MAINTENANCE
    # =====================================================

    def perform_maintenance(self):

        self.cleanup_old_data()

        self.cleanup_backups()

        self.optimize_database()

        self.clear_cache()

        return True

    # -----------------------------------------------------

    def maintenance_report(self):

        return {

            "database_ok": self.integrity_check(),

            "database_size_mb": self.size_mb(),

            "backup_count": self.backup_count(),

            "cache_items": self.cache_size(),

            "statistics": self.performance_statistics(),

        }

    # =====================================================
    # CONNECTION DIAGNOSTICS
    # =====================================================

    def connection_information(self):

        return {

            "connected": self.connection is not None,

            "database": str(self.database_path),

            "sqlite_version": sqlite3.sqlite_version,

            "thread_safe": sqlite3.threadsafety,

        }

    # -----------------------------------------------------

    def ping(self):

        try:

            self.fetchone(
                "SELECT 1"
            )

            return True

        except Exception:

            return False

    # =====================================================
    # TABLE EXISTS
    # =====================================================

    def table_exists(
        self,
        table_name,
    ):

        row = self.fetchone(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name=?
            """,
            (
                table_name,
            ),
        )

        return row is not None

    # =====================================================
    # DATABASE READY
    # =====================================================

    def is_ready(self):

        return (

            self.exists()

            and self.connection is not None

            and self.integrity_check()

        )

    # =====================================================
    # APPLICATION STARTUP
    # =====================================================

    def startup(self):

        self.connect()

        self.initialize_database()

        self.initialize_performance_monitor()

        self.migrate()

        return self.is_ready()

    # =====================================================
    # APPLICATION SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.auto_backup()

        self.close()

        return True
        # =====================================================
    # GENERIC INSERT
    # =====================================================

    def insert(
        self,
        table,
        data,
    ):

        columns = list(data.keys())

        placeholders = ",".join(
            ["?"] * len(columns)
        )

        sql = f"""
            INSERT INTO {table}
            ({",".join(columns)})
            VALUES ({placeholders})
        """

        self.execute(
            sql,
            tuple(data.values()),
        )

        return self.last_insert_id()

    # =====================================================
    # GENERIC UPDATE
    # =====================================================

    def update(
        self,
        table,
        data,
        where,
        params,
    ):

        assignments = ", ".join(
            f"{column}=?"
            for column in data.keys()
        )

        sql = f"""
            UPDATE {table}
            SET {assignments}
            WHERE {where}
        """

        self.execute(
            sql,
            tuple(data.values()) + tuple(params),
        )

    # =====================================================
    # GENERIC DELETE
    # =====================================================

    def delete(
        self,
        table,
        where,
        params=(),
    ):

        sql = f"""
            DELETE
            FROM {table}
            WHERE {where}
        """

        self.execute(
            sql,
            params,
        )

    # =====================================================
    # GENERIC SELECT
    # =====================================================

    def select(
        self,
        table,
        columns="*",
        where=None,
        params=(),
        order_by=None,
        limit=None,
    ):

        sql = f"SELECT {columns} FROM {table}"

        if where:
            sql += f" WHERE {where}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql += f" LIMIT {int(limit)}"

        return self.fetchall(
            sql,
            params,
        )

    # =====================================================
    # BATCH UPDATE
    # =====================================================

    def batch_update(
        self,
        sql,
        rows,
    ):

        with self.transaction():

            self.execute_many(
                sql,
                rows,
            )

        return len(rows)

    # =====================================================
    # BATCH DELETE
    # =====================================================

    def batch_delete(
        self,
        table,
        ids,
    ):

        if not ids:
            return 0

        placeholders = ",".join(
            ["?"] * len(ids)
        )

        sql = f"""
            DELETE
            FROM {table}
            WHERE id IN ({placeholders})
        """

        self.execute(
            sql,
            tuple(ids),
        )

        return len(ids)

    # =====================================================
    # SORTING
    # =====================================================

    def sorted_rows(
        self,
        table,
        column,
        ascending=True,
    ):

        order = "ASC" if ascending else "DESC"

        return self.fetchall(
            f"""
            SELECT *
            FROM {table}
            ORDER BY {column} {order}
            """
        )

    # =====================================================
    # FILTERING
    # =====================================================

    def filter_rows(
        self,
        table,
        filters,
    ):

        if not filters:

            return self.select(table)

        clauses = []
        values = []

        for key, value in filters.items():

            clauses.append(
                f"{key}=?"
            )

            values.append(value)

        sql = f"""
            SELECT *
            FROM {table}
            WHERE {' AND '.join(clauses)}
            """

        return self.fetchall(
            sql,
            tuple(values),
        )

    # =====================================================
    # JSON EXPORT
    # =====================================================

    def export_json(
        self,
        table,
    ):

        rows = self.export_table(
            table
        )

        return json.dumps(
            rows,
            indent=4,
            default=str,
        )

    # =====================================================
    # JSON IMPORT
    # =====================================================

    def import_json(
        self,
        table,
        json_data,
    ):

        rows = json.loads(
            json_data
        )

        return self.import_table(
            table,
            rows,
        )

    # =====================================================
    # CSV EXPORT
    # =====================================================

    def export_csv(
        self,
        table,
        filename,
    ):

        import csv

        rows = self.export_table(
            table
        )

        if not rows:
            return False

        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=rows[0].keys(),
            )

            writer.writeheader()

            writer.writerows(rows)

        return True

    # =====================================================
    # ERROR LOGGING
    # =====================================================

    def log_error(
        self,
        message,
        exception=None,
    ):

        try:

            self.log_action(

                action="ERROR",

                table_name="SYSTEM",

                description=f"{message} | {exception}",

            )

        except Exception:

            pass

    # =====================================================
    # DATABASE EVENTS
    # =====================================================

    def record_event(
        self,
        event,
        details="",
    ):

        self.notify_hooks(

            event,

            details=details,

            timestamp=datetime.now(),

        )

    # =====================================================
    # LAST BACKUP TIME
    # =====================================================

    def last_backup_time(
        self,
        folder="backups",
    ):

        backup = self.latest_backup(
            folder
        )

        if backup is None:

            return None

        return datetime.fromtimestamp(
            backup.stat().st_mtime
        )

    # =====================================================
    # LAST MAINTENANCE TIME
    # =====================================================

    def update_maintenance_time(self):

        self.set_setting(

            "last_maintenance",

            datetime.now().isoformat(),

        )

    # -----------------------------------------------------

    def last_maintenance_time(self):

        return self.get_setting(
            "last_maintenance"
        )

    # =====================================================
    # DATABASE SUMMARY
    # =====================================================

    def summary(self):

        return {

            "version": self.database_version(),

            "health": self.health_check(),

            "statistics": self.database_statistics(),

            "performance": self.performance_statistics(),

            "maintenance": self.last_maintenance_time(),

            "backup": self.last_backup_time(),

        }
    # =====================================================
# CONTEXT MANAGER SUPPORT
# =====================================================

    def __enter__(self):

        if self.connection is None:
            self.connect()

        return self

    # -----------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        if exc_type is not None:

            try:
                self.rollback()
            except Exception:
                pass

        self.close()

        return False

    # =====================================================
    # DESTRUCTOR
    # =====================================================

    def __del__(self):

        try:

            if getattr(self, "connection", None):

                self.close()

        except Exception:

            pass

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<DatabaseManager "
            f"database='{self.DATABASE_NAME}' "
            f"version='{self.database_version()}'>"
        )

    # -----------------------------------------------------

    def __str__(self):

        return (
            f"DatabaseManager("
            f"{self.database_path})"
        )

    # =====================================================
    # APPLICATION INFORMATION
    # =====================================================

    def application_info(self):

        return {

            "application": "StockVersity Scanner Pro",

            "version": "4.0",

            "database": self.DATABASE_NAME,

            "database_version": self.database_version(),

            "database_path": str(self.database_path),

            "database_size_mb": self.size_mb(),

            "tables": self.tables(),

            "ready": self.is_ready(),

            "performance": self.performance_statistics(),

        }

    # =====================================================
    # SYSTEM STATUS
    # =====================================================

    def system_status(self):

        return {

            "database": self.health_check(),

            "performance": self.performance_statistics(),

            "maintenance": self.maintenance_report(),

            "summary": self.summary(),

        }


# =====================================================
# SINGLETON INSTANCE
# =====================================================

_database_manager = None


def get_database():

    """
    Returns the shared DatabaseManager instance.
    """

    global _database_manager

    if _database_manager is None:

        _database_manager = DatabaseManager()

        _database_manager.startup()

    return _database_manager


# =====================================================
# FACTORY
# =====================================================

def create_database():

    """
    Create a new independent DatabaseManager.
    """

    db = DatabaseManager()

    db.startup()

    return db


# =====================================================
# SHUTDOWN HELPER
# =====================================================

def shutdown_database():

    global _database_manager

    if _database_manager is not None:

        _database_manager.shutdown()

        _database_manager = None


# =====================================================
# INITIALIZATION
# =====================================================

try:

    database = get_database()

except Exception:

    database = None


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "DatabaseManager",

    "database",

    "get_database",

    "create_database",

    "shutdown_database",

]
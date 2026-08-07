"""
=========================================================
StockVersity Scanner Pro
Market Feed Pipeline
Version : 2.0
=========================================================

Purpose
-------

Central pipeline connecting:

Upstox WebSocket
        ↓
MarketDataParser
        ↓
MarketFeedPipeline
        ↓
LiveFeedConnector
        ↓
ScannerMarketBridge
        ↓
ScannerEngine
        ↓
Trading Signals

=========================================================
"""

from __future__ import annotations

from datetime import datetime

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

from core.scanner.signal import Signal
from core.scanner.live_feed_connector import LiveFeedConnector


# =========================================================
# MARKET FEED PIPELINE
# =========================================================

class MarketFeedPipeline:
    """
    Connect parsed Upstox market data with the scanner
    live-feed system.

    Responsibilities
    ----------------
    • Receive raw websocket messages
    • Pass raw data through MarketDataParser
    • Normalize parser output
    • Forward ticks to LiveFeedConnector
    • Handle single and batch updates
    • Track feed statistics
    • Protect scanner pipeline from malformed packets
    """

    def __init__(
        self,
        parser: Any,
        connector: LiveFeedConnector,
    ) -> None:

        if parser is None:
            raise ValueError(
                "parser cannot be None."
            )

        if not isinstance(
            connector,
            LiveFeedConnector,
        ):
            raise TypeError(
                "connector must be a LiveFeedConnector instance."
            )

        self.parser = parser

        self.connector = connector

        # =================================================
        # STATE
        # =================================================

        self.running = False

        self.enabled = True

        self.debug = False

        # =================================================
        # COUNTERS
        # =================================================

        self.messages_received = 0

        self.messages_parsed = 0

        self.messages_failed = 0

        self.ticks_forwarded = 0

        self.empty_messages = 0

        # =================================================
        # TIMESTAMPS
        # =================================================

        self.started_at: Optional[
            datetime
        ] = None

        self.last_message_at: Optional[
            datetime
        ] = None

        self.last_success_at: Optional[
            datetime
        ] = None

        self.last_error_at: Optional[
            datetime
        ] = None

        # =================================================
        # ERROR STATE
        # =================================================

        self.last_error: Optional[
            str
        ] = None

        # =================================================
        # CALLBACKS
        # =================================================

        self._error_callbacks: List[
            Callable[[str], None]
        ] = []

        self._parsed_callbacks: List[
            Callable[
                [Dict[str, Dict[str, Any]]],
                None,
            ]
        ] = []

    # =====================================================
    # CONFIGURE
    # =====================================================

    def configure(
        self,
        *,
        enabled: Optional[bool] = None,
        debug: Optional[bool] = None,
    ) -> "MarketFeedPipeline":

        if enabled is not None:

            self.enabled = bool(
                enabled
            )

        if debug is not None:

            self.debug = bool(
                debug
            )

        return self

    # =====================================================
    # LOG
    # =====================================================

    def log(
        self,
        *message: Any,
    ) -> None:

        if not self.debug:
            return

        print(
            "[MarketFeedPipeline]",
            *message,
        )

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:

        if self.running:
            return

        self.running = True

        self.started_at = datetime.now()

        if not self.connector.running:

            self.connector.start()

        self.log(
            "Market feed pipeline started."
        )

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
        *,
        flush: bool = True,
    ) -> None:

        if not self.running:
            return

        self.running = False

        self.connector.stop(
            flush=flush
        )

        self.log(
            "Market feed pipeline stopped."
        )

    # =====================================================
    # RAW MESSAGE
    # =====================================================

    def on_message(
        self,
        message: Any,
    ) -> List[Signal]:
        """
        Main websocket entry point.

        Pass the raw websocket packet here.
        """

        if not self.enabled:

            return self.connector.signals

        if not self.running:

            self.start()

        self.messages_received += 1

        self.last_message_at = (
            datetime.now()
        )

        if message is None:

            self.empty_messages += 1

            return self.connector.signals

        try:

            parsed = self._parse_message(
                message
            )

            if not parsed:

                self.empty_messages += 1

                return self.connector.signals

            normalized = (
                self._normalize_parser_output(
                    parsed
                )
            )

            if not normalized:

                self.empty_messages += 1

                return self.connector.signals

            self.messages_parsed += 1

            self.last_success_at = (
                datetime.now()
            )

            self._notify_parsed(
                normalized
            )

            self.ticks_forwarded += len(
                normalized
            )

            return self.connector.on_ticks(
                normalized
            )

        except Exception as exc:

            self.messages_failed += 1

            self._handle_error(
                "Market message processing failed",
                exc,
            )

            return self.connector.signals

    # =====================================================
    # PARSER DISPATCH
    # =====================================================

    def _parse_message(
        self,
        message: Any,
    ) -> Any:
        """
        Supports several common parser method names.

        This allows the pipeline to work with the existing
        StockVersity MarketDataParser without forcing one
        exact parser method name.
        """

        parser_methods = (

            "parse",

            "parse_message",

            "parse_feed",

            "parse_market_data",

            "decode",

            "process",

        )

        for method_name in parser_methods:

            method = getattr(
                self.parser,
                method_name,
                None,
            )

            if callable(method):

                return method(
                    message
                )

        if callable(
            self.parser
        ):

            return self.parser(
                message
            )

        raise AttributeError(
            "MarketDataParser does not provide a supported "
            "parse method. Expected one of: "
            "parse, parse_message, parse_feed, "
            "parse_market_data, decode, process."
        )

    # =====================================================
    # NORMALIZE PARSER OUTPUT
    # =====================================================

    def _normalize_parser_output(
        self,
        parsed: Any,
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:
        """
        Convert parser output into:

        {
            "NSE_EQ|INE002A01018": {
                "instrument_key": "...",
                "symbol": "RELIANCE",
                "ltp": 1400.0,
                ...
            }
        }
        """

        normalized: Dict[
            str,
            Dict[str, Any]
        ] = {}

        if parsed is None:

            return normalized

        # =================================================
        # CASE 1
        # Dictionary keyed by instrument_key
        # =================================================

        if isinstance(
            parsed,
            Mapping,
        ):

            # ---------------------------------------------
            # Single tick dictionary
            # ---------------------------------------------

            instrument_key = (
                parsed.get(
                    "instrument_key"
                )
                or parsed.get(
                    "instrumentKey"
                )
                or parsed.get(
                    "key"
                )
            )

            if instrument_key:

                record = dict(
                    parsed
                )

                record[
                    "instrument_key"
                ] = str(
                    instrument_key
                )

                normalized[
                    str(instrument_key)
                ] = record

                return normalized

            # ---------------------------------------------
            # Common wrapper:
            #
            # {
            #     "feeds": {
            #         instrument_key: {...}
            #     }
            # }
            # ---------------------------------------------

            feeds = parsed.get(
                "feeds"
            )

            if isinstance(
                feeds,
                Mapping,
            ):

                return (
                    self._normalize_mapping(
                        feeds
                    )
                )

            # ---------------------------------------------
            # Common wrapper:
            #
            # {
            #     "data": {
            #         instrument_key: {...}
            #     }
            # }
            # ---------------------------------------------

            data = parsed.get(
                "data"
            )

            if isinstance(
                data,
                Mapping,
            ):

                result = (
                    self._normalize_mapping(
                        data
                    )
                )

                if result:

                    return result

            # ---------------------------------------------
            # Assume mapping itself is instrument map
            # ---------------------------------------------

            result = (
                self._normalize_mapping(
                    parsed
                )
            )

            if result:

                return result

        # =================================================
        # CASE 2
        # List of ticks
        # =================================================

        if isinstance(
            parsed,
            (list, tuple),
        ):

            for item in parsed:

                if not isinstance(
                    item,
                    Mapping,
                ):

                    continue

                instrument_key = (

                    item.get(
                        "instrument_key"
                    )

                    or item.get(
                        "instrumentKey"
                    )

                    or item.get(
                        "key"
                    )

                )

                if not instrument_key:

                    continue

                record = dict(
                    item
                )

                record[
                    "instrument_key"
                ] = str(
                    instrument_key
                )

                normalized[
                    str(instrument_key)
                ] = record

            return normalized

        return normalized

    # =====================================================
    # NORMALIZE MAPPING
    # =====================================================

    def _normalize_mapping(
        self,
        data: Mapping[
            Any,
            Any
        ],
    ) -> Dict[
        str,
        Dict[str, Any]
    ]:

        normalized: Dict[
            str,
            Dict[str, Any]
        ] = {}

        for key, value in data.items():

            if not isinstance(
                value,
                Mapping,
            ):

                continue

            record = dict(
                value
            )

            instrument_key = (

                record.get(
                    "instrument_key"
                )

                or record.get(
                    "instrumentKey"
                )

                or key

            )

            if not instrument_key:

                continue

            instrument_key = str(
                instrument_key
            )

            record[
                "instrument_key"
            ] = instrument_key

            normalized[
                instrument_key
            ] = record

        return normalized

    # =====================================================
    # PARSED DATA DIRECT
    # =====================================================

    def on_parsed_data(
        self,
        parsed: Any,
    ) -> List[Signal]:
        """
        Use this when data has already been parsed.

        This bypasses MarketDataParser.
        """

        if not self.enabled:

            return self.connector.signals

        if not self.running:

            self.start()

        try:

            normalized = (
                self._normalize_parser_output(
                    parsed
                )
            )

            if not normalized:

                return self.connector.signals

            self.ticks_forwarded += len(
                normalized
            )

            self.last_success_at = (
                datetime.now()
            )

            self._notify_parsed(
                normalized
            )

            return self.connector.on_ticks(
                normalized
            )

        except Exception as exc:

            self._handle_error(
                "Parsed market-data forwarding failed",
                exc,
            )

            return self.connector.signals

    # =====================================================
    # FORCE SCAN
    # =====================================================

    def force_scan(
        self,
    ) -> List[Signal]:

        return self.connector.force_scan()

    # =====================================================
    # FLUSH
    # =====================================================

    def flush(
        self,
        *,
        force_scan: bool = True,
    ) -> List[Signal]:

        return self.connector.flush(
            force_scan=force_scan
        )

    # =====================================================
    # ADD ERROR LISTENER
    # =====================================================

    def add_error_listener(
        self,
        callback: Callable[
            [str],
            None,
        ],
    ) -> None:

        if callback not in (
            self._error_callbacks
        ):

            self._error_callbacks.append(
                callback
            )

    # =====================================================
    # ADD PARSED LISTENER
    # =====================================================

    def add_parsed_listener(
        self,
        callback: Callable[
            [Dict[str, Dict[str, Any]]],
            None,
        ],
    ) -> None:

        if callback not in (
            self._parsed_callbacks
        ):

            self._parsed_callbacks.append(
                callback
            )

    # =====================================================
    # NOTIFY PARSED
    # =====================================================

    def _notify_parsed(
        self,
        data: Dict[
            str,
            Dict[str, Any]
        ],
    ) -> None:

        for callback in list(
            self._parsed_callbacks
        ):

            try:

                callback(
                    data
                )

            except Exception as exc:

                self._handle_error(
                    "Parsed-data callback failed",
                    exc,
                )

    # =====================================================
    # ERROR HANDLER
    # =====================================================

    def _handle_error(
        self,
        prefix: str,
        exc: Exception,
    ) -> None:

        self.last_error_at = (
            datetime.now()
        )

        self.last_error = (

            f"{prefix}: "
            f"{type(exc).__name__}: "
            f"{exc}"

        )

        self.log(
            self.last_error
        )

        for callback in list(
            self._error_callbacks
        ):

            try:

                callback(
                    self.last_error
                )

            except Exception:

                pass

    # =====================================================
    # HEALTH
    # =====================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        connector_health = (
            self.connector.feed_health()
        )

        return {

            "healthy": (
                self.enabled
                and self.running
                and connector_health[
                    "healthy"
                ]
            ),

            "pipeline_running":
                self.running,

            "pipeline_enabled":
                self.enabled,

            "messages_received":
                self.messages_received,

            "messages_parsed":
                self.messages_parsed,

            "messages_failed":
                self.messages_failed,

            "ticks_forwarded":
                self.ticks_forwarded,

            "connector":
                connector_health,

            "last_error":
                self.last_error,

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(
        self,
    ) -> Dict[str, Any]:

        return {

            "running":
                self.running,

            "enabled":
                self.enabled,

            "messages_received":
                self.messages_received,

            "messages_parsed":
                self.messages_parsed,

            "messages_failed":
                self.messages_failed,

            "empty_messages":
                self.empty_messages,

            "ticks_forwarded":
                self.ticks_forwarded,

            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),

            "last_message_at": (
                self.last_message_at.isoformat()
                if self.last_message_at
                else None
            ),

            "last_success_at": (
                self.last_success_at.isoformat()
                if self.last_success_at
                else None
            ),

            "last_error_at": (
                self.last_error_at.isoformat()
                if self.last_error_at
                else None
            ),

            "last_error":
                self.last_error,

            "connector":
                self.connector.status(),

        }

    # =====================================================
    # RESET STATISTICS
    # =====================================================

    def reset_statistics(
        self,
    ) -> None:

        self.messages_received = 0

        self.messages_parsed = 0

        self.messages_failed = 0

        self.ticks_forwarded = 0

        self.empty_messages = 0

        self.last_message_at = None

        self.last_success_at = None

        self.last_error_at = None

        self.last_error = None

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"running={self.running}, "

            f"received="
            f"{self.messages_received}, "

            f"parsed="
            f"{self.messages_parsed}, "

            f"forwarded="
            f"{self.ticks_forwarded}"

            f")"

        )

    def __str__(
        self,
    ) -> str:

        return (

            "MarketFeedPipeline | "

            f"{self.messages_received} messages | "

            f"{self.ticks_forwarded} ticks | "

            f"{self.connector.signal_count} signals"

        )


# =========================================================
# FACTORY
# =========================================================

def create_market_feed_pipeline(
    parser: Any,
    connector: LiveFeedConnector,
    *,
    debug: bool = False,
) -> MarketFeedPipeline:

    pipeline = MarketFeedPipeline(

        parser=parser,

        connector=connector,

    )

    pipeline.configure(
        debug=debug
    )

    return pipeline


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "MarketFeedPipeline",

    "create_market_feed_pipeline",

]


# ==========================
# END OF FILE
# ==========================
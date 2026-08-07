"""
=========================================================
STOCKVERSITY SCANNER PRO
UPSTOX WEBSOCKET V3 DIAGNOSTIC TEST
=========================================================

Purpose
-------
1. Check Upstox environment variables
2. Create official Upstox ApiClient
3. Create MarketDataParser
4. Create WebSocketManager
5. Subscribe to NIFTY 50
6. Connect to Upstox MarketDataStreamerV3
7. Print RAW websocket messages
8. Pass RAW messages through MarketDataParser
9. Print parsed Tick objects
10. Show diagnostics
11. Disconnect cleanly

IMPORTANT:
This test DOES NOT place any orders.
=========================================================
"""

from __future__ import annotations

import os
import sys
import time
import threading
import traceback
from pathlib import Path
from typing import Any


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# =========================================================
# IMPORTS
# =========================================================

import upstox_client

from core.market_data.websocket_manager import (
    WebSocketManager,
)

from core.market_data.market_data_parser import (
    MarketDataParser,
)


# =========================================================
# CONFIGURATION
# =========================================================

INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"

MODE = "full"

CONNECTION_TIMEOUT = 15

MESSAGE_WAIT_TIME = 20

MAX_RAW_MESSAGES_TO_PRINT = 5


# =========================================================
# OUTPUT HELPERS
# =========================================================

def heading(text: str) -> None:

    print()
    print("=" * 70)
    print(text)
    print("=" * 70)


def passed(text: str) -> None:

    print(
        f"[PASS] {text}"
    )


def failed(text: str) -> None:

    print(
        f"[FAIL] {text}"
    )


def info(text: str) -> None:

    print(
        f"[INFO] {text}"
    )


def warning(text: str) -> None:

    print(
        f"[WARNING] {text}"
    )


# =========================================================
# SAFE OBJECT DESCRIPTION
# =========================================================

def describe_object(
    obj: Any,
) -> None:
    """
    Print useful information about an incoming Upstox
    websocket message without modifying it.
    """

    print(
        "Python type:",
        type(obj),
    )

    # -----------------------------------------------------
    # DICTIONARY
    # -----------------------------------------------------

    if isinstance(
        obj,
        dict,
    ):

        print(
            "Top-level keys:",
            list(
                obj.keys()
            ),
        )

        print()
        print(
            "RAW DICTIONARY:"
        )

        print(
            repr(obj)
        )

        return

    # -----------------------------------------------------
    # BYTES
    # -----------------------------------------------------

    if isinstance(
        obj,
        bytes,
    ):

        print(
            "Bytes length:",
            len(obj),
        )

        print()
        print(
            "RAW BYTES:"
        )

        print(
            repr(obj[:500])
        )

        return

    # -----------------------------------------------------
    # STRING
    # -----------------------------------------------------

    if isinstance(
        obj,
        str,
    ):

        print(
            "String length:",
            len(obj),
        )

        print()
        print(
            "RAW STRING:"
        )

        print(
            obj[:3000]
        )

        return

    # -----------------------------------------------------
    # OBJECT ATTRIBUTES
    # -----------------------------------------------------

    try:

        attributes = [
            name
            for name in dir(obj)
            if not name.startswith("_")
        ]

        print(
            "Public attributes:",
            attributes[:80],
        )

    except Exception as exc:

        print(
            "Unable to inspect attributes:",
            exc,
        )

    # -----------------------------------------------------
    # to_dict()
    # -----------------------------------------------------

    if hasattr(
        obj,
        "to_dict",
    ):

        try:

            converted = (
                obj.to_dict()
            )

            print()
            print(
                "to_dict() type:",
                type(converted),
            )

            if isinstance(
                converted,
                dict,
            ):

                print(
                    "to_dict() keys:",
                    list(
                        converted.keys()
                    ),
                )

            print()
            print(
                "to_dict() DATA:"
            )

            print(
                repr(converted)
            )

        except Exception as exc:

            print(
                "to_dict() failed:",
                repr(exc),
            )

    # -----------------------------------------------------
    # __dict__
    # -----------------------------------------------------

    if hasattr(
        obj,
        "__dict__",
    ):

        try:

            print()
            print(
                "__dict__:"
            )

            print(
                repr(
                    obj.__dict__
                )
            )

        except Exception as exc:

            print(
                "__dict__ inspection failed:",
                repr(exc),
            )

    # -----------------------------------------------------
    # REPR
    # -----------------------------------------------------

    try:

        print()
        print(
            "repr(message):"
        )

        print(
            repr(obj)
        )

    except Exception as exc:

        print(
            "repr() failed:",
            repr(exc),
        )


# =========================================================
# MAIN TEST
# =========================================================

def main() -> int:

    heading(
        "STOCKVERSITY - UPSTOX WEBSOCKET V3 DIAGNOSTIC"
    )

    manager = None

    parser = None

    # =====================================================
    # 1. ENVIRONMENT
    # =====================================================

    heading(
        "1. ENVIRONMENT"
    )

    api_key = os.environ.get(
        "UPSTOX_API_KEY"
    )

    access_token = os.environ.get(
        "UPSTOX_ACCESS_TOKEN"
    )

    if not api_key:

        failed(
            "UPSTOX_API_KEY environment variable is missing."
        )

        return 1

    if not access_token:

        failed(
            "UPSTOX_ACCESS_TOKEN environment variable is missing."
        )

        return 1

    passed(
        "UPSTOX_API_KEY found."
    )

    passed(
        "UPSTOX_ACCESS_TOKEN found."
    )

    # =====================================================
    # 2. API CLIENT
    # =====================================================

    heading(
        "2. UPSTOX API CLIENT"
    )

    try:

        configuration = (
            upstox_client.Configuration()
        )

        configuration.access_token = (
            access_token
        )

        api_client = (
            upstox_client.ApiClient(
                configuration
            )
        )

        passed(
            "Upstox ApiClient created."
        )

    except Exception as exc:

        failed(
            f"Unable to create ApiClient: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # 3. PARSER
    # =====================================================

    heading(
        "3. MARKET DATA PARSER"
    )

    try:

        parser = (
            MarketDataParser()
        )

        passed(
            "MarketDataParser created."
        )

    except Exception as exc:

        failed(
            f"MarketDataParser creation failed: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # CALLBACK STATE
    # =====================================================

    connected_event = (
        threading.Event()
    )

    tick_event = (
        threading.Event()
    )

    raw_message_event = (
        threading.Event()
    )

    error_event = (
        threading.Event()
    )

    received_ticks = []

    websocket_errors = []

    raw_messages = []

    raw_message_count = 0

    # =====================================================
    # DEBUG PARSER
    # =====================================================

    def debug_parser(
        message: Any,
    ):

        nonlocal raw_message_count

        raw_message_count += 1

        raw_messages.append(
            message
        )

        raw_message_event.set()

        # -------------------------------------------------
        # PRINT FIRST FEW RAW MESSAGES
        # -------------------------------------------------

        if (
            raw_message_count
            <= MAX_RAW_MESSAGES_TO_PRINT
        ):

            print()
            print(
                "=" * 70
            )

            print(
                f"RAW UPSTOX MESSAGE #{raw_message_count}"
            )

            print(
                "=" * 70
            )

            describe_object(
                message
            )

            print(
                "=" * 70
            )
            print()

        # -------------------------------------------------
        # REAL STOCKVERSITY PARSER
        # -------------------------------------------------

        try:

            result = (
                parser.parse(
                    message
                )
            )

        except Exception as exc:

            print()
            print(
                "[PARSER EXCEPTION]"
            )

            print(
                repr(exc)
            )

            traceback.print_exc()

            return None

        # -------------------------------------------------
        # DEBUG PARSER RESULT
        # -------------------------------------------------

        if (
            raw_message_count
            <= MAX_RAW_MESSAGES_TO_PRINT
        ):

            print(
                "[PARSER RETURN]"
            )

            print(
                repr(result)
            )

            print()

        return result

    # =====================================================
    # 4. WEBSOCKET MANAGER
    # =====================================================

    heading(
        "4. WEBSOCKET MANAGER"
    )

    try:

        manager = (
            WebSocketManager(
                api_client
            )
        )

        passed(
            "WebSocketManager created."
        )

        manager.set_message_parser(
            debug_parser
        )

        passed(
            "Diagnostic parser attached."
        )

    except Exception as exc:

        failed(
            f"WebSocketManager setup failed: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # STATUS CALLBACK
    # =====================================================

    def on_status(
        connected: bool,
    ) -> None:

        print(
            f"[STATUS] Connected = {connected}"
        )

        if connected:

            connected_event.set()

    # =====================================================
    # ERROR CALLBACK
    # =====================================================

    def on_error(
        error,
    ) -> None:

        websocket_errors.append(
            error
        )

        print()
        print(
            "[WEBSOCKET ERROR]"
        )

        print(
            error
        )

        error_event.set()

    # =====================================================
    # TICK CALLBACK
    # =====================================================

    def on_tick(
        tick,
    ) -> None:

        received_ticks.append(
            tick
        )

        print()
        print(
            "=" * 70
        )

        print(
            "LIVE TICK RECEIVED"
        )

        print(
            "=" * 70
        )

        print(
            tick
        )

        print()

        # ---------------------------------------------
        # DISPLAY COMMON TICK FIELDS
        # ---------------------------------------------

        attributes = (

            "instrument_key",

            "symbol",

            "ltp",

            "last_price",

            "open",

            "high",

            "low",

            "close",

            "volume",

            "bid",

            "ask",

            "bid_qty",

            "ask_qty",

            "open_interest",

            "timestamp",

        )

        for attribute in attributes:

            if hasattr(
                tick,
                attribute,
            ):

                try:

                    value = getattr(
                        tick,
                        attribute
                    )

                    print(
                        f"{attribute}: {value}"
                    )

                except Exception:

                    pass

        print(
            "=" * 70
        )

        tick_event.set()

    # =====================================================
    # REGISTER CALLBACKS
    # =====================================================

    heading(
        "5. CALLBACK REGISTRATION"
    )

    try:

        manager.add_status_callback(
            on_status
        )

        manager.add_error_callback(
            on_error
        )

        manager.add_tick_callback(
            on_tick
        )

        passed(
            "Callbacks registered."
        )

    except Exception as exc:

        failed(
            f"Callback registration failed: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # 6. SUBSCRIBE BEFORE CONNECT
    # =====================================================

    heading(
        "6. NIFTY 50 SUBSCRIPTION"
    )

    try:

        manager.subscribe(
            INSTRUMENT_KEY,
            MODE,
        )

        passed(
            f"Subscription queued: {INSTRUMENT_KEY}"
        )

        info(
            f"Mode: {MODE}"
        )

    except Exception as exc:

        failed(
            f"Unable to queue subscription: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # 7. CONNECT
    # =====================================================

    heading(
        "7. WEBSOCKET CONNECTION"
    )

    try:

        info(
            "Connecting to Upstox MarketDataStreamerV3..."
        )

        manager.connect()

    except Exception as exc:

        failed(
            f"WebSocket connect() failed: {exc}"
        )

        traceback.print_exc()

        return 1

    # =====================================================
    # WAIT FOR CONNECTION
    # =====================================================

    info(
        f"Waiting up to {CONNECTION_TIMEOUT} seconds "
        "for WebSocket connection..."
    )

    connected = (
        connected_event.wait(
            CONNECTION_TIMEOUT
        )
    )

    if not connected:

        if error_event.is_set():

            failed(
                "WebSocket connection generated an error."
            )

        else:

            failed(
                "WebSocket did not report OPEN "
                f"within {CONNECTION_TIMEOUT} seconds."
            )

        try:

            manager.disconnect()

        except Exception:

            pass

        return 1

    passed(
        "WebSocket connected successfully."
    )

    # =====================================================
    # 8. WAIT FOR RAW MARKET DATA
    # =====================================================

    heading(
        "8. RAW MARKET DATA"
    )

    info(
        f"Subscribed instrument: {INSTRUMENT_KEY}"
    )

    info(
        f"Waiting up to {MESSAGE_WAIT_TIME} seconds "
        "for Upstox messages..."
    )

    raw_received = (
        raw_message_event.wait(
            MESSAGE_WAIT_TIME
        )
    )

    if raw_received:

        passed(
            "At least one raw WebSocket message received."
        )

    else:

        warning(
            "No raw WebSocket message received "
            "during the wait period."
        )

    # =====================================================
    # GIVE PARSER A LITTLE TIME
    # =====================================================

    if raw_received:

        info(
            "Waiting briefly for parser/tick processing..."
        )

        tick_event.wait(
            3
        )

    # =====================================================
    # 9. DIAGNOSTICS
    # =====================================================

    heading(
        "9. DIAGNOSTICS"
    )

    print(
        "Manager connected:",
        getattr(
            manager,
            "connected",
            False,
        ),
    )

    print(
        "Manager total messages:",
        getattr(
            manager,
            "total_messages",
            0,
        ),
    )

    print(
        "Raw messages captured:",
        len(
            raw_messages
        ),
    )

    print(
        "Parsed ticks received:",
        len(
            received_ticks
        ),
    )

    try:

        print(
            "Parser statistics:",
            parser.statistics(),
        )

    except Exception as exc:

        print(
            "Parser statistics unavailable:",
            exc,
        )

    # -----------------------------------------------------
    # PARSER DIAGNOSTICS
    # -----------------------------------------------------

    if hasattr(
        parser,
        "diagnostics",
    ):

        try:

            print(
                "Parser diagnostics:",
                parser.diagnostics(),
            )

        except Exception as exc:

            print(
                "Parser diagnostics unavailable:",
                exc,
            )

    # -----------------------------------------------------
    # WEBSOCKET ERRORS
    # -----------------------------------------------------

    if websocket_errors:

        print()
        print(
            "WebSocket errors:"
        )

        for error in websocket_errors:

            print(
                " -",
                error,
            )

    # =====================================================
    # 10. CLEAN SHUTDOWN
    # =====================================================

    heading(
        "10. CLEAN SHUTDOWN"
    )

    try:

        manager.disconnect()

        passed(
            "WebSocket disconnected."
        )

    except Exception as exc:

        warning(
            f"Disconnect issue: {exc}"
        )

    # Give callback threads a moment to settle.

    time.sleep(
        1
    )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    heading(
        "TEST RESULT"
    )

    # -----------------------------------------------------
    # FULL SUCCESS
    # -----------------------------------------------------

    if received_ticks:

        passed(
            "LIVE UPSTOX WEBSOCKET DATA RECEIVED AND PARSED."
        )

        print()
        print(
            "UPSTOX WEBSOCKET V3: READY"
        )

        print()
        print(
            "MarketDataParser: READY"
        )

        return 0

    # -----------------------------------------------------
    # RAW DATA BUT NO TICK
    # -----------------------------------------------------

    if raw_messages:

        print(
            "[PARTIAL PASS] WebSocket received raw messages "
            "but MarketDataParser produced no Tick."
        )

        print()
        print(
            "IMPORTANT:"
        )

        print(
            "Copy the RAW UPSTOX MESSAGE section shown above "
            "and send it for parser inspection."
        )

        print()
        print(
            "Do NOT modify WebSocketManager yet."
        )

        return 2

    # -----------------------------------------------------
    # CONNECTED BUT NOTHING ARRIVED
    # -----------------------------------------------------

    if connected:

        print(
            "[PARTIAL PASS] WebSocket connected successfully "
            "but no market-data message arrived."
        )

        print()
        print(
            "If NSE is closed, this does not automatically "
            "mean the WebSocket implementation is broken."
        )

        print()
        print(
            "Run the test again during live NSE market hours."
        )

        return 3

    # -----------------------------------------------------
    # FAILURE
    # -----------------------------------------------------

    failed(
        "WebSocket diagnostic test failed."
    )

    return 1


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    try:

        raise SystemExit(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "Test interrupted by user."
        )

        raise SystemExit(
            130
        )
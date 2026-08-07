from pathlib import Path
from datetime import datetime
import shutil

APP = Path("ui/app.py")
PAGE = Path("ui/pages/intraday_page.py")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# =========================================================
# SAFETY
# =========================================================

for path in (APP, PAGE):
    if not path.exists():
        raise SystemExit(f"SAFETY STOP: {path} not found")

    if path.stat().st_size < 10000:
        raise SystemExit(
            f"SAFETY STOP: {path} unexpectedly small"
        )

# =========================================================
# BACKUPS
# =========================================================

app_backup = APP.with_name(
    f"app.before_live_intraday_{stamp}.py"
)

page_backup = PAGE.with_name(
    f"intraday_page.before_live_intraday_{stamp}.py"
)

shutil.copy2(APP, app_backup)
shutil.copy2(PAGE, page_backup)

# =========================================================
# PATCH ui/app.py
# =========================================================

text = APP.read_text(encoding="utf-8")

old_page = '''        self._add_page(
            "scanner",
            IntradayScannerPage(),
        )'''

new_page = '''        self.intraday_page = IntradayScannerPage()

        self._add_page(
            "scanner",
            self.intraday_page,
        )

        # -------------------------------------------------
        # LIVE INTRADAY SCANNER CONNECTION
        # -------------------------------------------------

        try:

            container = get_container()

            self.application_controller = (
                container.get(
                    "application_controller"
                )
            )

            self.intraday_page.scan_requested.connect(
                self._run_intraday_scan
            )

            self.application_controller.scannerCompleted.connect(
                self._receive_intraday_results
            )

            print(
                "[INTRADAY] Live scanner connected."
            )

        except Exception as exc:

            print(
                "[INTRADAY] Connection failed:",
                exc,
            )'''

if old_page not in text:
    raise SystemExit(
        "SAFETY STOP: scanner page creation block not found. "
        "app.py unchanged."
    )

text = text.replace(
    old_page,
    new_page,
    1,
)

# ---------------------------------------------------------
# Add bridge methods before SIDEBAR
# ---------------------------------------------------------

marker = '''    # =====================================================
    # SIDEBAR
    # ====================================================='''

if marker not in text:
    raise SystemExit(
        "SAFETY STOP: SIDEBAR marker not found."
    )

bridge = '''    # =====================================================
    # LIVE INTRADAY SCANNER BRIDGE
    # =====================================================

    def _run_intraday_scan(
        self,
        filters: Dict,
    ) -> None:
        """
        Execute the existing StockVersity scanner pipeline.

        No duplicate scanner or NSE engine is created here.
        """

        try:

            controller = self.application_controller

            if controller is None:
                raise RuntimeError(
                    "ApplicationController unavailable"
                )

            print(
                "[INTRADAY] Scan requested:",
                filters,
            )

            # Existing ApplicationController owns:
            # NSEDataEngine -> ScannerExecutor -> Ranker.
            controller.run_scanner()

        except Exception as exc:

            print(
                "[INTRADAY] Scan failed:",
                exc,
            )

            if hasattr(
                self,
                "intraday_page",
            ):

                self.intraday_page.scan_failed(
                    str(exc)
                )


    def _receive_intraday_results(
        self,
        opportunities,
    ) -> None:
        """
        Receive ranked opportunities from the existing
        ApplicationController scannerCompleted signal.
        """

        try:

            if opportunities is None:
                opportunities = []

            if not isinstance(
                opportunities,
                list,
            ):
                opportunities = list(
                    opportunities
                )

            print(
                "[INTRADAY] Results received:",
                len(opportunities),
            )

            self.intraday_page.set_scanner_results(
                opportunities
            )

        except Exception as exc:

            print(
                "[INTRADAY] Result update failed:",
                exc,
            )


'''

text = text.replace(
    marker,
    bridge + marker,
    1,
)

APP.write_text(
    text,
    encoding="utf-8",
)

# =========================================================
# PATCH intraday_page.py
# =========================================================

text = PAGE.read_text(
    encoding="utf-8"
)

old_demo = '''        # Development mode only:
        # simulate a short scan cycle.

        QTimer.singleShot(
            700,
            self._finish_demo_scan,
        )'''

new_demo = '''        # Real scanner mode.
        #
        # Results now return through set_scanner_results().
        # Demo timer intentionally disabled.'''

if old_demo not in text:
    raise SystemExit(
        "SAFETY STOP: demo timer block not found."
    )

text = text.replace(
    old_demo,
    new_demo,
    1,
)

# ---------------------------------------------------------
# Ensure real results restore RUN button
# ---------------------------------------------------------

result_marker = '''        self.opportunity_table.set_opportunities(
            opportunities
        )'''

result_replacement = '''        # Real scanner response received.
        # Restore scanner controls.

        self.scanner_header.scan_button.setEnabled(
            True
        )

        self.scanner_header.scan_button.setText(
            "RUN SCANNER"
        )

        from PySide6.QtCore import QDateTime

        self.scanner_header.set_last_scan(
            QDateTime.currentDateTime().toString(
                "hh:mm:ss AP"
            )
        )

        self.opportunity_table.set_opportunities(
            opportunities
        )'''

if result_marker not in text:
    raise SystemExit(
        "SAFETY STOP: set_scanner_results insertion "
        "point not found."
    )

text = text.replace(
    result_marker,
    result_replacement,
    1,
)

# ---------------------------------------------------------
# Add failure handler
# ---------------------------------------------------------

external_marker = '''    # ======================================================
    # EXTERNAL DATA API
    # ======================================================'''

failure_method = '''    def scan_failed(
        self,
        message: str,
    ) -> None:

        self.scanner_header.scan_button.setEnabled(
            True
        )

        self.scanner_header.scan_button.setText(
            "RUN SCANNER"
        )

        self.scanner_status.set_status(
            {
                "status": "ERROR",
                "scanned": 0,
                "passed": 0,
                "buys": 0,
                "sells": 0,
                "best_score": 0,
                "runtime": str(message),
            }
        )


'''

if external_marker not in text:
    raise SystemExit(
        "SAFETY STOP: EXTERNAL DATA API marker "
        "not found."
    )

text = text.replace(
    external_marker,
    failure_method + external_marker,
    1,
)

PAGE.write_text(
    text,
    encoding="utf-8",
)

print()
print("=" * 54)
print("LIVE INTRADAY SCANNER UI CONNECTION COMPLETE")
print("=" * 54)
print("App backup :", app_backup)
print("Page backup:", page_backup)
print()
print("Connected:")
print("  IntradayScannerPage")
print("        -> scan_requested")
print("        -> ApplicationController")
print("        -> existing NSEDataEngine")
print("        -> existing ScannerExecutor")
print("        -> scannerCompleted")
print("        -> set_scanner_results")
print()
print("Demo result timer: DISABLED")
print("=" * 54)

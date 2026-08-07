from pathlib import Path
from datetime import datetime
import shutil

app = Path("core/app_controller.py")
market = Path("ui/market_controller.py")

if not app.exists() or not market.exists():
    raise SystemExit("SAFETY STOP: required file missing")

app_text = app.read_text(encoding="utf-8")
market_text = market.read_text(encoding="utf-8")

if len(app_text) < 30000:
    raise SystemExit("SAFETY STOP: app_controller.py unexpectedly small")

if len(market_text) < 10000:
    raise SystemExit("SAFETY STOP: market_controller.py unexpectedly small")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

app_backup = app.with_name(
    f"app_controller.before_institutional_isolation_{stamp}.py"
)

market_backup = market.with_name(
    f"market_controller.before_institutional_isolation_{stamp}.py"
)

shutil.copy2(app, app_backup)
shutil.copy2(market, market_backup)


# =========================================================
# PART 1
# Add independent institutional refresh method
# to AppController.
# =========================================================

if "def refresh_institutional_data(self):" not in app_text:

    marker = '''    # =====================================================
    # REFRESH DASHBOARDS
    # =====================================================
'''

    if marker not in app_text:
        raise SystemExit(
            "SAFETY STOP: REFRESH DASHBOARDS marker not found"
        )

    method = '''    # =====================================================
    # REFRESH INSTITUTIONAL DATA
    # =====================================================

    def refresh_institutional_data(self):
        """
        Refresh FII/DII independently from the main market
        refresh so another provider failure cannot prevent
        Institutional Flow from updating.
        """

        try:

            service = getattr(
                self,
                "fii_dii",
                None,
            )

            if service is None:
                return

            data = service.fetch()

            if not isinstance(
                data,
                dict,
            ):
                return

            # Do not replace a valid cached session with an
            # unavailable response.
            if not data.get(
                "available",
                False,
            ):
                return

            if not isinstance(
                self.market_cache,
                dict,
            ):
                self.market_cache = {}

            self.market_cache[
                "institutional"
            ] = data

        except Exception as e:

            try:
                self.errorOccurred.emit(
                    f"Institutional refresh: {e}"
                )

            except Exception:
                pass


'''

    app_text = app_text.replace(
        marker,
        method + marker,
        1,
    )


# =========================================================
# PART 2
# Call institutional refresh independently from
# refresh_everything().
# =========================================================

old = '''            self.refresh_market()

            self.refresh_dashboards()'''

new = '''            self.refresh_market()

            # FII/DII is intentionally refreshed separately.
            # A failure in Yahoo/NSE breadth/sectors must not
            # prevent Institutional Flow from updating.
            self.refresh_institutional_data()

            self.refresh_dashboards()'''

# There are duplicate historical sections in this file.
# Patch all matching refresh_everything implementations.
if "self.refresh_institutional_data()" not in app_text:

    if old not in app_text:
        raise SystemExit(
            "SAFETY STOP: refresh_everything insertion point not found"
        )

    app_text = app_text.replace(
        old,
        new,
    )


# =========================================================
# PART 3
# Normalize institutional data BEFORE the NIFTY500
# universe check.
# =========================================================

old_market = '''        universe = getattr(
            self,
            "live_stock_universe",
            None,
        )

        if universe is None:
            return

        if not isinstance(
            self.market_data,
            dict,
        ):
            self.market_data = {}

        # -------------------------------------------------
        # INSTITUTIONAL FLOW
        #
        # AppController.market_snapshot() stores this under
        # market -> institutional. Copy it to the normalized
        # top-level dashboard snapshot.
        # -------------------------------------------------

        try:

            legacy_market = self.market_data.get(
                "market",
                {},
            )

            if isinstance(
                legacy_market,
                dict,
            ):

                institutional = legacy_market.get(
                    "institutional",
                    {},
                )

                if isinstance(
                    institutional,
                    dict,
                ):

                    self.market_data[
                        "institutional"
                    ] = institutional

        except Exception:
            pass
'''

new_market = '''        # -------------------------------------------------
        # INSTITUTIONAL FLOW
        #
        # This is independent of the NIFTY 500 universe.
        # Normalize it BEFORE checking live_stock_universe.
        # -------------------------------------------------

        if not isinstance(
            self.market_data,
            dict,
        ):
            self.market_data = {}

        try:

            legacy_market = self.market_data.get(
                "market",
                {},
            )

            if isinstance(
                legacy_market,
                dict,
            ):

                institutional = legacy_market.get(
                    "institutional",
                    {},
                )

                if isinstance(
                    institutional,
                    dict,
                ) and institutional:

                    self.market_data[
                        "institutional"
                    ] = institutional

        except Exception:
            pass

        universe = getattr(
            self,
            "live_stock_universe",
            None,
        )

        if universe is None:
            return
'''

if old_market not in market_text:
    raise SystemExit(
        "SAFETY STOP: existing institutional merge block "
        "not found. Files unchanged."
    )

market_text = market_text.replace(
    old_market,
    new_market,
    1,
)


# =========================================================
# WRITE
# =========================================================

app.write_text(
    app_text,
    encoding="utf-8",
)

market.write_text(
    market_text,
    encoding="utf-8",
)

print()
print("========================================")
print("INSTITUTIONAL PIPELINE ISOLATION COMPLETE")
print("========================================")
print("FII/DII service       : INDEPENDENT")
print("Main market failure   : CANNOT BLOCK FII/DII")
print("NIFTY500 dependency   : REMOVED")
print("Valid cache protected : YES")
print("Dashboard UI          : UNTOUCHED")
print("NIFTY500 live engine  : UNTOUCHED")
print("Upstox pipeline       : UNTOUCHED")
print("Refresh timer         : UNTOUCHED (30 sec)")
print()
print("App backup    :", app_backup)
print("Market backup :", market_backup)
print("========================================")

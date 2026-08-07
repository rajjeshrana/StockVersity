from pathlib import Path
from datetime import datetime
import shutil
import sys

FILE = Path("ui/market_controller.py")

if not FILE.exists():
    raise SystemExit("ERROR: market_controller.py not found")

# ---------------------------------------------------------
# SAFETY CHECK
# ---------------------------------------------------------

original = FILE.read_text(encoding="utf-8")

if len(original) < 10000:
    raise SystemExit(
        f"SAFETY STOP: controller unexpectedly small "
        f"({len(original)} characters)"
    )

if "def refresh_market(self):" not in original:
    raise SystemExit(
        "SAFETY STOP: refresh_market() not found"
    )

if "def update_indices(self):" not in original:
    raise SystemExit(
        "SAFETY STOP: update_indices() not found"
    )

# ---------------------------------------------------------
# TIMESTAMPED BACKUP
# ---------------------------------------------------------

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = FILE.with_name(
    f"market_controller.before_live_merge_{stamp}.py"
)

shutil.copy2(
    FILE,
    backup,
)

print(f"Backup: {backup}")

text = original


# =========================================================
# CHANGE 1
# Add live merge to existing refresh_market()
# =========================================================

old = '''        self.last_update = datetime.now()

        self.update_indices()
'''

new = '''        # -------------------------------------------------
        # Merge the live NIFTY 500 universe into the legacy
        # backend snapshot.
        #
        # Existing index data remains untouched.
        # -------------------------------------------------

        self._merge_live_nifty500()

        self.last_update = datetime.now()

        self.update_indices()
'''

if old not in text:
    raise SystemExit(
        "SAFETY STOP: refresh insertion point not found. "
        "File has NOT been written."
    )

text = text.replace(
    old,
    new,
    1,
)


# =========================================================
# CHANGE 2
# Add new live-universe merge method
# =========================================================

marker = '''    # =====================================================
    # UPDATE INDICES
    # =====================================================

    def update_indices(self):
'''

if marker not in text:
    raise SystemExit(
        "SAFETY STOP: update_indices marker not found. "
        "File has NOT been written."
    )


method = '''    # =====================================================
    # LIVE NIFTY 500 MERGE
    # =====================================================

    def _merge_live_nifty500(self):
        """
        Merge LiveStockUniverse data into market_data.

        Preserves:
            indices
            other legacy backend sections

        Replaces with live NIFTY 500 data:
            breadth
            sectors
            gainers
            losers
            heatmap
        """

        universe = getattr(
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
        # BREADTH
        # -------------------------------------------------

        try:

            breadth = universe.breadth()

            if isinstance(
                breadth,
                dict,
            ):
                self.market_data[
                    "breadth"
                ] = breadth

        except Exception:
            pass

        # -------------------------------------------------
        # INDUSTRY STRENGTH -> SECTOR FORMAT
        # -------------------------------------------------

        try:

            industries = (
                universe.industry_strength()
            )

            sectors = []

            if isinstance(
                industries,
                list,
            ):

                for row in industries:

                    if not isinstance(
                        row,
                        dict,
                    ):
                        continue

                    name = str(
                        row.get(
                            "industry",
                            "Unknown",
                        )
                    )

                    try:
                        change = float(
                            row.get(
                                "average_change_percent",
                                0.0,
                            )
                            or 0.0
                        )
                    except (
                        TypeError,
                        ValueError,
                    ):
                        change = 0.0

                    sectors.append(
                        {
                            "name": name,
                            "sector": name,
                            "industry": name,

                            # Compatibility with the
                            # existing MarketController.
                            "change": change,
                            "change_percent": change,

                            "average_change_percent":
                                change,

                            "advance": row.get(
                                "advance",
                                0,
                            ),

                            "decline": row.get(
                                "decline",
                                0,
                            ),

                            "unchanged": row.get(
                                "unchanged",
                                0,
                            ),

                            "live_stocks": row.get(
                                "live_stocks",
                                0,
                            ),
                        }
                    )

            self.market_data[
                "sectors"
            ] = sectors

        except Exception:
            pass

        # -------------------------------------------------
        # GAINERS
        # -------------------------------------------------

        try:

            gainers = universe.top_gainers(
                limit=10
            )

            if isinstance(
                gainers,
                list,
            ):
                self.market_data[
                    "gainers"
                ] = gainers

        except Exception:
            pass

        # -------------------------------------------------
        # LOSERS
        # -------------------------------------------------

        try:

            losers = universe.top_losers(
                limit=10
            )

            if isinstance(
                losers,
                list,
            ):
                self.market_data[
                    "losers"
                ] = losers

        except Exception:
            pass

        # -------------------------------------------------
        # HEATMAP
        # -------------------------------------------------

        try:

            heatmap = universe.heatmap(
                limit=30
            )

            if isinstance(
                heatmap,
                list,
            ):
                self.market_data[
                    "heatmap"
                ] = heatmap

        except Exception:
            pass


'''


text = text.replace(
    marker,
    method + marker,
    1,
)


# =========================================================
# FINAL SAFETY CHECKS
# =========================================================

if len(text) < len(original):
    raise SystemExit(
        "SAFETY STOP: resulting file became smaller. "
        "Nothing written."
    )

if text.count(
    "def _merge_live_nifty500"
) != 1:
    raise SystemExit(
        "SAFETY STOP: unexpected live merge method count. "
        "Nothing written."
    )

if text.count(
    "self._merge_live_nifty500()"
) != 1:
    raise SystemExit(
        "SAFETY STOP: unexpected merge call count. "
        "Nothing written."
    )


# =========================================================
# WRITE
# =========================================================

FILE.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("SAFE LIVE NIFTY 500 MERGE COMPLETE")
print("========================================")
print("Breadth       : connected to universe")
print("Sectors       : connected to universe")
print("Gainers       : connected to universe")
print("Losers        : connected to universe")
print("Heatmap data  : connected to universe")
print("Indices       : preserved")
print("UI            : untouched")
print("Upstox        : untouched")
print("========================================")
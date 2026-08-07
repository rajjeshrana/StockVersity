from pathlib import Path
from datetime import datetime
import shutil
import py_compile


ROOT = Path(__file__).resolve().parent

CONTROLLER = ROOT / "ui" / "market_controller.py"
DASHBOARD = ROOT / "ui" / "pages" / "dashboard_page.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def backup(path: Path) -> Path:
    target = path.with_name(
        f"{path.stem}.before_live_breadth_fix_{timestamp}{path.suffix}"
    )
    shutil.copy2(path, target)
    return target


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(
            f"[PATCH ERROR] Could not find expected block: {label}"
        )

    return text.replace(old, new, 1)


print("=" * 72)
print("STOCKVERSITY LIVE MARKET BREADTH PATCH")
print("=" * 72)

controller_backup = backup(CONTROLLER)
dashboard_backup = backup(DASHBOARD)

# ============================================================
# PATCH 1 — MARKET CONTROLLER
# ============================================================

text = CONTROLLER.read_text(
    encoding="utf-8"
)

old = '''        updater(
            sectors=self.market_data.get(
                "sectors",
                [],
            ),
'''

new = '''        updater(
            breadth=self.market_data.get(
                "breadth",
                {},
            ),
            sectors=self.market_data.get(
                "sectors",
                [],
            ),
'''

text = replace_once(
    text,
    old,
    new,
    "MarketController updater breadth argument",
)

CONTROLLER.write_text(
    text,
    encoding="utf-8",
)

print("[PATCH] MarketController now sends live breadth.")

# ============================================================
# PATCH 2 — DASHBOARD METHOD SIGNATURE
# ============================================================

text = DASHBOARD.read_text(
    encoding="utf-8"
)

old = '''    def update_live_market_cards(
        self,
        sectors=None,
        heatmap=None,
        gainers=None,
        losers=None,
        institutional=None,
    ) -> None:

        sectors = sectors or []
        heatmap = heatmap or []
        gainers = gainers or []
        losers = losers or []
        institutional = institutional or {}
'''

new = '''    def update_live_market_cards(
        self,
        breadth=None,
        sectors=None,
        heatmap=None,
        gainers=None,
        losers=None,
        institutional=None,
    ) -> None:

        breadth = breadth or {}
        sectors = sectors or []
        heatmap = heatmap or []
        gainers = gainers or []
        losers = losers or []
        institutional = institutional or {}

        # -------------------------------------------------
        # Market Breadth — LIVE NIFTY 500
        # -------------------------------------------------

        try:
            advances = int(
                breadth.get(
                    "advance",
                    breadth.get(
                        "advances",
                        0,
                    ),
                )
                or 0
            )

            declines = int(
                breadth.get(
                    "decline",
                    breadth.get(
                        "declines",
                        0,
                    ),
                )
                or 0
            )

            unchanged = int(
                breadth.get(
                    "unchanged",
                    0,
                )
                or 0
            )

            total = (
                advances
                + declines
                + unchanged
            )

            if hasattr(
                self,
                "advance_card",
            ):
                self.advance_card.set_value(
                    f"{advances:,}"
                )

            if hasattr(
                self,
                "decline_card",
            ):
                self.decline_card.set_value(
                    f"{declines:,}"
                )

            if hasattr(
                self,
                "unchanged_card",
            ):
                self.unchanged_card.set_value(
                    f"{unchanged:,}"
                )

            if total > 0:
                breadth_percent = int(
                    round(
                        advances
                        / total
                        * 100.0
                    )
                )
            else:
                breadth_percent = 0

            breadth_percent = max(
                0,
                min(
                    100,
                    breadth_percent,
                ),
            )

            gauge = getattr(
                self,
                "breadth_gauge",
                None,
            )

            if gauge is not None:
                if hasattr(
                    gauge,
                    "set_value",
                ):
                    gauge.set_value(
                        breadth_percent
                    )

                elif hasattr(
                    gauge,
                    "setValue",
                ):
                    gauge.setValue(
                        breadth_percent
                    )

        except Exception:
            pass
'''

text = replace_once(
    text,
    old,
    new,
    "Dashboard live market method signature",
)

# ============================================================
# PATCH 3 — REMOVE FAKE STARTUP BREADTH VALUES
# ============================================================

text = text.replace(
    '''            "1,247",
            GREEN,
''',
    '''            "--",
            GREEN,
''',
    1,
)

text = text.replace(
    '''            "684",
            RED,
''',
    '''            "--",
            RED,
''',
    1,
)

text = text.replace(
    '''            "91",
            MUTED,
''',
    '''            "--",
            MUTED,
''',
    1,
)

DASHBOARD.write_text(
    text,
    encoding="utf-8",
)

print("[PATCH] Dashboard accepts live breadth.")
print("[PATCH] Advances connected.")
print("[PATCH] Declines connected.")
print("[PATCH] Unchanged connected.")
print("[PATCH] Breadth gauge connected.")
print("[PATCH] Fake startup breadth values removed.")

# ============================================================
# SYNTAX VALIDATION
# ============================================================

py_compile.compile(
    str(CONTROLLER),
    doraise=True,
)

py_compile.compile(
    str(DASHBOARD),
    doraise=True,
)

print()
print("=" * 72)
print("LIVE MARKET BREADTH FIX INSTALLED")
print("=" * 72)

print(f"Controller backup : {controller_backup}")
print(f"Dashboard backup  : {dashboard_backup}")

print()
print("Live pipeline:")
print("  LiveStockUniverse.breadth()")
print("          ↓")
print("  MarketController.market_data['breadth']")
print("          ↓")
print("  update_live_dashboard_cards()")
print("          ↓")
print("  DashboardPage.update_live_market_cards()")
print("          ↓")
print("  Advances / Declines / Unchanged / Gauge")

print()
print("Syntax validation: PASSED")
print("=" * 72)
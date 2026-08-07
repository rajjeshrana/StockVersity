from pathlib import Path
from datetime import datetime
import shutil

path = Path("backend/scanner/nse_data_engine.py")

text = path.read_text(
    encoding="utf-8"
)

# ---------------------------------------------------------
# SAFETY
# ---------------------------------------------------------

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: nse_data_engine.py unexpectedly small."
    )

target = '''    def market_snapshot(
        self,
    ) -> Dict:

        return {

            "Status": self.market_status(),

            "Last Update": self.last_refresh,

            "Stocks": len(self.market_data),

            "Indices": self.indices,

            "Breadth": self.market_breadth,

            "Top Gainers": self.top_gainers,

            "Top Losers": self.top_losers,

        }
'''

if target not in text:
    raise SystemExit(
        "SAFETY STOP: exact market_snapshot() block not found. "
        "File unchanged."
    )

# ---------------------------------------------------------
# BACKUP
# ---------------------------------------------------------

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = path.with_name(
    f"nse_data_engine.before_institutional_{stamp}.py"
)

shutil.copy2(
    path,
    backup,
)

# ---------------------------------------------------------
# NEW SNAPSHOT
# ---------------------------------------------------------

replacement = '''    def market_snapshot(
        self,
    ) -> Dict:

        # -------------------------------------------------
        # Institutional Flow
        #
        # FII/DII cash-market data is published after
        # market hours. Failure here must never interrupt
        # the main NSE / Upstox dashboard pipeline.
        # -------------------------------------------------

        institutional = {}

        try:

            from backend.services.fii_dii_service import (
                FIIDIIService,
            )

            service = getattr(
                self,
                "_fii_dii_service",
                None,
            )

            if service is None:

                service = FIIDIIService()

                self._fii_dii_service = service

            result = service.fetch()

            if isinstance(
                result,
                dict,
            ):

                institutional = result

        except Exception as exc:

            try:
                self.logger.warning(
                    "Institutional flow unavailable: %s",
                    exc,
                )
            except Exception:
                pass

        return {

            "Status": self.market_status(),

            "Last Update": self.last_refresh,

            "Stocks": len(self.market_data),

            "Indices": self.indices,

            "Breadth": self.market_breadth,

            "Top Gainers": self.top_gainers,

            "Top Losers": self.top_losers,

            # Normalized dashboard key
            "institutional": institutional,

        }
'''

text = text.replace(
    target,
    replacement,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("INSTITUTIONAL FLOW ENGINE PATCH COMPLETE")
print("========================================")
print("Backend       : NSEDataEngine")
print("FII/DII       : FIIDIIService")
print("Snapshot key  : institutional")
print("UI            : untouched")
print("NIFTY 500     : untouched")
print("Upstox        : untouched")
print("Backup        :", backup)
print("========================================")

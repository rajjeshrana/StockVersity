from pathlib import Path
from datetime import datetime
import shutil

path = Path("ui/app.py")

if not path.exists():
    raise SystemExit(
        "ERROR: ui/app.py not found"
    )

text = path.read_text(
    encoding="utf-8"
)

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: app.py unexpectedly small"
    )

# =========================================================
# BACKUP
# =========================================================

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = path.with_name(
    f"app.before_live_footer_{stamp}.py"
)

shutil.copy2(
    path,
    backup,
)

# =========================================================
# STEP 1
# Store footer NSE label on self
# =========================================================

old_nse = '''        nse = QLabel(
            "NSE   â—   OPEN"
        )
'''

new_nse = '''        self.footer_nse = QLabel(
            "NSE   ●   OPEN"
        )

        nse = self.footer_nse
'''

if old_nse not in text:

    # Handle already-correct Unicode source if present.
    old_nse = '''        nse = QLabel(
            "NSE   ●   OPEN"
        )
'''

if old_nse not in text:
    raise SystemExit(
        "SAFETY STOP: footer NSE block not found. "
        "app.py NOT changed."
    )

text = text.replace(
    old_nse,
    new_nse,
    1,
)

# =========================================================
# STEP 2
# Store footer BSE label on self
# =========================================================

old_bse = '''        bse = QLabel(
            "BSE   â—   OPEN"
        )
'''

new_bse = '''        self.footer_bse = QLabel(
            "BSE   ●   OPEN"
        )

        bse = self.footer_bse
'''

if old_bse not in text:

    old_bse = '''        bse = QLabel(
            "BSE   ●   OPEN"
        )
'''

if old_bse not in text:
    raise SystemExit(
        "SAFETY STOP: footer BSE block not found. "
        "app.py NOT changed."
    )

text = text.replace(
    old_bse,
    new_bse,
    1,
)

# =========================================================
# STEP 3
# Add footer update inside _update_shell_clock()
# =========================================================

marker = '''

    # =====================================================
    # PAGE MANAGEMENT
    # =====================================================
'''

if marker not in text:
    raise SystemExit(
        "SAFETY STOP: PAGE MANAGEMENT marker not found. "
        "app.py NOT changed."
    )

footer_update = '''

        # ---------------------------------------------
        # Footer market status
        # ---------------------------------------------

        footer_state = (
            "OPEN"
            if market_open
            else "CLOSED"
        )

        footer_color = (
            "#25dc7b"
            if market_open
            else "#ff5364"
        )

        if hasattr(
            self,
            "footer_nse",
        ):

            self.footer_nse.setText(
                f"NSE   ●   {footer_state}"
            )

            self.footer_nse.setStyleSheet(
                f"""
                color: {footer_color};
                font-size: 12px;
                font-weight: 700;
                """
            )

        if hasattr(
            self,
            "footer_bse",
        ):

            self.footer_bse.setText(
                f"BSE   ●   {footer_state}"
            )

            self.footer_bse.setStyleSheet(
                f"""
                color: {footer_color};
                font-size: 12px;
                font-weight: 700;
                """
            )
'''

# Don't accidentally add it twice.
if "self.footer_nse.setText(" in text:
    raise SystemExit(
        "SAFETY STOP: footer live updater already appears "
        "to exist. Nothing written."
    )

text = text.replace(
    marker,
    footer_update + marker,
    1,
)

# =========================================================
# FINAL SAFETY CHECKS
# =========================================================

required = [
    "self.footer_nse = QLabel(",
    "self.footer_bse = QLabel(",
    "self.footer_nse.setText(",
    "self.footer_bse.setText(",
]

for item in required:
    if item not in text:
        raise SystemExit(
            f"SAFETY STOP: missing {item}. "
            "Nothing written."
        )

if len(text) < 10000:
    raise SystemExit(
        "SAFETY STOP: resulting app.py unexpectedly small"
    )

# =========================================================
# WRITE
# =========================================================

path.write_text(
    text,
    encoding="utf-8",
)

print()
print("========================================")
print("LIVE FOOTER STATUS PATCH COMPLETE")
print("========================================")
print("Footer NSE     : DYNAMIC")
print("Footer BSE     : DYNAMIC")
print("OPEN           : GREEN")
print("CLOSED         : RED")
print("Sidebar        : UNTOUCHED")
print("Dashboard      : UNTOUCHED")
print("Live market    : UNTOUCHED")
print("Backup         :", backup)
print("========================================")

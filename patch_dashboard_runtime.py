from pathlib import Path

FILE = Path("ui/pages/dashboard_page.py")

text = FILE.read_text(
    encoding="utf-8",
    errors="ignore",
)

# --------------------------------------------------------
# Import Runtime
# --------------------------------------------------------

import_marker = "from typing import"

runtime_import = """
from core.runtime import (
    get_runtime,
)

"""

if "get_runtime" not in text:

    pos = text.find(import_marker)

    if pos != -1:

        end = text.find("\n", pos)

        text = (
            text[: end + 1]
            + runtime_import
            + text[end + 1 :]
        )

# --------------------------------------------------------
# Runtime Helper
# --------------------------------------------------------

marker = """
    def update_live_scanner(
"""

helper = """
    # =====================================================
    # DASHBOARD SNAPSHOT
    # =====================================================

    def runtime_snapshot(
        self,
    ):

        return get_runtime().snapshot


"""

if helper not in text:

    text = text.replace(
        marker,
        helper + marker,
        1,
    )

FILE.write_text(
    text,
    encoding="utf-8",
)

print()

print("=" * 60)

print("Dashboard Runtime connected.")

print("=" * 60)
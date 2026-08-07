from pathlib import Path
from datetime import datetime
import shutil
import py_compile


ROOT = Path(__file__).resolve().parent

MOMENTUM = (
    ROOT
    / "core"
    / "scanners"
    / "momentum_scanner.py"
)

UI_APP = (
    ROOT
    / "ui"
    / "app.py"
)


def backup(path: Path, label: str) -> Path:
    stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    target = path.with_name(
        f"{path.stem}.before_{label}_{stamp}"
        f"{path.suffix}"
    )

    shutil.copy2(
        path,
        target,
    )

    return target


# =========================================================
# MOMENTUM DIAGNOSTIC
# =========================================================

momentum_text = MOMENTUM.read_text(
    encoding="utf-8"
)

momentum_backup = backup(
    MOMENTUM,
    "final_gate_diagnostic",
)


old = """        if score < self.minimum_score:
            return None

        if (
            confidence
            < self.minimum_confidence
        ):
            return None
"""


new = """        if score < self.minimum_score:

            print(
                "[MOMENTUM FINAL REJECT] "
                f"{symbol} | "
                f"{signal_type.value} | "
                f"SCORE | "
                f"score={score:.2f} | "
                f"minimum={self.minimum_score:.2f} | "
                f"confidence={confidence:.2f} | "
                f"breakdown={breakdown}"
            )

            return None

        if (
            confidence
            < self.minimum_confidence
        ):

            print(
                "[MOMENTUM FINAL REJECT] "
                f"{symbol} | "
                f"{signal_type.value} | "
                f"CONFIDENCE | "
                f"score={score:.2f} | "
                f"confidence={confidence:.2f} | "
                f"minimum={self.minimum_confidence:.2f} | "
                f"breakdown={breakdown}"
            )

            return None

        print(
            "[MOMENTUM SCORE PASS] "
            f"{symbol} | "
            f"{signal_type.value} | "
            f"score={score:.2f} | "
            f"confidence={confidence:.2f} | "
            f"breakdown={breakdown}"
        )
"""


if old not in momentum_text:
    raise RuntimeError(
        "Could not locate Momentum score/confidence "
        "gate. No changes made."
    )


momentum_text = momentum_text.replace(
    old,
    new,
    1,
)

MOMENTUM.write_text(
    momentum_text,
    encoding="utf-8",
)


# =========================================================
# UI FINAL SCORE DIAGNOSTIC
# =========================================================

ui_text = UI_APP.read_text(
    encoding="utf-8"
)

ui_backup = backup(
    UI_APP,
    "final_gate_diagnostic",
)


old_ui = """            if minimum_score > 0:
                opportunities = [
                    item
                    for item in opportunities
                    if float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ) >= minimum_score
                ]
"""


new_ui = """            if minimum_score > 0:

                print(
                    "[UI SCORE FILTER] "
                    f"Before={len(opportunities)} | "
                    f"Minimum={minimum_score:.2f}"
                )

                for item in opportunities:

                    print(
                        "[UI RAW SCORE] "
                        f"{item.get('symbol', item.get('stock', ''))} | "
                        f"signal={item.get('signal', '')} | "
                        f"scanner={item.get('scanner', item.get('strategy', ''))} | "
                        f"score={item.get('score', 0.0)} | "
                        f"confidence={item.get('confidence', 0.0)}"
                    )

                opportunities = [
                    item
                    for item in opportunities
                    if float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ) >= minimum_score
                ]

                print(
                    "[UI SCORE FILTER] "
                    f"After={len(opportunities)} | "
                    f"RejectedByScore="
                    f"{max(0, _ui_before_count - len(opportunities))}"
                )
"""


# Need count before filter.
new_ui = new_ui.replace(
    """                print(
                    "[UI SCORE FILTER] "
                    f"Before={len(opportunities)} | """,
    """                _ui_before_count = len(opportunities)

                print(
                    "[UI SCORE FILTER] "
                    f"Before={len(opportunities)} | """,
)


if old_ui not in ui_text:
    raise RuntimeError(
        "Could not locate UI minimum-score gate. "
        "Momentum diagnostic was installed, but "
        "UI diagnostic was not installed."
    )


ui_text = ui_text.replace(
    old_ui,
    new_ui,
    1,
)

UI_APP.write_text(
    ui_text,
    encoding="utf-8",
)


# =========================================================
# VALIDATE
# =========================================================

py_compile.compile(
    str(MOMENTUM),
    doraise=True,
)

py_compile.compile(
    str(UI_APP),
    doraise=True,
)


print("=" * 72)
print(
    "STOCKVERSITY FINAL-GATE RUNTIME "
    "DIAGNOSTIC INSTALLED"
)
print("=" * 72)

print("Momentum :", MOMENTUM)
print("Backup   :", momentum_backup)

print()

print("UI App   :", UI_APP)
print("Backup   :", ui_backup)

print()
print("Trading logic      : UNCHANGED")
print("Scanner thresholds : UNCHANGED")
print("Score thresholds   : UNCHANGED")
print("Signal generation  : UNCHANGED")
print("Diagnostic only    : ENABLED")
print()
print("Syntax validation: PASSED")
print("=" * 72)
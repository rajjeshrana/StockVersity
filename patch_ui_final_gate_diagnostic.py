from pathlib import Path
from datetime import datetime
import py_compile
import shutil

TARGET = Path(r"D:\StockVersityScanner\ui\app.py")

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

source = TARGET.read_text(encoding="utf-8")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = TARGET.with_name(
    f"app.before_ui_final_gate_diagnostic_{timestamp}.py"
)

shutil.copy2(TARGET, backup)

old = '''            minimum_score = float(
                filters.get(
                    "minimum_score",
                    0,
                )
                or 0
            )

            if minimum_score > 0:

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
'''

new = '''            # =========================================================
            # STOCKVERSITY FINAL UI GATE DIAGNOSTIC
            # Diagnostic only. No trading/filter logic changed.
            # =========================================================

            print(
                "[UI FINAL GATE] Before minimum-score filter:",
                len(opportunities),
            )

            if opportunities:

                diagnostic_scores = []

                for diagnostic_item in opportunities:

                    try:
                        diagnostic_score = float(
                            diagnostic_item.get(
                                "score",
                                0.0,
                            )
                            or 0.0
                        )

                    except Exception:
                        diagnostic_score = 0.0

                    diagnostic_scores.append(
                        diagnostic_score
                    )

                print(
                    "[UI FINAL GATE] Score range:"
                    f" min={min(diagnostic_scores):.2f}"
                    f" max={max(diagnostic_scores):.2f}"
                    f" avg={sum(diagnostic_scores) / len(diagnostic_scores):.2f}"
                )

                diagnostic_top = sorted(
                    opportunities,
                    key=lambda item: float(
                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ),
                    reverse=True,
                )[:10]

                for diagnostic_item in diagnostic_top:

                    print(
                        "[UI FINAL CANDIDATE]"
                        f" symbol={diagnostic_item.get('symbol', '')}"
                        f" signal={diagnostic_item.get('signal', '')}"
                        f" scanner={diagnostic_item.get('scanner', '')}"
                        f" score={float(diagnostic_item.get('score', 0.0) or 0.0):.2f}"
                        f" confidence={float(diagnostic_item.get('confidence', 0.0) or 0.0):.2f}"
                        f" rr={float(diagnostic_item.get('rr', 0.0) or 0.0):.2f}"
                    )

            minimum_score = float(
                filters.get(
                    "minimum_score",
                    0,
                )
                or 0
            )

            print(
                "[UI FINAL GATE] Requested minimum_score:",
                minimum_score,
            )

            before_minimum_score_count = len(
                opportunities
            )

            if minimum_score > 0:

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
                "[UI FINAL GATE] Minimum-score result:"
                f" before={before_minimum_score_count}"
                f" after={len(opportunities)}"
                f" rejected={before_minimum_score_count - len(opportunities)}"
            )
'''

if "[UI FINAL GATE] Before minimum-score filter:" in source:
    print(
        "[INFO] UI final-gate diagnostic already installed."
    )

else:

    count = source.count(old)

    if count != 1:
        raise RuntimeError(
            "Could not uniquely locate UI minimum-score block. "
            f"Matches found: {count}. No changes made."
        )

    source = source.replace(
        old,
        new,
        1,
    )

    TARGET.write_text(
        source,
        encoding="utf-8",
    )

py_compile.compile(
    str(TARGET),
    doraise=True,
)

print("=" * 72)
print("STOCKVERSITY UI FINAL-GATE DIAGNOSTIC INSTALLED")
print("=" * 72)
print("Target :", TARGET)
print("Backup :", backup)
print()
print("Trading logic      : UNCHANGED")
print("Scanner thresholds : UNCHANGED")
print("Minimum score      : UNCHANGED")
print("Direction filter   : UNCHANGED")
print("Diagnostic only    : ENABLED")
print()
print("Will report:")
print("  1. Opportunities before score filter")
print("  2. Score min/max/average")
print("  3. Top 10 candidate scores")
print("  4. Requested UI minimum score")
print("  5. Number rejected by score gate")
print()
print("Syntax validation: PASSED")
print("=" * 72)
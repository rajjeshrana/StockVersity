from pathlib import Path
from datetime import datetime
import py_compile
import shutil


TARGET = Path(r"D:\StockVersityScanner\ui\app.py")

if not TARGET.exists():
    raise FileNotFoundError(TARGET)


text = TARGET.read_text(
    encoding="utf-8"
)


# ============================================================
# BACKUP
# ============================================================

stamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

backup = TARGET.with_name(
    f"app.before_raw_score_gate_{stamp}.py"
)

shutil.copy2(
    TARGET,
    backup,
)


# ============================================================
# LOCATE SCORE / CONFIDENCE BLOCK
# ============================================================

old_score_block = '''                score = float(
                    getattr(
                        signal,
                        "score",
                        0.0,
                    )
                    or 0.0
                )

                confidence = float(
                    getattr(
                        signal,
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )

                if score <= 1.0 and score > 0:
                    score *= 100.0

                if confidence <= 1.0 and confidence > 0:
                    confidence *= 100.0
'''


new_score_block = '''                # -------------------------------------------------
                # SCORE MODEL
                # -------------------------------------------------
                #
                # signal.score:
                #     Weighted/ranked score produced by BaseScanner.
                #
                # metadata["raw_score"]:
                #     Original scanner qualification score before
                #     common weighted ranking.
                #
                # Keep both values separate.
                # -------------------------------------------------

                rank_score = float(
                    getattr(
                        signal,
                        "score",
                        0.0,
                    )
                    or 0.0
                )

                raw_score = float(
                    metadata.get(
                        "raw_score",
                        rank_score,
                    )
                    or rank_score
                    or 0.0
                )

                confidence = float(
                    getattr(
                        signal,
                        "confidence",
                        0.0,
                    )
                    or 0.0
                )

                if (
                    rank_score <= 1.0
                    and rank_score > 0
                ):
                    rank_score *= 100.0

                if (
                    raw_score <= 1.0
                    and raw_score > 0
                ):
                    raw_score *= 100.0

                if (
                    confidence <= 1.0
                    and confidence > 0
                ):
                    confidence *= 100.0

                # UI "score" represents setup qualification quality.
                # rank_score remains available separately for sorting.
                score = raw_score
'''


if old_score_block not in text:

    raise RuntimeError(
        "Could not locate the UI score conversion block. "
        "No changes made."
    )


text = text.replace(
    old_score_block,
    new_score_block,
    1,
)


# ============================================================
# ADD RANK SCORE TO OPPORTUNITY
# ============================================================

old_opportunity_score = '''                    "score": score,
                    "confidence": confidence,
'''


new_opportunity_score = '''                    "score": score,
                    "raw_score": raw_score,
                    "rank_score": rank_score,
                    "confidence": confidence,
'''


if old_opportunity_score not in text:

    raise RuntimeError(
        "Could not locate opportunity score fields. "
        "No changes made."
    )


text = text.replace(
    old_opportunity_score,
    new_opportunity_score,
    1,
)


# ============================================================
# SORTING
# ============================================================
#
# Qualification uses raw/setup score.
# Ordering uses weighted rank score.
#

old_sort = '''                        item.get(
                            "score",
                            0.0,
                        )
                        or 0.0
                    ),
                    float(
                        item.get(
                            "confidence",
'''


new_sort = '''                        item.get(
                            "rank_score",
                            item.get(
                                "score",
                                0.0,
                            ),
                        )
                        or 0.0
                    ),
                    float(
                        item.get(
                            "confidence",
'''


if old_sort not in text:

    raise RuntimeError(
        "Could not locate opportunity sorting block. "
        "No changes made."
    )


text = text.replace(
    old_sort,
    new_sort,
    1,
)


# ============================================================
# SAVE
# ============================================================

TARGET.write_text(
    text,
    encoding="utf-8",
)


# ============================================================
# VALIDATE
# ============================================================

py_compile.compile(
    str(TARGET),
    doraise=True,
)


print("=" * 72)
print(
    "STOCKVERSITY RAW SCORE UI GATE PATCH INSTALLED"
)
print("=" * 72)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print()
print(
    "Scanner trading logic : UNCHANGED"
)
print(
    "Scanner thresholds    : UNCHANGED"
)
print(
    "Signal generation     : UNCHANGED"
)
print(
    "Raw/setup score       : UI qualification"
)
print(
    "Weighted rank score   : sorting/ranking"
)
print()
print(
    "Syntax validation: PASSED"
)
print("=" * 72)
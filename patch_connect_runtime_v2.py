from pathlib import Path

APP = Path("ui/app.py")

text = APP.read_text(
    encoding="utf-8",
    errors="ignore",
)

marker = """
            # =========================================================
            # STOCKVERSITY FINAL UI GATE DIAGNOSTIC
"""

if marker not in text:
    raise RuntimeError(
        "Could not locate STOCKVERSITY FINAL UI GATE DIAGNOSTIC."
    )

insert = """
            # =========================================================
            # STOCKVERSITY RUNTIME
            # =========================================================

            try:

                from core.runtime import (
                    get_runtime,
                )

                runtime = get_runtime()

                runtime.publish(
                    opportunities
                )

            except Exception as runtime_error:

                print(
                    "[RUNTIME]",
                    runtime_error,
                )

"""

text = text.replace(
    marker,
    insert + marker,
    1,
)

APP.write_text(
    text,
    encoding="utf-8",
)

print()
print("====================================")
print("Runtime connected successfully.")
print("====================================")
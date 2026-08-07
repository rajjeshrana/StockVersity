from pathlib import Path

APP = Path("ui/app.py")

text = APP.read_text(encoding="utf-8")

marker = '''
print(
                "[UI FINAL GATE] Before minimum-score filter:",
'''

if marker not in text:
    raise RuntimeError(
        "Could not locate UI FINAL GATE block."
    )

insert = '''
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

'''

text = text.replace(
    marker,
    insert + marker,
    1,
)

APP.write_text(
    text,
    encoding="utf-8",
)

print(
    "\\nSUCCESS"
)

print(
    "Runtime connected."
)
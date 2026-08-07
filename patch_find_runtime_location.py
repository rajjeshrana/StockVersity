from pathlib import Path

text = Path("ui/app.py").read_text(
    encoding="utf-8",
    errors="ignore",
)

patterns = [
    "UI FINAL GATE",
    "minimum-score filter",
    "opportunities.append",
    "diagnostic_scores",
    "Raw signals:",
    "scanner_system.scan_now",
]

for p in patterns:

    print("\n" + "=" * 80)
    print("SEARCH:", p)
    print("=" * 80)

    pos = text.find(p)

    if pos == -1:
        print("NOT FOUND")
        continue

    start = max(0, pos - 400)
    end = min(len(text), pos + 700)

    print(text[start:end])
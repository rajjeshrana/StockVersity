from core.scanner.scanner_bootstrap import get_scanner_system
import inspect

s = get_scanner_system()
s.initialize()

print("=== REGISTERED SCANNERS ===")

for scanner in s.manager.scanners:
    print(
        type(scanner).__name__,
        "->",
        inspect.getfile(type(scanner)),
    )

print()
print("=== MOMENTUM DETAILS ===")

items = [
    scanner
    for scanner in s.manager.scanners
    if type(scanner).__name__ == "MomentumScanner"
]

print("COUNT:", len(items))

for scanner in items:
    print("CLASS:", type(scanner))
    print("FILE:", inspect.getfile(type(scanner)))
    print("SCAN FILE:", inspect.getsourcefile(scanner.scan))
    print(
        "SCAN FIRST LINE:",
        scanner.scan.__func__.__code__.co_firstlineno,
    )

    source = inspect.getsource(scanner.scan)

    print(
        "DIAGNOSTIC INSTALLED:",
        "MOMENTUM DIAGNOSTIC" in source,
    )

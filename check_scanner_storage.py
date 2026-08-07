from core.scanner.scanner_bootstrap import get_scanner_system
import inspect

s = get_scanner_system()
s.initialize()

m = s.manager

print("=== REGISTRY ===")
print("TYPE:", type(m.registry))
print("ATTRS:", [x for x in dir(m.registry) if not x.startswith("__")])
print("DICT:", getattr(m.registry, "__dict__", {}))

print()
print("=== ENGINE ===")
print("TYPE:", type(m.engine))
print("ATTRS:", [x for x in dir(m.engine) if not x.startswith("__")])
print("DICT:", getattr(m.engine, "__dict__", {}))

print()
print("=== MOMENTUM CLASS IMPORT ===")

from core.scanners.momentum_scanner import MomentumScanner

print("CLASS:", MomentumScanner)
print("FILE:", inspect.getfile(MomentumScanner))
print(
    "SCAN FIRST LINE:",
    MomentumScanner.scan.__code__.co_firstlineno,
)

source = inspect.getsource(MomentumScanner.scan)

print(
    "DIAGNOSTIC IN IMPORTED CLASS:",
    "MOMENTUM DIAGNOSTIC" in source,
)

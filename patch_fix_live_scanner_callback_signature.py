from pathlib import Path
from datetime import datetime
import shutil, py_compile, sys
TARGET=Path.cwd()/"core"/"data_manager.py"
if not TARGET.exists(): print(f"ERROR: {TARGET} not found"); sys.exit(1)
text=TARGET.read_text(encoding="utf-8")
old="""    def _forward_tick_to_scanner(
        self,
        tick,
    ) -> None:"""
new="""    def _forward_tick_to_scanner(
        self,
        instrument_key,
        tick,
    ) -> None:"""
anchor="""            if not quote:
                return

            scanner_system = get_scanner_system()"""
replacement="""            if not quote:
                return

            if instrument_key and not quote.get("instrument_key"):
                quote["instrument_key"] = instrument_key

            scanner_system = get_scanner_system()"""
if old not in text:
    if new in text:
        print("ALREADY INSTALLED"); py_compile.compile(str(TARGET),doraise=True); sys.exit(0)
    print("ERROR: callback signature block not found"); sys.exit(2)
if anchor not in text: print("ERROR: quote forwarding block not found"); sys.exit(3)
stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
backup=TARGET.with_name(f"data_manager.before_scanner_callback_signature_fix_{stamp}.py")
shutil.copy2(TARGET,backup)
TARGET.write_text(text.replace(old,new,1).replace(anchor,replacement,1),encoding="utf-8")
try: py_compile.compile(str(TARGET),doraise=True)
except Exception as exc:
    shutil.copy2(backup,TARGET); print(f"FAILED - restored: {exc}"); sys.exit(4)
print("="*68)
print("STOCKVERSITY LIVE SCANNER CALLBACK SIGNATURE FIX INSTALLED")
print("="*68)
print(f"Target : {TARGET}")
print(f"Backup : {backup}")
print("Changed: _forward_tick_to_scanner(self, tick)")
print("     to: _forward_tick_to_scanner(self, instrument_key, tick)")
print("Also preserves/injects instrument_key into the forwarded quote.")
print("Syntax validation: PASSED")
print("="*68)

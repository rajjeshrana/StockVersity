"""
=========================================================
StockVersity Scanner Pro
Scanner Integration Smoke Test
Version : 2.1
=========================================================

File:
    tests/test_scanner_integration.py

Purpose
-------
Verify the complete scanner initialization chain:

core.scanners
      ↓
ScannerRegistry
      ↓
ScannerBootstrap
      ↓
ScannerEngine
      ↓
Scanner Instances

This test does NOT require live Upstox market data.
=========================================================
"""

from __future__ import annotations

import sys
from pathlib import Path


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# =========================================================
# TEST HELPERS
# =========================================================

def heading(
    title: str,
) -> None:

    print()

    print(
        "=" * 70
    )

    print(
        title
    )

    print(
        "=" * 70
    )


def passed(
    message: str,
) -> None:

    print(
        f"[PASS] {message}"
    )


def failed(
    message: str,
) -> None:

    print(
        f"[FAIL] {message}"
    )


# =========================================================
# TEST SCANNER PACKAGE
# =========================================================

def test_scanner_package():

    heading(
        "1. SCANNER PACKAGE"
    )

    from core.scanners import (
        get_scanner_classes,
        get_scanner_names,
        validate_scanner_classes,
    )

    scanner_classes = (
        get_scanner_classes()
    )

    scanner_names = (
        get_scanner_names()
    )

    errors = (
        validate_scanner_classes()
    )

    print(
        "Scanner count:",
        len(scanner_classes),
    )

    for name in scanner_names:

        print(
            "  -",
            name,
        )

    assert scanner_classes, (
        "No scanner classes loaded."
    )

    assert not errors, (
        f"Scanner package errors: {errors}"
    )

    passed(
        "Scanner package loaded."
    )


# =========================================================
# TEST REGISTRY
# =========================================================

def test_registry():

    heading(
        "2. SCANNER REGISTRY"
    )

    from core.scanner.registry import (
        load_default_scanners,
    )

    registry = (
        load_default_scanners()
    )

    status = (
        registry.status()
    )

    print(
        "Registered:",
        status["registered"],
    )

    print(
        "Enabled:",
        status["enabled"],
    )

    print(
        "Disabled:",
        status["disabled"],
    )

    if status["errors"]:

        print(
            "Registry errors:"
        )

        for name, error in (
            status["errors"].items()
        ):

            print(
                f"  {name}: {error}"
            )

    assert status["registered"] > 0, (
        "Registry contains no scanners."
    )

    assert not status["errors"], (
        f"Registry errors: "
        f"{status['errors']}"
    )

    passed(
        "Scanner registry healthy."
    )


# =========================================================
# TEST SCANNER CREATION
# =========================================================

def test_scanner_creation():

    heading(
        "3. SCANNER INSTANCE CREATION"
    )

    from core.scanner.registry import (
        load_default_scanners,
    )

    registry = (
        load_default_scanners()
    )

    registry.clear_errors()

    scanners = (
        registry.create_all()
    )

    print(
        "Created instances:",
        len(scanners),
    )

    for scanner in scanners:

        print(
            "  -",
            scanner.__class__.__name__,
            "=>",
            scanner.name,
        )

    if registry.errors:

        print(
            "Creation errors:"
        )

        for name, error in (
            registry.errors.items()
        ):

            print(
                f"  {name}: {error}"
            )

    assert scanners, (
        "No scanner instances created."
    )

    assert not registry.errors, (
        f"Scanner creation errors: "
        f"{registry.errors}"
    )

    passed(
        "Scanner instances created."
    )


# =========================================================
# TEST BOOTSTRAP
# =========================================================

def test_bootstrap():

    heading(
        "4. SCANNER BOOTSTRAP"
    )

    from core.scanner.bootstrap import (
        ScannerBootstrap,
    )

    bootstrap = (
        ScannerBootstrap(
            parallel=False,
            debug=True,
        )
    )

    engine = (
        bootstrap.initialize()
    )

    status = (
        bootstrap.status()
    )

    print(
        "Initialized:",
        status["initialized"],
    )

    print(
        "Registry registered:",
        status["registry_registered"],
    )

    print(
        "Registry enabled:",
        status["registry_enabled"],
    )

    print(
        "Engine registered:",
        status["engine_registered"],
    )

    print(
        "Engine enabled:",
        status["engine_enabled"],
    )

    print(
        "Created instances:",
        status["created_instances"],
    )

    assert status[
        "initialized"
    ], (
        "Bootstrap did not initialize."
    )

    assert engine.scanners, (
        "Engine contains no scanners."
    )

    assert not bootstrap.validate(), (
        f"Bootstrap validation errors: "
        f"{bootstrap.validate()}"
    )

    passed(
        "Bootstrap initialized."
    )


# =========================================================
# TEST ENGINE
# =========================================================

def test_engine():

    heading(
        "5. SCANNER ENGINE"
    )

    from core.scanner.bootstrap import (
        ScannerBootstrap,
    )

    bootstrap = (
        ScannerBootstrap(
            parallel=False,
            debug=False,
        )
    )

    engine = (
        bootstrap.initialize()
    )

    info = (
        engine.info()
    )

    health = (
        engine.health_check()
    )

    print(
        "Engine:",
        info["engine"],
    )

    print(
        "Version:",
        info["version"],
    )

    print(
        "Registered:",
        info["registered"],
    )

    print(
        "Enabled:",
        info["enabled"],
    )

    print(
        "Healthy:",
        health["healthy"],
    )

    if health["issues"]:

        print(
            "Issues:"
        )

        for issue in (
            health["issues"]
        ):

            print(
                "  -",
                issue,
            )

    assert info[
        "registered"
    ] > 0

    assert info[
        "enabled"
    ] > 0

    assert health[
        "healthy"
    ], (
        f"Engine health failed: "
        f"{health['issues']}"
    )

    passed(
        "Scanner engine healthy."
    )


# =========================================================
# TEST REGISTRY / ENGINE MATCH
# =========================================================

def test_registry_engine_match():

    heading(
        "6. REGISTRY → ENGINE MATCH"
    )

    from core.scanner.bootstrap import (
        ScannerBootstrap,
    )

    bootstrap = (
        ScannerBootstrap(
            parallel=False,
        )
    )

    bootstrap.initialize()

    registry_names = set(
        bootstrap.registry.enabled_names
    )

    engine_class_names = {

        scanner.__class__.__name__

        for scanner in (
            bootstrap.engine.scanners.values()
        )

    }

    missing = (
        registry_names
        - engine_class_names
    )

    unexpected = (
        engine_class_names
        - registry_names
    )

    print(
        "Registry scanners:",
        len(registry_names),
    )

    print(
        "Engine scanners:",
        len(engine_class_names),
    )

    if missing:

        print(
            "Missing from engine:",
            sorted(missing),
        )

    if unexpected:

        print(
            "Unexpected in engine:",
            sorted(unexpected),
        )

    assert not missing, (
        f"Scanners missing from engine: "
        f"{sorted(missing)}"
    )

    assert not unexpected, (
        f"Unexpected engine scanners: "
        f"{sorted(unexpected)}"
    )

    passed(
        "Registry and engine match."
    )


# =========================================================
# RUN ALL TESTS
# =========================================================

def run_all_tests():

    heading(
        "STOCKVERSITY SCANNER PRO - SMOKE TEST"
    )

    tests = [

        test_scanner_package,

        test_registry,

        test_scanner_creation,

        test_bootstrap,

        test_engine,

        test_registry_engine_match,

    ]

    failures = []

    for test in tests:

        try:

            test()

        except Exception as exc:

            failed(
                f"{test.__name__}: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            failures.append(
                (
                    test.__name__,
                    exc,
                )
            )

    heading(
        "TEST RESULT"
    )

    total = len(
        tests
    )

    failed_count = len(
        failures
    )

    passed_count = (
        total
        - failed_count
    )

    print(
        "Total :",
        total,
    )

    print(
        "Passed:",
        passed_count,
    )

    print(
        "Failed:",
        failed_count,
    )

    if failures:

        print()

        print(
            "FAILED TESTS:"
        )

        for name, error in failures:

            print(
                f"  - {name}: "
                f"{type(error).__name__}: "
                f"{error}"
            )

        print()

        print(
            "SMOKE TEST: FAILED"
        )

        return False

    print()

    print(
        "SMOKE TEST: PASSED"
    )

    return True


# =========================================================
# DIRECT EXECUTION
# =========================================================

if __name__ == "__main__":

    success = (
        run_all_tests()
    )

    raise SystemExit(
        0
        if success
        else 1
    )


# =========================================================
# END OF FILE
# =========================================================
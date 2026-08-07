"""
==========================================================
StockVersity Scanner Pro
Dependency Container
Version : 4.0
Powered By : AI
==========================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from core.service_manager import ServiceManager
from backend.scanner.nse_data_engine import NSEDataEngine
from backend.scanner.scanner_executor import ScannerExecutor
from backend.ai.market_prediction_engine import MarketPredictionEngine
from backend.ai.market_sentiment_engine import MarketSentimentEngine
from backend.ai.market_regime_engine import MarketRegimeEngine

from backend.ai.pattern_recognition_engine import (
    PatternRecognitionEngine
)

from backend.ai.opportunity_ranker import (
    OpportunityRanker
)

from backend.ai.risk_management_engine import (
    RiskManagementEngine
)

from backend.ai.market_structure_engine import (
    MarketStructureEngine
)

from backend.ai.sector_rotation_engine import (
    SectorRotationEngine
)

from backend.ai.volume_analysis_engine import (
    VolumeAnalysisEngine
)


class DependencyContainer:

    """
    Singleton Dependency Container

    One instance of every engine
    throughout the application.
    """

    def __init__(self):

        self.logger = logging.getLogger(
            "DependencyContainer"
        )

        self._instances: Dict[str, Any] = {}

        self._build()

    # ===================================================
    # BUILD CONTAINER
    # ===================================================

    def _build(self):

        self.logger.info(
            "Creating Dependency Container..."
        )

        self.register(
            "service_manager",
            ServiceManager()
        )

        service = self.get(
            "service_manager"
        )

        controller = service.application

        self.register(
            "application_controller",
            controller
        )

        self.register(
            "nse_engine",
            controller.nse_engine
        )

        self.register(
            "scanner_executor",
            controller.scanner
        )

        self.register(
            "market_prediction",
            controller.market_prediction
        )

        self.register(
            "market_sentiment",
            controller.market_sentiment
        )

        self.register(
            "market_regime",
            controller.market_regime
        )

        self.register(
            "pattern_engine",
            controller.pattern_engine
        )

        self.register(
            "opportunity_ranker",
            controller.ranker
        )

        self.register(
            "risk_engine",
            controller.risk_engine
        )

        self.register(
            "market_structure",
            controller.structure_engine
        )

        self.register(
            "sector_rotation",
            controller.rotation_engine
        )

        self.register(
            "volume_engine",
            controller.volume_engine
        )

        self.logger.info(
            "Dependency Container Ready."
        )

    # ===================================================
    # REGISTER
    # ===================================================

    def register(

        self,

        name: str,

        instance: object

    ):

        self._instances[name] = instance

    # ===================================================
    # GET
    # ===================================================

    def get(

        self,

        name: str

    ):

        if name not in self._instances:

            raise KeyError(

                f"{name} not registered."

            )

        return self._instances[name]

    # ===================================================
    # EXISTS
    # ===================================================

    def exists(

        self,

        name: str

    ):

        return name in self._instances

    # ===================================================
    # REMOVE
    # ===================================================

    def remove(

        self,

        name: str

    ):

        if self.exists(name):

            del self._instances[name]

    # ===================================================
    # REGISTER INSTANCE
    # ===================================================

    def replace(

        self,

        name,

        instance

    ):

        self._instances[name] = instance

    # ===================================================
    # REGISTER MULTIPLE
    # ===================================================

    def register_many(
        self,
        instances: Dict[str, object]
    ):

        for name, instance in instances.items():

            self.register(name, instance)

        return True


    # ===================================================
    # GET ALL
    # ===================================================

    def all_instances(self):

        return self._instances


    # ===================================================
    # GET ALL NAMES
    # ===================================================

    def names(self):

        return list(

            self._instances.keys()

        )


    # ===================================================
    # TOTAL SERVICES
    # ===================================================

    def total(self):

        return len(

            self._instances

        )


    # ===================================================
    # APPLICATION
    # ===================================================

    @property
    def application(self):

        return self.get(

            "application_controller"

        )


    # ===================================================
    # SERVICE MANAGER
    # ===================================================

    @property
    def service_manager(self):

        return self.get(

            "service_manager"

        )


    # ===================================================
    # NSE ENGINE
    # ===================================================

    @property
    def nse_engine(self):

        return self.get(

            "nse_engine"

        )


    # ===================================================
    # SCANNER
    # ===================================================

    @property
    def scanner(self):

        return self.get(

            "scanner_executor"

        )


    # ===================================================
    # OPPORTUNITY RANKER
    # ===================================================

    @property
    def ranker(self):

        return self.get(

            "opportunity_ranker"

        )


    # ===================================================
    # VERIFY CONTAINER
    # ===================================================

    def verify(self):

        report = {}

        for name, instance in self._instances.items():

            report[name] = instance is not None

        return report


    # ===================================================
    # READY
    # ===================================================

    def ready(self):

        return all(

            self.verify().values()

        )


    # ===================================================
    # HEALTH REPORT
    # ===================================================

    def health(self):

        report = {}

        for name, instance in self._instances.items():

            try:

                if hasattr(instance, "health"):

                    report[name] = instance.health()

                elif hasattr(instance, "health_status"):

                    report[name] = instance.health_status()

                else:

                    report[name] = {

                        "status": "OK"

                    }

            except Exception as e:

                report[name] = {

                    "status": "ERROR",

                    "message": str(e)

                }

        return report


    # ===================================================
    # DIAGNOSTICS
    # ===================================================

    def diagnostics(self):

        return {

            "total_instances":

                self.total(),

            "registered":

                self.names(),

            "verification":

                self.verify(),

            "health":

                self.health()

        }


    # ===================================================
    # START APPLICATION
    # ===================================================

    def start(self):

        self.logger.info(

            "Starting Service Manager..."

        )

        self.service_manager.start_all()


    # ===================================================
    # STOP APPLICATION
    # ===================================================

    def stop(self):

        self.logger.info(

            "Stopping Service Manager..."

        )

        self.service_manager.stop_all()


    # ===================================================
    # RESTART APPLICATION
    # ===================================================

    def restart(self):

        self.logger.info(

            "Restarting Application..."

        )

        self.stop()

        self.start()


    # ===================================================
    # RESET
    # ===================================================

    def reset(self):

        self.service_manager.reset()


    # ===================================================
    # CLEAR CACHE
    # ===================================================

    def clear_cache(self):

        self.service_manager.clear_cache()


# ==========================================================
# GLOBAL DEPENDENCY CONTAINER
# ==========================================================
_container = None


def get_container() -> DependencyContainer:
    """
    Return the global DependencyContainer instance.

    The container is created lazily on first access so that
    importing this module does not immediately initialize
    the complete StockVersity backend.
    """

    global _container

    if _container is None:
        _container = DependencyContainer()

    return _container
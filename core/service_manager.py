"""
============================================================
StockVersity Scanner Pro
Service Manager
Version : 4.0
Powered By : AI
============================================================
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal

from core.application_controller import ApplicationController


class ServiceManager(QObject):

    # -----------------------------------------------------
    # Signals
    # -----------------------------------------------------

    statusChanged = Signal(str)

    serviceStarted = Signal(str)

    serviceStopped = Signal(str)

    serviceFailed = Signal(str)

    allServicesStarted = Signal()

    allServicesStopped = Signal()

    # -----------------------------------------------------

    def __init__(self):

        super().__init__()

        self.logger = logging.getLogger("ServiceManager")

        self.running = False

        self.controller: Optional[ApplicationController] = None

        self.monitor_thread = None

        self.stop_event = threading.Event()

        self.services: Dict[str, object] = {}

        self.service_status: Dict[str, bool] = {}

        self.initialize_services()

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize_services(self):

        self.statusChanged.emit(

            "Initializing Services..."

        )

        self.controller = ApplicationController()

        self.services = {

            "ApplicationController": self.controller,

            "NSEDataEngine": self.controller.nse_engine,

            "ScannerExecutor": self.controller.scanner,

            "OpportunityRanker": self.controller.ranker,

            "MarketPrediction": self.controller.market_prediction,

            "MarketSentiment": self.controller.market_sentiment,

            "MarketRegime": self.controller.market_regime,

            "PatternRecognition": self.controller.pattern_engine,

            "RiskManagement": self.controller.risk_engine,

            "MarketStructure": self.controller.structure_engine,

            "VolumeAnalysis": self.controller.volume_engine,

            "SectorRotation": self.controller.rotation_engine

        }

        for name in self.services:

            self.service_status[name] = False

    # =====================================================
    # START ALL
    # =====================================================

    def start_all(self):

        if self.running:

            return

        self.running = True

        self.stop_event.clear()

        self.statusChanged.emit(

            "Starting Services..."

        )

        try:

            self.controller.start()

            for name in self.services:

                self.service_status[name] = True

                self.serviceStarted.emit(name)

            self.monitor_thread = threading.Thread(

                target=self.monitor_services,

                daemon=True

            )

            self.monitor_thread.start()

            self.allServicesStarted.emit()

            self.statusChanged.emit(

                "All Services Started"

            )

        except Exception as e:

            self.logger.exception(e)

            self.serviceFailed.emit(

                str(e)

            )

    # =====================================================
    # STOP ALL
    # =====================================================

    def stop_all(self):

        if not self.running:

            return

        self.running = False

        self.stop_event.set()

        try:

            self.controller.stop()

        except Exception:

            pass

        for name in self.services:

            self.service_status[name] = False

            self.serviceStopped.emit(name)

        self.allServicesStopped.emit()

        self.statusChanged.emit(

            "All Services Stopped"

        )

    # =====================================================
    # START ONE SERVICE
    # =====================================================

    def start_service(

        self,

        service_name: str

    ):

        if service_name not in self.services:

            return False

        self.service_status[service_name] = True

        self.serviceStarted.emit(

            service_name

        )

        return True

    # =====================================================
    # STOP ONE SERVICE
    # =====================================================

    def stop_service(

        self,

        service_name: str

    ):

        if service_name not in self.services:

            return False

        self.service_status[service_name] = False

        self.serviceStopped.emit(

            service_name

        )

        return True
    # =====================================================
# SERVICE MONITOR
# =====================================================

    def monitor_services(self):

        self.logger.info("Service Monitor Started")

        while not self.stop_event.is_set():

            try:

                self.check_all_services()

                self.auto_recovery()

                time.sleep(5)

            except Exception as e:

                self.logger.exception(e)

                self.serviceFailed.emit(str(e))

        self.logger.info("Service Monitor Stopped")


# =====================================================
# CHECK ALL SERVICES
# =====================================================

    def check_all_services(self):

        for name, service in self.services.items():

            try:

                healthy = self.is_service_alive(service)

                self.service_status[name] = healthy

                if not healthy:

                    self.serviceFailed.emit(name)

            except Exception:

                self.service_status[name] = False

                self.serviceFailed.emit(name)


# =====================================================
# CHECK SINGLE SERVICE
# =====================================================

    def is_service_alive(self, service):

        if service is None:

            return False

        if hasattr(service, "running"):

            return bool(service.running)

        return True


# =====================================================
# AUTO RECOVERY
# =====================================================

    def auto_recovery(self):

        for name, status in self.service_status.items():

            if status:

                continue

            self.logger.warning(

                f"Recovering {name}"

            )

            self.restart_service(name)


# =====================================================
# RESTART SERVICE
# =====================================================

    def restart_service(self, service_name):

        try:

            if service_name == "ApplicationController":

                self.controller.stop()

                time.sleep(2)

                self.controller.start()

                self.service_status[service_name] = True

                self.serviceStarted.emit(service_name)

                return

            service = self.services.get(service_name)

            if service is None:

                return

            if hasattr(service, "initialize"):

                service.initialize()

            elif hasattr(service, "startup"):

                service.startup()

            elif hasattr(service, "connect"):

                service.connect()

            self.service_status[service_name] = True

            self.serviceStarted.emit(service_name)

        except Exception as e:

            self.logger.exception(e)

            self.service_status[service_name] = False

            self.serviceFailed.emit(service_name)


# =====================================================
# SERVICE HEALTH
# =====================================================

    def health(self):

        result = {}

        for name in self.services:

            result[name] = {

                "running": self.service_status[name]

            }

        return result


# =====================================================
# SERVICE COUNT
# =====================================================

    def total_services(self):

        return len(self.services)


# =====================================================
# RUNNING SERVICES
# =====================================================

    def running_services(self):

        return sum(

            self.service_status.values()

        )


# =====================================================
# FAILED SERVICES
# =====================================================

    def failed_services(self):

        return [

            name

            for name, status

            in self.service_status.items()

            if not status

        ]


# =====================================================
# SERVICE SUMMARY
# =====================================================

    def service_summary(self):

        return {

            "total":

                self.total_services(),

            "running":

                self.running_services(),

            "failed":

                len(

                    self.failed_services()

                ),

            "services":

                self.service_status.copy()

        }


# =====================================================
# PRINT SUMMARY
# =====================================================

    def print_summary(self):

        summary = self.service_summary()

        self.logger.info(summary)

        return summary
    # =====================================================
# VERIFY DEPENDENCIES
# =====================================================

    def verify_dependencies(self):

        report = {}

        for name, service in self.services.items():

            report[name] = service is not None

        return report


# =====================================================
# VERIFY SYSTEM
# =====================================================

    def verify_system(self):

        dependencies = self.verify_dependencies()

        health = self.health()

        return {

            "dependencies": dependencies,

            "health": health,

            "ready": all(dependencies.values())

        }


# =====================================================
# CONTROLLER
# =====================================================

    @property
    def application(self):

        return self.controller


# =====================================================
# MANUAL SCAN
# =====================================================

    def manual_scan(self):

        if not self.running:

            return

        self.controller.manual_scan()


# =====================================================
# REFRESH DASHBOARD
# =====================================================

    def refresh_dashboard(self):

        self.controller.refresh_dashboard()


# =====================================================
# FULL REFRESH
# =====================================================

    def full_refresh(self):

        self.controller.full_refresh()


# =====================================================
# EXPORT DASHBOARD
# =====================================================

    def dashboard(self):

        return self.controller.export_dashboard()


# =====================================================
# EXPORT OPPORTUNITIES
# =====================================================

    def opportunities(self):

        return self.controller.export_opportunities()


# =====================================================
# MARKET SUMMARY
# =====================================================

    def market_summary(self):

        return self.controller.market_summary()


# =====================================================
# PERFORMANCE
# =====================================================

    def performance(self):

        try:

            return self.controller.performance_metrics()

        except Exception:

            return {}


# =====================================================
# APPLICATION STATUS
# =====================================================

    def application_status(self):

        return self.controller.application_status()


# =====================================================
# THREAD INFORMATION
# =====================================================

    def thread_information(self):

        return self.controller.thread_status()


# =====================================================
# DIAGNOSTICS
# =====================================================

    def diagnostics(self):

        return {

            "application":

                self.application_status(),

            "performance":

                self.performance(),

            "services":

                self.service_summary(),

            "health":

                self.health(),

            "threads":

                self.thread_information()

        }


# =====================================================
# LOG DIAGNOSTICS
# =====================================================

    def log_diagnostics(self):

        report = self.diagnostics()

        self.logger.info(report)

        return report


# =====================================================
# RESTART EVERYTHING
# =====================================================

    def restart_all(self):

        self.stop_all()

        time.sleep(2)

        self.start_all()


# =====================================================
# CLEAR SESSION
# =====================================================

    def reset(self):

        self.controller.reset_session()


# =====================================================
# CACHE CLEAR
# =====================================================

    def clear_cache(self):

        self.controller.clear_cache()


# =====================================================
# SAVE SESSION
# =====================================================

    def save(self):

        self.controller.save_session()


# =====================================================
# LOAD SESSION
# =====================================================

    def load(self):

        self.controller.load_session()
        # =====================================================
# SHUTDOWN
# =====================================================

    def shutdown(self):

        self.statusChanged.emit(

            "Shutting Down Services..."

        )

        try:

            self.stop_all()

            if self.monitor_thread:

                self.monitor_thread.join(timeout=5)

        except Exception as e:

            self.logger.exception(e)

        self.statusChanged.emit(

            "Shutdown Complete."

        )


# =====================================================
# APPLICATION INFORMATION
# =====================================================

    @property
    def application_name(self):

        return "StockVersity Scanner Pro"


    @property
    def version(self):

        return "4.0"


    @property
    def build(self):

        return "Production"


# =====================================================
# BUILD INFO
# =====================================================

    def build_information(self):

        return {

            "application":

                self.application_name,

            "version":

                self.version,

            "build":

                self.build,

            "python":

                "3.14",

            "framework":

                "PySide6"

        }


# =====================================================
# RUNTIME INFORMATION
# =====================================================

    def runtime_information(self):

        return {

            "running":

                self.running,

            "started":

                datetime.now(),

            "threads":

                threading.active_count(),

            "services":

                self.service_summary(),

            "application":

                self.application_status()

        }


# =====================================================
# SYSTEM INFORMATION
# =====================================================

    def system_information(self):

        return {

            "build":

                self.build_information(),

            "runtime":

                self.runtime_information(),

            "diagnostics":

                self.diagnostics()

        }


# =====================================================
# LOG SYSTEM INFORMATION
# =====================================================

    def log_system_information(self):

        report = self.system_information()

        self.logger.info(report)

        return report


# =====================================================
# VERIFY APPLICATION
# =====================================================

    def verify(self):

        return {

            "services":

                self.verify_dependencies(),

            "controller":

                self.controller.verify_application(),

            "ready":

                self.controller.verify_application()

        }


# =====================================================
# APPLICATION READY
# =====================================================

    def ready(self):

        return self.verify()["ready"]


# =====================================================
# CONTEXT MANAGER
# =====================================================

    def __enter__(self):

        self.start_all()

        return self


    def __exit__(

        self,

        exc_type,

        exc_value,

        traceback

    ):

        self.shutdown()


# =====================================================
# STRING REPRESENTATION
# =====================================================

    def __repr__(self):

        return (

            f"<ServiceManager "

            f"running={self.running} "

            f"services={self.running_services()}/"

            f"{self.total_services()}>"

        )


# =====================================================
# END OF FILE
# =====================================================

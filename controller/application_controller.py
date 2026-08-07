from __future__ import annotations

import logging
import threading
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any

from core.upstox_client import UpstoxClient
from core.data_manager import DataManager
from core.market_analyzer import MarketAnalyzer
from core.screener_engine import ScreenerEngine
from core.alert_manager import AlertManager

from services.scanner_service import ScannerService
from services.websocket_service import WebSocketService

from ui.dashboard import DashboardWindow
from ui.login_window import LoginWindow
from ui.splash_screen import SplashScreen


# ==========================================================
# APPLICATION STATE
# ==========================================================

class ApplicationState(Enum):

    STARTING = "Starting"

    SPLASH = "Splash"

    LOGIN = "Login"

    CONNECTING = "Connecting"

    INITIALIZING = "Initializing"

    READY = "Ready"

    RUNNING = "Running"

    STOPPING = "Stopping"

    CLOSED = "Closed"


# ==========================================================
# APPLICATION CONTROLLER
# ==========================================================

class ApplicationController:

    VERSION = "1.0.0"

    APP_NAME = "StockVersity Scanner Pro"

    def __init__(self):

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.lock = threading.RLock()

        self.state = ApplicationState.STARTING

        self.started = datetime.now()

        # -----------------------------------------
        # Core Components
        # -----------------------------------------

        self.upstox: Optional[
            UpstoxClient
        ] = None

        self.data_manager: Optional[
            DataManager
        ] = None

        self.market_analyzer: Optional[
            MarketAnalyzer
        ] = None

        self.screener: Optional[
            ScreenerEngine
        ] = None

        self.alert_manager: Optional[
            AlertManager
        ] = None

        # -----------------------------------------
        # Services
        # -----------------------------------------

        self.scanner_service: Optional[
            ScannerService
        ] = None

        self.websocket_service: Optional[
            WebSocketService
        ] = None

        # -----------------------------------------
        # UI
        # -----------------------------------------

        self.splash: Optional[
            SplashScreen
        ] = None

        self.login: Optional[
            LoginWindow
        ] = None

        self.dashboard: Optional[
            DashboardWindow
        ] = None

        self.logger.info(
            "%s initialized.",
            self.APP_NAME,
        )
            # ==========================================================
    # APPLICATION STARTUP
    # ==========================================================

    def start(self) -> None:
        """
        Entry point for the application.
        """

        self.logger.info(
            "Starting %s...",
            self.APP_NAME,
        )

        self.change_state(
            ApplicationState.SPLASH
        )

        self.show_splash()

    # ==========================================================
    # STATE MANAGEMENT
    # ==========================================================

    def change_state(
        self,
        state: ApplicationState,
    ) -> None:
        """
        Update application state.
        """

        self.logger.info(

            "Application State: %s -> %s",

            self.state.value,

            state.value,

        )

        self.state = state

    # ==========================================================
    # SPLASH
    # ==========================================================

    def show_splash(self) -> None:
        """
        Display splash screen.
        """

        self.splash = SplashScreen()

        self.splash.show()

    def close_splash(self) -> None:
        """
        Close splash screen.
        """

        if self.splash:

            self.splash.close()

            self.splash = None

    # ==========================================================
    # LOGIN
    # ==========================================================

    def show_login(self) -> None:
        """
        Display login window.
        """

        self.change_state(
            ApplicationState.LOGIN
        )

        self.close_splash()

        self.login = LoginWindow()

        self.login.login_success.connect(
            self.on_login_success
        )

        self.login.login_cancelled.connect(
            self.shutdown
        )

        self.login.show()

    def close_login(self) -> None:
        """
        Close login window.
        """

        if self.login:

            self.login.close()

            self.login = None

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def show_dashboard(self) -> None:
        """
        Open dashboard.
        """

        self.change_state(
            ApplicationState.RUNNING
        )

        self.dashboard = DashboardWindow()

        self.dashboard.show()

    def close_dashboard(self) -> None:
        """
        Close dashboard.
        """

        if self.dashboard:

            self.dashboard.close()

            self.dashboard = None

    # ==========================================================
    # LOGIN CALLBACK
    # ==========================================================

    def on_login_success(
        self,
        client: UpstoxClient,
    ) -> None:
        """
        Login completed successfully.
        """

        self.logger.info(
            "User authenticated."
        )

        self.upstox = client

        self.close_login()

        self.initialize_components()

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def initialize_components(
        self,
    ) -> None:
        """
        Create all core objects.
        """

        self.change_state(
            ApplicationState.INITIALIZING
        )

        self.data_manager = DataManager(
            self.upstox
        )

        self.market_analyzer = MarketAnalyzer(
            self.data_manager
        )

        self.screener = ScreenerEngine(
            self.data_manager,
            self.market_analyzer,
        )

        self.alert_manager = AlertManager(
            self.market_analyzer
        )

        self.initialize_services()

    # ==========================================================
    # INITIALIZE SERVICES
    # ==========================================================

    def initialize_services(
        self,
    ) -> None:
        """
        Create background services.
        """

        self.scanner_service = ScannerService(

            screener=self.screener,

            alerts=self.alert_manager,

        )

        self.websocket_service = WebSocketService(

            upstox=self.upstox,

            data_manager=self.data_manager,

        )

        self.change_state(
            ApplicationState.READY
        )

        self.start_services()

    # ==========================================================
    # START SERVICES
    # ==========================================================

    def start_services(
        self,
    ) -> None:
        """
        Start all background services.
        """

        self.websocket_service.start()

        self.scanner_service.start()

        self.show_dashboard()
            # ==========================================================
    # COMPONENT INITIALIZATION
    # ==========================================================

    def initialize_core(self) -> None:
        """
        Initialize all core modules.
        """

        self.logger.info(
            "Initializing core modules..."
        )

        if self.upstox is None:
            raise RuntimeError(
                "Upstox client is not available."
            )

        # -----------------------------------------
        # Data Manager
        # -----------------------------------------

        self.data_manager = DataManager(
            upstox_client=self.upstox
        )

        self.logger.info(
            "DataManager initialized."
        )

        # -----------------------------------------
        # Market Analyzer
        # -----------------------------------------

        self.market_analyzer = MarketAnalyzer(
            data_manager=self.data_manager
        )

        self.logger.info(
            "MarketAnalyzer initialized."
        )

        # -----------------------------------------
        # Screener Engine
        # -----------------------------------------

        self.screener = ScreenerEngine(
            data_manager=self.data_manager,
            market_analyzer=self.market_analyzer,
        )

        self.logger.info(
            "ScreenerEngine initialized."
        )

        # -----------------------------------------
        # Alert Manager
        # -----------------------------------------

        self.alert_manager = AlertManager(
            market_analyzer=self.market_analyzer
        )

        self.logger.info(
            "AlertManager initialized."
        )

        self.initialize_services()

    # ==========================================================
    # LOAD CONFIGURATION
    # ==========================================================

    def load_configuration(self) -> None:
        """
        Load application configuration.
        """

        self.logger.info(
            "Loading configuration..."
        )

        self.config: Dict[str, Any] = {

            "theme": "Dark",

            "market": "NSE",

            "refresh_interval": 5,

            "scanner_interval": 60,

            "alerts_enabled": True,

            "auto_connect": True,

            "auto_scan": True,

            "log_level": "INFO",

        }

        self.logger.info(
            "Configuration loaded."
        )

    # ==========================================================
    # DEPENDENCY CHECK
    # ==========================================================

    def verify_dependencies(self) -> None:
        """
        Verify initialized modules.
        """

        modules = {

            "Upstox": self.upstox,

            "DataManager": self.data_manager,

            "MarketAnalyzer": self.market_analyzer,

            "ScreenerEngine": self.screener,

            "AlertManager": self.alert_manager,

        }

        missing = []

        for name, module in modules.items():

            if module is None:

                missing.append(name)

        if missing:

            raise RuntimeError(

                "Missing modules: "

                + ", ".join(missing)

            )

        self.logger.info(
            "Dependency verification successful."
        )

    # ==========================================================
    # CONNECT MODULES
    # ==========================================================

    def connect_modules(self) -> None:
        """
        Establish communication between modules.
        """

        self.logger.info(
            "Connecting modules..."
        )

        self.market_analyzer.set_alert_manager(
            self.alert_manager
        )

        self.screener.set_alert_manager(
            self.alert_manager
        )

        self.screener.set_market_analyzer(
            self.market_analyzer
        )

        self.logger.info(
            "Modules connected."
        )

    # ==========================================================
    # INITIALIZATION COMPLETE
    # ==========================================================

    def finish_initialization(self) -> None:

        self.verify_dependencies()

        self.connect_modules()

        self.change_state(
            ApplicationState.READY
        )

        self.logger.info(
            "Initialization completed successfully."
        )

        self.start_services()
            # ==========================================================
    # COMPONENT INITIALIZATION
    # ==========================================================

    def initialize_core(self) -> None:
        """
        Initialize all core modules.
        """

        self.logger.info(
            "Initializing core modules..."
        )

        if self.upstox is None:
            raise RuntimeError(
                "Upstox client is not available."
            )

        # -----------------------------------------
        # Data Manager
        # -----------------------------------------

        self.data_manager = DataManager(
            upstox_client=self.upstox
        )

        self.logger.info(
            "DataManager initialized."
        )

        # -----------------------------------------
        # Market Analyzer
        # -----------------------------------------

        self.market_analyzer = MarketAnalyzer(
            data_manager=self.data_manager
        )

        self.logger.info(
            "MarketAnalyzer initialized."
        )

        # -----------------------------------------
        # Screener Engine
        # -----------------------------------------

        self.screener = ScreenerEngine(
            data_manager=self.data_manager,
            market_analyzer=self.market_analyzer,
        )

        self.logger.info(
            "ScreenerEngine initialized."
        )

        # -----------------------------------------
        # Alert Manager
        # -----------------------------------------

        self.alert_manager = AlertManager(
            market_analyzer=self.market_analyzer
        )

        self.logger.info(
            "AlertManager initialized."
        )

        self.initialize_services()

    # ==========================================================
    # LOAD CONFIGURATION
    # ==========================================================

    def load_configuration(self) -> None:
        """
        Load application configuration.
        """

        self.logger.info(
            "Loading configuration..."
        )

        self.config: Dict[str, Any] = {

            "theme": "Dark",

            "market": "NSE",

            "refresh_interval": 5,

            "scanner_interval": 60,

            "alerts_enabled": True,

            "auto_connect": True,

            "auto_scan": True,

            "log_level": "INFO",

        }

        self.logger.info(
            "Configuration loaded."
        )

    # ==========================================================
    # DEPENDENCY CHECK
    # ==========================================================

    def verify_dependencies(self) -> None:
        """
        Verify initialized modules.
        """

        modules = {

            "Upstox": self.upstox,

            "DataManager": self.data_manager,

            "MarketAnalyzer": self.market_analyzer,

            "ScreenerEngine": self.screener,

            "AlertManager": self.alert_manager,

        }

        missing = []

        for name, module in modules.items():

            if module is None:

                missing.append(name)

        if missing:

            raise RuntimeError(

                "Missing modules: "

                + ", ".join(missing)

            )

        self.logger.info(
            "Dependency verification successful."
        )

    # ==========================================================
    # CONNECT MODULES
    # ==========================================================

    def connect_modules(self) -> None:
        """
        Establish communication between modules.
        """

        self.logger.info(
            "Connecting modules..."
        )

        self.market_analyzer.set_alert_manager(
            self.alert_manager
        )

        self.screener.set_alert_manager(
            self.alert_manager
        )

        self.screener.set_market_analyzer(
            self.market_analyzer
        )

        self.logger.info(
            "Modules connected."
        )

    # ==========================================================
    # INITIALIZATION COMPLETE
    # ==========================================================

    def finish_initialization(self) -> None:

        self.verify_dependencies()

        self.connect_modules()

        self.change_state(
            ApplicationState.READY
        )

        self.logger.info(
            "Initialization completed successfully."
        )

        self.start_services()
            # ==========================================================
    # LOGOUT
    # ==========================================================

    def logout(self) -> None:
        """
        Logout current user.
        """

        self.logger.info("Logging out user...")

        self.stop_services()

        self.close_dashboard()

        if self.upstox:

            try:

                self.upstox.logout()

            except Exception as ex:

                self.logger.exception(ex)

        self.upstox = None

        self.data_manager = None
        self.market_analyzer = None
        self.screener = None
        self.alert_manager = None

        self.change_state(
            ApplicationState.LOGIN
        )

        self.show_login()

    # ==========================================================
    # RESTART APPLICATION
    # ==========================================================

    def restart(self) -> None:
        """
        Restart application.
        """

        self.logger.info(
            "Restarting application..."
        )

        self.stop_services()

        self.close_dashboard()

        self.upstox = None

        self.change_state(
            ApplicationState.STARTING
        )

        self.start()

    # ==========================================================
    # RECONNECT
    # ==========================================================

    def reconnect(self) -> bool:
        """
        Attempt to reconnect.
        """

        self.logger.info(
            "Reconnecting..."
        )

        if self.upstox is None:
            return False

        try:

            connected = self.upstox.connect()

            if connected:

                self.logger.info(
                    "Reconnect successful."
                )

                if self.websocket_service:

                    self.websocket_service.start()

                return True

        except Exception as ex:

            self.logger.exception(ex)

        return False

    # ==========================================================
    # CONNECTION STATUS
    # ==========================================================

    def is_connected(self) -> bool:

        if self.upstox is None:
            return False

        try:

            return self.upstox.is_connected()

        except Exception:

            return False

    # ==========================================================
    # SESSION STATUS
    # ==========================================================

    def session_info(self) -> Dict[str, Any]:
        """
        Return current session details.
        """

        return {

            "logged_in": self.upstox is not None,

            "connected": self.is_connected(),

            "state": self.state.value,

            "started": self.started,

        }

    # ==========================================================
    # GLOBAL ERROR HANDLER
    # ==========================================================

    def handle_exception(
        self,
        exception: Exception,
    ) -> None:
        """
        Global exception handler.
        """

        self.logger.exception(exception)

        if self.dashboard:

            try:

                self.dashboard.show_error(
                    str(exception)
                )

            except Exception:

                pass

    # ==========================================================
    # SAFE EXECUTION
    # ==========================================================

    def execute(
        self,
        func,
        *args,
        **kwargs,
    ):
        """
        Execute safely.
        """

        try:

            return func(
                *args,
                **kwargs,
            )

        except Exception as ex:

            self.handle_exception(ex)

            return None

    # ==========================================================
    # TOKEN REFRESH
    # ==========================================================

    def refresh_session(self) -> bool:
        """
        Refresh API session.
        """

        if self.upstox is None:
            return False

        try:

            return self.upstox.refresh_session()

        except Exception as ex:

            self.logger.exception(ex)

            return False
            # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Perform application health check.
        """

        health = {

            "application": self.APP_NAME,

            "version": self.VERSION,

            "state": self.state.value,

            "timestamp": datetime.now(),

            "components": {},

            "healthy": True,

        }

        components = {

            "upstox": self.upstox,

            "data_manager": self.data_manager,

            "market_analyzer": self.market_analyzer,

            "screener": self.screener,

            "alert_manager": self.alert_manager,

            "scanner_service": self.scanner_service,

            "websocket_service": self.websocket_service,

        }

        for name, component in components.items():

            status = component is not None

            health["components"][name] = status

            if not status:

                health["healthy"] = False

        return health

    # ==========================================================
    # APPLICATION INFORMATION
    # ==========================================================

    def application_info(self) -> Dict[str, Any]:

        uptime = datetime.now() - self.started

        return {

            "name": self.APP_NAME,

            "version": self.VERSION,

            "state": self.state.value,

            "uptime": str(uptime),

            "started": self.started,

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Collect diagnostics from all modules.
        """

        report = {

            "application": self.application_info(),

            "health": self.health_check(),

        }

        try:

            if self.market_analyzer:

                report["market"] = (

                    self.market_analyzer.diagnostics()

                )

        except Exception as ex:

            self.logger.exception(ex)

        try:

            if self.screener:

                report["scanner"] = (

                    self.screener.diagnostics()

                )

        except Exception as ex:

            self.logger.exception(ex)

        try:

            if self.alert_manager:

                report["alerts"] = (

                    self.alert_manager.diagnostics()

                )

        except Exception as ex:

            self.logger.exception(ex)

        return report

    # ==========================================================
    # RELOAD CONFIGURATION
    # ==========================================================

    def reload_configuration(self) -> None:
        """
        Reload application configuration.
        """

        self.logger.info(
            "Reloading configuration..."
        )

        self.load_configuration()

        self.logger.info(
            "Configuration reloaded."
        )

    # ==========================================================
    # UPDATE DASHBOARD STATUS
    # ==========================================================

    def update_statusbar(self) -> None:
        """
        Push current status to dashboard.
        """

        if self.dashboard is None:
            return

        try:

            self.dashboard.update_status(

                self.application_info()

            )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # PERIODIC MAINTENANCE
    # ==========================================================

    def maintenance(self) -> None:
        """
        Periodic maintenance task.
        """

        self.logger.debug(
            "Running maintenance..."
        )

        self.update_statusbar()

        self.heartbeat()

    # ==========================================================
    # DEBUG REPORT
    # ==========================================================

    def debug_report(self) -> Dict[str, Any]:

        return {

            "status": self.get_status(),

            "health": self.health_check(),

            "diagnostics": self.diagnostics(),

        }

    # ==========================================================
    # LOG APPLICATION STATUS
    # ==========================================================

    def log_status(self) -> None:

        self.logger.info(

            "Application Status: %s",

            self.get_status(),

        )
            # ==========================================================
    # SHUTDOWN
    # ==========================================================

    def shutdown(self) -> None:
        """
        Gracefully shutdown the application.
        """

        self.logger.info(
            "Application shutdown initiated."
        )

        self.change_state(
            ApplicationState.STOPPING
        )

        try:

            self.stop_services()

            self.cleanup()

        except Exception as ex:

            self.logger.exception(ex)

        finally:

            self.close_dashboard()

            self.close_login()

            self.close_splash()

            self.change_state(
                ApplicationState.CLOSED
            )

            self.logger.info(
                "Application closed successfully."
            )

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def cleanup(self) -> None:
        """
        Release all resources.
        """

        self.logger.info(
            "Cleaning application resources..."
        )

        self.disconnect_websocket()

        self.release_components()

        self.clear_cache()

        self.logger.info(
            "Cleanup completed."
        )

    # ==========================================================
    # DISCONNECT WEBSOCKET
    # ==========================================================

    def disconnect_websocket(self) -> None:

        if self.websocket_service:

            try:

                self.websocket_service.stop()

            except Exception as ex:

                self.logger.exception(ex)

    # ==========================================================
    # RELEASE COMPONENTS
    # ==========================================================

    def release_components(self) -> None:

        components = [

            "alert_manager",

            "market_analyzer",

            "screener",

            "data_manager",

            "upstox",

            "scanner_service",

            "websocket_service",

        ]

        for component in components:

            setattr(

                self,

                component,

                None,

            )

    # ==========================================================
    # CLEAR CACHE
    # ==========================================================

    def clear_cache(self) -> None:
        """
        Clear temporary runtime cache.
        """

        self.logger.info(
            "Clearing runtime cache..."
        )

        # Future implementation:
        # cache_service.clear()

    # ==========================================================
    # FORCE CLOSE
    # ==========================================================

    def force_close(self) -> None:
        """
        Emergency shutdown.
        """

        self.logger.warning(
            "Force shutdown requested."
        )

        self.close_dashboard()

        self.close_login()

        self.close_splash()

        self.change_state(
            ApplicationState.CLOSED
        )

    # ==========================================================
    # APPLICATION EXIT
    # ==========================================================

    def exit(self) -> None:
        """
        Public exit API.
        """

        self.shutdown()

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        if exc_val:

            self.logger.exception(
                exc_val
            )

        self.shutdown()

        return False

    # ==========================================================
    # DESTRUCTOR
    # ==========================================================

    def __del__(self):

        try:

            if self.state != ApplicationState.CLOSED:

                self.shutdown()

        except Exception:

            pass
            # ==========================================================
    # VERSION INFORMATION
    # ==========================================================

    def version_info(self) -> Dict[str, Any]:
        """
        Return application version information.
        """

        return {

            "application": self.APP_NAME,

            "version": self.VERSION,

            "build": "2026.07.30",

            "author": "StockVersity",

            "platform": "Desktop",

        }

    # ==========================================================
    # RUNTIME STATISTICS
    # ==========================================================

    def runtime_statistics(self) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        uptime = datetime.now() - self.started

        return {

            "uptime": str(uptime),

            "state": self.state.value,

            "started": self.started,

            "connected": self.is_connected(),

            "healthy": self.health_check()["healthy"],

        }

    # ==========================================================
    # SERVICE REGISTRY
    # ==========================================================

    def service_registry(self) -> Dict[str, Any]:
        """
        Return all registered services.
        """

        return {

            "upstox": self.upstox,

            "data_manager": self.data_manager,

            "market_analyzer": self.market_analyzer,

            "screener": self.screener,

            "alert_manager": self.alert_manager,

            "scanner_service": self.scanner_service,

            "websocket_service": self.websocket_service,

        }

    # ==========================================================
    # GET SERVICE
    # ==========================================================

    def get_service(
        self,
        name: str,
    ):
        """
        Get service by name.
        """

        return self.service_registry().get(name)

    # ==========================================================
    # IS RUNNING
    # ==========================================================

    def is_running(self) -> bool:

        return self.state == ApplicationState.RUNNING

    # ==========================================================
    # IS READY
    # ==========================================================

    def is_ready(self) -> bool:

        return self.state == ApplicationState.READY

    # ==========================================================
    # IS CLOSED
    # ==========================================================

    def is_closed(self) -> bool:

        return self.state == ApplicationState.CLOSED

    # ==========================================================
    # APPLICATION SUMMARY
    # ==========================================================

    def summary(self) -> Dict[str, Any]:
        """
        Complete application summary.
        """

        return {

            "application": self.application_info(),

            "version": self.version_info(),

            "status": self.get_status(),

            "runtime": self.runtime_statistics(),

            "health": self.health_check(),

        }

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (

            f"<ApplicationController "

            f"state={self.state.value} "

            f"version={self.VERSION}>"

        )

    def __str__(self):

        return (

            f"{self.APP_NAME} "

            f"({self.VERSION})"

        )


# ==========================================================
# FACTORY FUNCTION
# ==========================================================

def create_application_controller() -> ApplicationController:
    """
    Factory function.
    """

    return ApplicationController()


# ==========================================================
# END OF FILE
# ==========================================================
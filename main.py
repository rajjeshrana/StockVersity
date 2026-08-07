"""
=========================================================
StockVersity Scanner Pro v3
Main Entry Point
=========================================================
"""

import sys
import os
import traceback
import logging
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QSharedMemory,
    QTimer,
)

from PySide6.QtGui import (
    QPixmap,
    QFont,
)

from PySide6.QtWidgets import (
    QApplication,
    QSplashScreen,
    QMessageBox,
)

from ui.app import MainWindow


# =========================================================
# APPLICATION INFORMATION
# =========================================================

APP_NAME = "StockVersity Scanner Pro"

APP_VERSION = "3.0"

ORGANIZATION = "StockVersity"

LOG_FOLDER = "logs"

LOG_FILE = "application.log"


# =========================================================
# CREATE LOG DIRECTORY
# =========================================================

Path(LOG_FOLDER).mkdir(

    exist_ok=True

)

logging.basicConfig(

    filename=os.path.join(

        LOG_FOLDER,

        LOG_FILE,

    ),

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

)


logger = logging.getLogger(APP_NAME)


# =========================================================
# GLOBAL EXCEPTION HANDLER
# =========================================================

def exception_handler(

    exc_type,

    exc_value,

    exc_traceback,

):

    if issubclass(

        exc_type,

        KeyboardInterrupt,

    ):

        sys.__excepthook__(

            exc_type,

            exc_value,

            exc_traceback,

        )

        return

    error = "".join(

        traceback.format_exception(

            exc_type,

            exc_value,

            exc_traceback,

        )

    )

    logger.exception(error)

    QMessageBox.critical(

        None,

        "Unexpected Error",

        error,

    )


sys.excepthook = exception_handler


# =========================================================
# SINGLE INSTANCE
# =========================================================

shared_memory = QSharedMemory(

    APP_NAME

)

if shared_memory.attach():

    app = QApplication(sys.argv)

    QMessageBox.information(

        None,

        APP_NAME,

        "Application is already running.",

    )

    sys.exit()

shared_memory.create(1)


# =========================================================
# APPLICATION
# =========================================================

app = QApplication(sys.argv)

app.setApplicationName(APP_NAME)

app.setApplicationVersion(APP_VERSION)

app.setOrganizationName(

    ORGANIZATION

)

app.setAttribute(

    Qt.AA_EnableHighDpiScaling,

    True,

)

app.setAttribute(

    Qt.AA_UseHighDpiPixmaps,

    True,

)

font = QFont(

    "Segoe UI",

    10,

)

app.setFont(font)
# =========================================================
# SPLASH SCREEN
# =========================================================

pixmap = QPixmap(600, 350)

pixmap.fill(Qt.black)

splash = QSplashScreen(pixmap)

splash.setStyleSheet("""

QLabel{

    color:white;

    font-size:22px;

    font-weight:700;

    background:#111111;

    padding:20px;

}

""")

splash.show()

app.processEvents()

# =========================================================
# STARTUP MESSAGES
# =========================================================

startup_messages = [

    "Initializing application...",

    "Loading UI components...",

    "Loading Dashboard module...",

    "Loading Intraday Scanner...",

    "Loading Swing Scanner...",

    "Loading Positional Scanner...",

    "Loading AI Engine...",

    "Preparing Market Data...",

    "Loading Watchlists...",

    "Checking configuration...",

    "Initializing database...",

    "Loading user preferences...",

    "Starting services...",

    "Finalizing startup...",

]

for message in startup_messages:

    splash.showMessage(

        message,

        Qt.AlignBottom | Qt.AlignCenter,

        Qt.white,

    )

    logger.info(message)

    app.processEvents()

# =========================================================
# MAIN WINDOW
# =========================================================

logger.info("Creating MainWindow")

window = MainWindow()

window.hide()

# =========================================================
# LOAD SETTINGS
# =========================================================

try:

    if hasattr(

        window,

        "restore_ui_state",

    ):

        window.restore_ui_state()

        logger.info(

            "UI state restored."

        )

except Exception as e:

    logger.warning(

        "Unable to restore UI state: %s",

        e,

    )

# =========================================================
# APPLICATION READY
# =========================================================

def launch_application():

    logger.info(

        "Launching application."

    )

    splash.finish(window)

    window.show()

    window.raise_()

    window.activateWindow()

    try:

        if hasattr(

            window,

            "application_ready",

        ):

            window.application_ready()

    except Exception as e:

        logger.warning(

            "application_ready(): %s",

            e,

        )

# =========================================================
# SMALL STARTUP DELAY
# =========================================================

QTimer.singleShot(

    1200,

    launch_application,

)
# =========================================================
# CLEAN SHUTDOWN
# =========================================================

def shutdown():

    logger.info(

        "=" * 60

    )

    logger.info(

        "Application shutdown initiated."

    )

    try:

        if "window" in globals():

            if hasattr(window, "cleanup"):

                window.cleanup()

    except Exception as e:

        logger.exception(

            "Cleanup Error: %s",

            e,

        )

    logger.info(

        "Shutdown complete."

    )

    logger.info(

        "=" * 60

    )


# =========================================================
# APPLICATION EXECUTION
# =========================================================

def run():

    logger.info(

        "=" * 60

    )

    logger.info(

        "%s v%s",

        APP_NAME,

        APP_VERSION,

    )

    logger.info(

        "Application started."

    )

    logger.info(

        "=" * 60

    )

    exit_code = 0

    try:

        exit_code = app.exec()

    except Exception as e:

        logger.exception(

            "Fatal Runtime Error: %s",

            e,

        )

        QMessageBox.critical(

            None,

            APP_NAME,

            str(e),

        )

        exit_code = 1

    finally:

        shutdown()

    return exit_code


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    try:

        sys.exit(

            run()

        )

    except SystemExit:

        raise

    except Exception as e:

        logger.exception(

            "Unhandled Error: %s",

            e,

        )

        QMessageBox.critical(

            None,

            APP_NAME,

            str(e),

        )

        sys.exit(1)
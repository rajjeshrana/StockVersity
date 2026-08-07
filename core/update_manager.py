from __future__ import annotations

import json
import threading
import urllib.request
import urllib.error

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


# =====================================================
# UPDATE INFO
# =====================================================

@dataclass(slots=True)
class UpdateInfo:

    version: str = ""

    build: str = ""

    channel: str = "stable"

    release_date: str = ""

    download_url: str = ""

    checksum: str = ""

    release_notes: List[str] = field(default_factory=list)

    mandatory: bool = False

    size: int = 0


# =====================================================
# UPDATE MANAGER
# =====================================================

class UpdateManager:

    _instance = None
    _lock = threading.Lock()

    # -------------------------------------------------

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # -------------------------------------------------

    def __init__(self):

        if getattr(self, "_initialized", False):

            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.current_version = "4.0.0"

        self.current_build = "2026.07"

        self.channel = "stable"

        self.endpoint = ""

        self.timeout = 20

        self.download_folder = (
            Path.home()
            / ".stockversity"
            / "updates"
        )

        self.download_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.latest = UpdateInfo()

        self.last_check: Optional[datetime] = None

        self.progress_callback: Optional[
            Callable[[int], None]
        ] = None

    # =====================================================
    # CONFIGURATION
    # =====================================================

    def set_endpoint(

        self,

        url: str,

    ):

        self.endpoint = url

    # -------------------------------------------------

    def set_channel(

        self,

        channel: str,

    ):

        self.channel = channel.lower()

    # -------------------------------------------------

    def set_progress_callback(

        self,

        callback: Callable[[int], None],

    ):

        self.progress_callback = callback

    # =====================================================
    # VERSION
    # =====================================================

    def version_tuple(

        self,

        version: str,

    ):

        return tuple(

            int(x)

            for x in version.split(".")

        )

    # -------------------------------------------------

    def compare_versions(

        self,

        current: str,

        latest: str,

    ):

        current_tuple = self.version_tuple(
            current
        )

        latest_tuple = self.version_tuple(
            latest
        )

        if latest_tuple > current_tuple:
            return 1

        if latest_tuple < current_tuple:
            return -1

        return 0

    # =====================================================
    # UPDATE AVAILABLE
    # =====================================================

    def update_available(

        self,

    ):

        return (

            self.compare_versions(

                self.current_version,

                self.latest.version,

            )

            == 1

        )

    # =====================================================
    # CHECK FOR UPDATE
    # =====================================================

    def check(

        self,

    ):

        if not self.endpoint:

            return False

        try:

            with urllib.request.urlopen(

                self.endpoint,

                timeout=self.timeout,

            ) as response:

                payload = json.loads(

                    response.read().decode()

                )

        except (

            urllib.error.URLError,

            urllib.error.HTTPError,

            TimeoutError,

            json.JSONDecodeError,

        ):

            return False

        self.latest = UpdateInfo(

            version=payload.get(

                "version",

                "",

            ),

            build=payload.get(

                "build",

                "",

            ),

            channel=payload.get(

                "channel",

                "stable",

            ),

            release_date=payload.get(

                "release_date",

                "",

            ),

            download_url=payload.get(

                "download_url",

                "",

            ),

            checksum=payload.get(

                "checksum",

                "",

            ),

            release_notes=payload.get(

                "release_notes",

                [],

            ),

            mandatory=payload.get(

                "mandatory",

                False,

            ),

            size=payload.get(

                "size",

                0,

            ),

        )

        self.last_check = datetime.utcnow()

        return True
        # =====================================================
    # DOWNLOAD UPDATE
    # =====================================================

    def download(

        self,

        destination: Optional[Path] = None,

    ):

        if not self.latest.download_url:

            return None

        if destination is None:

            filename = Path(

                self.latest.download_url

            ).name or "update.bin"

            destination = (

                self.download_folder

                / filename

            )

        try:

            with urllib.request.urlopen(

                self.latest.download_url,

                timeout=self.timeout,

            ) as response:

                total = int(

                    response.headers.get(

                        "Content-Length",

                        0,

                    )

                )

                downloaded = 0

                chunk_size = 8192

                with open(

                    destination,

                    "wb",

                ) as file:

                    while True:

                        if getattr(

                            self,

                            "_cancel_download",

                            False,

                        ):

                            file.close()

                            destination.unlink(

                                missing_ok=True,

                            )

                            return None

                        chunk = response.read(

                            chunk_size

                        )

                        if not chunk:

                            break

                        file.write(

                            chunk

                        )

                        downloaded += len(

                            chunk

                        )

                        if (

                            total > 0

                            and self.progress_callback

                        ):

                            percent = int(

                                downloaded

                                * 100

                                / total

                            )

                            self.progress_callback(

                                percent

                            )

            return destination

        except Exception:

            return None

    # =====================================================
    # CANCEL DOWNLOAD
    # =====================================================

    def cancel_download(

        self,

    ):

        self._cancel_download = True

    # -------------------------------------------------

    def reset_download(

        self,

    ):

        self._cancel_download = False

    # =====================================================
    # CHECKSUM
    # =====================================================

    def verify_checksum(

        self,

        file_path: Path,

    ):

        if (

            not file_path.exists()

            or not self.latest.checksum

        ):

            return False

        import hashlib

        sha = hashlib.sha256()

        with open(

            file_path,

            "rb",

        ) as f:

            while True:

                block = f.read(

                    1024 * 1024

                )

                if not block:

                    break

                sha.update(

                    block

                )

        return (

            sha.hexdigest().lower()

            == self.latest.checksum.lower()

        )

    # =====================================================
    # RELEASE NOTES
    # =====================================================

    def release_notes(

        self,

    ):

        return list(

            self.latest.release_notes

        )

    # =====================================================
    # UPDATE INFO
    # =====================================================

    def info(

        self,

    ):

        return {

            "current_version": self.current_version,

            "latest_version": self.latest.version,

            "build": self.latest.build,

            "channel": self.latest.channel,

            "mandatory": self.latest.mandatory,

            "release_date": self.latest.release_date,

            "size": self.latest.size,

            "download_url": self.latest.download_url,

            "checked_at": (

                self.last_check.isoformat()

                if self.last_check

                else None

            ),

        }

    # =====================================================
    # DOWNLOAD SIZE
    # =====================================================

    def download_size_mb(

        self,

    ):

        return round(

            self.latest.size

            / (1024 * 1024),

            2,

        )

    # =====================================================
    # IS MANDATORY
    # =====================================================

    @property
    def mandatory(

        self,

    ):

        return self.latest.mandatory
        # =====================================================
    # CHECK IN BACKGROUND
    # =====================================================

    def check_async(

        self,

        callback: Optional[Callable[[bool], None]] = None,

    ):

        def worker():

            result = self.check()

            if callback:

                try:

                    callback(result)
                except Exception:
                    pass

        thread = threading.Thread(
            target=worker,
            daemon=True,
            name="UpdateChecker",
        )

        thread.start()

        return thread

    # =====================================================
    # UPDATE HISTORY
    # =====================================================

    @property
    def history_file(self):

        return self.download_folder / "history.json"

    # -------------------------------------------------

    def add_history(

        self,

        version: str,

        status: str = "downloaded",

    ):

        history = self.history()

        history.append(

            {

                "version": version,

                "status": status,

                "timestamp": datetime.utcnow().isoformat(),

            }

        )

        self.history_file.write_text(

            json.dumps(

                history,

                indent=4,

            ),

            encoding="utf-8",

        )

    # -------------------------------------------------

    def history(

        self,

    ):

        if not self.history_file.exists():

            return []

        try:

            return json.loads(

                self.history_file.read_text(

                    encoding="utf-8",

                )

            )

        except Exception:

            return []

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(

        self,

        version: str,

    ):

        history = self.history()

        for item in reversed(history):

            if item["version"] == version:

                item["status"] = "rolled_back"

                self.history_file.write_text(

                    json.dumps(

                        history,

                        indent=4,

                    ),

                    encoding="utf-8",

                )

                return True

        return False

    # =====================================================
    # CLEAN OLD DOWNLOADS
    # =====================================================

    def cleanup(

        self,

        keep_latest: int = 3,

    ):

        files = sorted(

            self.download_folder.glob("*"),

            key=lambda p: p.stat().st_mtime,

            reverse=True,

        )

        removed = 0

        for file in files[keep_latest:]:

            if file.name == "history.json":

                continue

            try:

                file.unlink()

                removed += 1
            except Exception:
                pass

        return removed

    # =====================================================
    # STARTUP CHECK
    # =====================================================

    def startup(

        self,

        async_check: bool = True,

    ):

        if async_check:

            self.check_async()

            return None

        return self.check()

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

    ):

        return {

            "current": self.current_version,

            "latest": self.latest.version,

            "update_available": self.update_available(),

            "mandatory": self.latest.mandatory,

            "channel": self.channel,

            "last_check": (

                self.last_check.isoformat()

                if self.last_check

                else None

            ),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "history_entries": len(

                self.history()

            ),

            "downloaded_files": len(

                list(

                    self.download_folder.glob("*")

                )

            ),

            "channel": self.channel,

            "last_checked": (

                self.last_check.isoformat()

                if self.last_check

                else None

            ),

        }
        # =====================================================
    # INSTALL UPDATE
    # =====================================================

    def install(
        self,
        package_path: Path,
    ):

        """
        Placeholder installation workflow.

        Replace this method with your platform-specific
        installer logic (MSI, EXE, ZIP, etc.).
        """

        if not package_path.exists():
            return False

        if not self.verify_checksum(package_path):
            return False

        self.add_history(
            self.latest.version,
            status="installed",
        )

        return True

    # =====================================================
    # EXPORT SETTINGS
    # =====================================================

    def export_settings(
        self,
    ):

        return {

            "current_version": self.current_version,

            "current_build": self.current_build,

            "channel": self.channel,

            "endpoint": self.endpoint,

            "timeout": self.timeout,

        }

    # =====================================================
    # IMPORT SETTINGS
    # =====================================================

    def import_settings(
        self,
        settings: Dict,
    ):

        self.current_version = settings.get(
            "current_version",
            self.current_version,
        )

        self.current_build = settings.get(
            "current_build",
            self.current_build,
        )

        self.channel = settings.get(
            "channel",
            self.channel,
        )

        self.endpoint = settings.get(
            "endpoint",
            self.endpoint,
        )

        self.timeout = settings.get(
            "timeout",
            self.timeout,
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ):

        self.latest = UpdateInfo()

        self.last_check = None

        self.progress_callback = None

        self._cancel_download = False

    # =====================================================
    # CURRENT VERSION
    # =====================================================

    @property
    def version(
        self,
    ):

        return self.current_version

    # -------------------------------------------------

    @property
    def build(
        self,
    ):

        return self.current_build

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ):

        return (

            "UpdateManager("

            f"version='{self.current_version}', "

            f"latest='{self.latest.version}', "

            f"channel='{self.channel}'"

            ")"

        )

    # -------------------------------------------------

    def __str__(
        self,
    ):

        available = "Yes" if self.update_available() else "No"

        return (

            "Update Manager\n"

            f"Current Version : {self.current_version}\n"

            f"Latest Version  : {self.latest.version or '-'}\n"

            f"Channel         : {self.channel}\n"

            f"Update Available: {available}\n"

            f"Last Check      : "

            f"{self.last_check.isoformat() if self.last_check else 'Never'}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

update_manager = UpdateManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "UpdateInfo",

    "UpdateManager",

    "update_manager",

]
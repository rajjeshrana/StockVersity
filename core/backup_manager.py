from __future__ import annotations

import hashlib
import shutil
import threading
import zipfile

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# =====================================================
# BACKUP INFO
# =====================================================

@dataclass(slots=True)
class BackupInfo:

    name: str

    created_at: datetime

    archive: Path

    source: Path

    backup_type: str = "full"

    size: int = 0

    checksum: str = ""

    verified: bool = False

    metadata: Dict = field(
        default_factory=dict
    )


# =====================================================
# BACKUP MANAGER
# =====================================================

class BackupManager:

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

        self.backup_directory = (

            Path.home()

            / ".stockversity"

            / "backups"

        )

        self.backup_directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        self.backups: List[BackupInfo] = []

        self.max_backups = 20

        self.compression = zipfile.ZIP_DEFLATED

    # =====================================================
    # CHECKSUM
    # =====================================================

    def checksum(

        self,

        file: Path,

    ):

        sha = hashlib.sha256()

        with open(

            file,

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

        return sha.hexdigest()

    # =====================================================
    # BACKUP NAME
    # =====================================================

    def backup_name(

        self,

        prefix: str = "backup",

    ):

        return (

            prefix

            + "_"

            + datetime.now().strftime(

                "%Y%m%d_%H%M%S"

            )

        )

    # =====================================================
    # CREATE ZIP
    # =====================================================

    def create_backup(

        self,

        source: Path,

        backup_type: str = "full",

        name: Optional[str] = None,

    ):

        if not source.exists():

            raise FileNotFoundError(

                source

            )

        if name is None:

            name = self.backup_name()

        archive = (

            self.backup_directory

            / f"{name}.zip"

        )

        with zipfile.ZipFile(

            archive,

            "w",

            compression=self.compression,

        ) as z:

            if source.is_file():

                z.write(

                    source,

                    source.name,

                )

            else:

                for file in source.rglob("*"):

                    if file.is_file():

                        z.write(

                            file,

                            file.relative_to(

                                source

                            ),

                        )

        info = BackupInfo(

            name=name,

            created_at=datetime.utcnow(),

            archive=archive,

            source=source,

            backup_type=backup_type,

            size=archive.stat().st_size,

            checksum=self.checksum(

                archive

            ),

        )

        self.backups.append(

            info

        )

        return info

    # =====================================================
    # LIST
    # =====================================================

    def list_backups(

        self,

    ):

        return list(

            self.backups

        )

    # =====================================================
    # GET
    # =====================================================

    def get_backup(

        self,

        name: str,

    ):

        for backup in self.backups:

            if backup.name == name:

                return backup

        return None
        # =====================================================
    # RESTORE BACKUP
    # =====================================================

    def restore_backup(

        self,

        name: str,

        destination: Path,

        overwrite: bool = True,

    ):

        backup = self.get_backup(

            name

        )

        if backup is None:

            raise ValueError(

                f"Backup '{name}' not found."

            )

        destination.mkdir(

            parents=True,

            exist_ok=True,

        )

        with zipfile.ZipFile(

            backup.archive,

            "r",

        ) as archive:

            if overwrite:

                archive.extractall(

                    destination

                )

            else:

                for member in archive.infolist():

                    target = (

                        destination

                        / member.filename

                    )

                    if not target.exists():

                        archive.extract(

                            member,

                            destination,

                        )

        return destination

    # =====================================================
    # VERIFY BACKUP
    # =====================================================

    def verify_backup(

        self,

        name: str,

    ):

        backup = self.get_backup(

            name

        )

        if backup is None:

            return False

        if not backup.archive.exists():

            return False

        current = self.checksum(

            backup.archive

        )

        backup.verified = (

            current == backup.checksum

        )

        return backup.verified

    # =====================================================
    # VERIFY ALL
    # =====================================================

    def verify_all(

        self,

    ):

        results = {}

        for backup in self.backups:

            results[

                backup.name

            ] = self.verify_backup(

                backup.name

            )

        return results

    # =====================================================
    # DELETE BACKUP
    # =====================================================

    def delete_backup(

        self,

        name: str,

    ):

        backup = self.get_backup(

            name

        )

        if backup is None:

            return False

        if backup.archive.exists():

            backup.archive.unlink()

        self.backups.remove(

            backup

        )

        return True

    # =====================================================
    # RETENTION POLICY
    # =====================================================

    def apply_retention(

        self,

    ):

        if len(

            self.backups

        ) <= self.max_backups:

            return 0

        self.backups.sort(

            key=lambda x: x.created_at

        )

        removed = 0

        while len(

            self.backups

        ) > self.max_backups:

            backup = self.backups.pop(

                0

            )

            if backup.archive.exists():

                backup.archive.unlink()

            removed += 1

        return removed

    # =====================================================
    # INCREMENTAL BACKUP
    # =====================================================

    def incremental_backup(

        self,

        source: Path,

    ):

        return self.create_backup(

            source,

            backup_type="incremental",

            name=self.backup_name(

                "incremental"

            ),

        )

    # =====================================================
    # FULL BACKUP
    # =====================================================

    def full_backup(

        self,

        source: Path,

    ):

        return self.create_backup(

            source,

            backup_type="full",

            name=self.backup_name(

                "full"

            ),

        )

    # =====================================================
    # SEARCH
    # =====================================================

    def search(

        self,

        keyword: str,

    ):

        keyword = keyword.lower()

        return [

            backup

            for backup in self.backups

            if keyword

            in backup.name.lower()

        ]

    # =====================================================
    # FILTER
    # =====================================================

    def filter(

        self,

        backup_type: str,

    ):

        return [

            backup

            for backup in self.backups

            if backup.backup_type

            == backup_type

        ]

    # =====================================================
    # TOTAL SIZE
    # =====================================================

    def total_size(

        self,

    ):

        return sum(

            backup.size

            for backup in self.backups

        )
        # =====================================================
    # COMPRESSION RATIO
    # =====================================================

    def compression_ratio(

        self,

        backup_name: str,

    ):

        backup = self.get_backup(

            backup_name

        )

        if backup is None:

            return 0.0

        original_size = 0

        if backup.source.is_file():

            original_size = backup.source.stat().st_size

        else:

            for file in backup.source.rglob("*"):

                if file.is_file():

                    original_size += file.stat().st_size

        if original_size == 0:

            return 0.0

        return round(

            (1 - (backup.size / original_size)) * 100,

            2,

        )

    # =====================================================
    # BACKUP REPORT
    # =====================================================

    def backup_report(

        self,

    ):

        report = []

        for backup in self.backups:

            report.append(

                {

                    "name": backup.name,

                    "type": backup.backup_type,

                    "created_at": backup.created_at,

                    "size": backup.size,

                    "verified": backup.verified,

                    "checksum": backup.checksum,

                }

            )

        return report

    # =====================================================
    # EXPORT METADATA
    # =====================================================

    def export_metadata(

        self,

    ):

        exported = []

        for backup in self.backups:

            exported.append(

                {

                    "name": backup.name,

                    "created_at": backup.created_at.isoformat(),

                    "archive": str(

                        backup.archive

                    ),

                    "source": str(

                        backup.source

                    ),

                    "backup_type": backup.backup_type,

                    "size": backup.size,

                    "checksum": backup.checksum,

                    "verified": backup.verified,

                    "metadata": backup.metadata,

                }

            )

        return exported

    # =====================================================
    # IMPORT METADATA
    # =====================================================

    def import_metadata(

        self,

        data: List[Dict],

    ):

        imported = 0

        for item in data:

            info = BackupInfo(

                name=item["name"],

                created_at=datetime.fromisoformat(

                    item["created_at"]

                ),

                archive=Path(

                    item["archive"]

                ),

                source=Path(

                    item["source"]

                ),

                backup_type=item.get(

                    "backup_type",

                    "full",

                ),

                size=item.get(

                    "size",

                    0,

                ),

                checksum=item.get(

                    "checksum",

                    "",

                ),

                verified=item.get(

                    "verified",

                    False,

                ),

                metadata=item.get(

                    "metadata",

                    {},

                ),

            )

            self.backups.append(

                info

            )

            imported += 1

        return imported

    # =====================================================
    # SCHEDULED BACKUP
    # =====================================================

    def scheduled_backup(

        self,

        source: Path,

        backup_type: str = "full",

    ):

        backup = self.create_backup(

            source,

            backup_type=backup_type,

        )

        self.apply_retention()

        return backup

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health(

        self,

    ):

        verified = sum(

            1

            for backup in self.backups

            if backup.verified

        )

        return {

            "total_backups": len(

                self.backups

            ),

            "verified": verified,

            "failed": len(

                self.backups

            )

            - verified,

            "storage_used": self.total_size(),

        }

    # =====================================================
    # REMOVE MISSING
    # =====================================================

    def remove_missing(

        self,

    ):

        before = len(

            self.backups

        )

        self.backups = [

            backup

            for backup in self.backups

            if backup.archive.exists()

        ]

        return before - len(

            self.backups

        )

    # =====================================================
    # OLDEST BACKUP
    # =====================================================

    def oldest_backup(

        self,

    ):

        if not self.backups:

            return None

        return min(

            self.backups,

            key=lambda b: b.created_at,

        )

    # =====================================================
    # LATEST BACKUP
    # =====================================================

    def latest_backup(

        self,

    ):

        if not self.backups:

            return None

        return max(

            self.backups,

            key=lambda b: b.created_at,

        )
        # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        full = len(

            self.filter(

                "full"

            )

        )

        incremental = len(

            self.filter(

                "incremental"

            )

        )

        verified = sum(

            1

            for backup in self.backups

            if backup.verified

        )

        return {

            "total_backups": len(

                self.backups

            ),

            "full_backups": full,

            "incremental_backups": incremental,

            "verified": verified,

            "failed": len(

                self.backups

            )

            - verified,

            "storage_used": self.total_size(),

            "max_backups": self.max_backups,

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ):

        self.backups.clear()

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(

        self,

    ):

        """
        Startup hook.

        Reserved for loading
        persisted backup metadata.
        """

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(

        self,

    ):

        """
        Shutdown hook.

        Reserved for saving
        backup metadata.
        """

        self.apply_retention()

        return {

            "backups": len(

                self.backups

            ),

            "storage": self.total_size(),

        }

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(

        self,

    ):

        stats = self.statistics()

        return (

            "BackupManager("

            f"backups={stats['total_backups']}, "

            f"storage={stats['storage_used']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(

        self,

    ):

        stats = self.statistics()

        return (

            "Backup Manager\n"

            f"Backups        : {stats['total_backups']}\n"

            f"Full           : {stats['full_backups']}\n"

            f"Incremental    : {stats['incremental_backups']}\n"

            f"Verified       : {stats['verified']}\n"

            f"Failed         : {stats['failed']}\n"

            f"Storage (B)    : {stats['storage_used']}\n"

            f"Retention Max  : {stats['max_backups']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

backup_manager = BackupManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "BackupInfo",

    "BackupManager",

    "backup_manager",

]
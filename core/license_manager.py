from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import socket
import threading
import uuid

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


# =====================================================
# LICENSE
# =====================================================

@dataclass(slots=True)
class License:

    key: str = ""

    customer: str = ""

    email: str = ""

    company: str = ""

    edition: str = "Professional"

    activated: bool = False

    activation_date: Optional[str] = None

    expiry_date: Optional[str] = None

    hardware_id: str = ""

    max_devices: int = 1

    enabled_features: List[str] = None

    metadata: Dict = None

    def __post_init__(self):

        if self.enabled_features is None:

            self.enabled_features = []

        if self.metadata is None:

            self.metadata = {}

    # -------------------------------------------------

    @property
    def expired(self):

        if not self.expiry_date:

            return False

        return datetime.utcnow() > datetime.fromisoformat(
            self.expiry_date
        )


# =====================================================
# LICENSE MANAGER
# =====================================================

class LicenseManager:

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

        self.license = License()

        self.storage_path = (
            Path.home()
            / ".stockversity"
            / "license.dat"
        )

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.trial_days = 14

        self.secret = (
            "StockVersityScannerProV4"
        )

    # =====================================================
    # HARDWARE ID
    # =====================================================

    def hardware_id(self):

        text = "|".join(

            [

                platform.system(),

                platform.machine(),

                platform.node(),

                socket.gethostname(),

                str(uuid.getnode()),

            ]

        )

        return hashlib.sha256(

            text.encode()

        ).hexdigest()

    # =====================================================
    # LICENSE KEY
    # =====================================================

    def generate_key(

        self,

        customer: str,

        email: str,

    ):

        raw = (

            customer

            + email

            + self.secret

        )

        digest = hashlib.sha256(

            raw.encode()

        ).hexdigest().upper()

        return "-".join(

            [

                digest[0:5],

                digest[5:10],

                digest[10:15],

                digest[15:20],

                digest[20:25],

            ]

        )

    # =====================================================
    # VERIFY FORMAT
    # =====================================================

    def validate_format(

        self,

        key: str,

    ):

        parts = key.split("-")

        if len(parts) != 5:

            return False

        return all(

            len(part) == 5

            for part in parts

        )

    # =====================================================
    # CREATE TRIAL
    # =====================================================

    def create_trial(

        self,

    ):

        now = datetime.utcnow()

        self.license = License(

            key="TRIAL",

            customer="Trial User",

            activated=True,

            activation_date=now.isoformat(),

            expiry_date=(
                now
                + timedelta(
                    days=self.trial_days
                )
            ).isoformat(),

            hardware_id=self.hardware_id(),

            edition="Trial",

            enabled_features=[

                "Scanner",

                "Dashboard",

                "AI"

            ],

        )

        self.save()

        return self.license
        # =====================================================
    # ACTIVATE LICENSE
    # =====================================================

    def activate(

        self,

        key: str,

        customer: str,

        email: str,

        edition: str = "Professional",

        expiry_date: Optional[str] = None,

        features: Optional[List[str]] = None,

    ):

        with self.manager_lock:

            if not self.validate_format(key):

                return False, "Invalid license format."

            expected = self.generate_key(

                customer,

                email,

            )

            if expected != key:

                return False, "License key verification failed."

            self.license = License(

                key=key,

                customer=customer,

                email=email,

                edition=edition,

                activated=True,

                activation_date=datetime.utcnow().isoformat(),

                expiry_date=expiry_date,

                hardware_id=self.hardware_id(),

                enabled_features=features or [

                    "Dashboard",

                    "Scanner",

                    "AI",

                ],

            )

            self.save()

            return True, "License activated successfully."

    # =====================================================
    # DEACTIVATE
    # =====================================================

    def deactivate(

        self,

    ):

        with self.manager_lock:

            self.license = License()

            if self.storage_path.exists():

                self.storage_path.unlink()

        return True

    # =====================================================
    # SAVE LICENSE
    # =====================================================

    def save(

        self,

    ):

        data = json.dumps(

            asdict(

                self.license

            )

        )

        encoded = base64.b64encode(

            data.encode()

        )

        self.storage_path.write_bytes(

            encoded

        )

    # =====================================================
    # LOAD LICENSE
    # =====================================================

    def load(

        self,

    ):

        if not self.storage_path.exists():

            return None

        try:

            encoded = self.storage_path.read_bytes()

            decoded = base64.b64decode(

                encoded

            ).decode()

            data = json.loads(

                decoded

            )

            self.license = License(

                **data

            )

            return self.license

        except Exception:

            return None

    # =====================================================
    # OFFLINE VALIDATION
    # =====================================================

    def validate(

        self,

    ):

        if not self.license.activated:

            return False, "License is not activated."

        if self.license.hardware_id != self.hardware_id():

            return False, "Hardware mismatch."

        if self.license.expired:

            return False, "License has expired."

        return True, "License is valid."

    # =====================================================
    # LICENSE EXISTS
    # =====================================================

    def exists(

        self,

    ):

        return self.storage_path.exists()

    # =====================================================
    # EXPIRY CHECK
    # =====================================================

    def days_remaining(

        self,

    ):

        if not self.license.expiry_date:

            return None

        expiry = datetime.fromisoformat(

            self.license.expiry_date

        )

        remaining = (

            expiry - datetime.utcnow()

        ).days

        return max(

            remaining,

            0,

        )

    # =====================================================
    # LICENSE TYPE
    # =====================================================

    @property
    def is_trial(

        self,

    ):

        return self.license.edition.lower() == "trial"

    # -------------------------------------------------

    @property
    def is_activated(

        self,

    ):

        return self.license.activated

    # -------------------------------------------------

    @property
    def is_expired(

        self,

    ):

        return self.license.expired
        # =====================================================
    # FEATURES
    # =====================================================

    def has_feature(

        self,

        feature: str,

    ) -> bool:

        return (

            feature in self.license.enabled_features

        )

    # -------------------------------------------------

    def enable_feature(

        self,

        feature: str,

    ):

        if feature not in self.license.enabled_features:

            self.license.enabled_features.append(

                feature

            )

            self.save()

    # -------------------------------------------------

    def disable_feature(

        self,

        feature: str,

    ):

        if feature in self.license.enabled_features:

            self.license.enabled_features.remove(

                feature

            )

            self.save()

    # =====================================================
    # EDITION
    # =====================================================

    def set_edition(

        self,

        edition: str,

    ):

        self.license.edition = edition

        self.save()

    # -------------------------------------------------

    def edition(

        self,

    ):

        return self.license.edition

    # =====================================================
    # RENEW LICENSE
    # =====================================================

    def renew(

        self,

        days: int,

    ):

        if self.license.expiry_date:

            expiry = datetime.fromisoformat(

                self.license.expiry_date

            )

        else:

            expiry = datetime.utcnow()

        expiry += timedelta(

            days=days

        )

        self.license.expiry_date = (

            expiry.isoformat()

        )

        self.save()

        return self.license.expiry_date

    # =====================================================
    # LICENSE INFO
    # =====================================================

    def info(

        self,

    ):

        return {

            "customer": self.license.customer,

            "email": self.license.email,

            "company": self.license.company,

            "edition": self.license.edition,

            "activated": self.license.activated,

            "activation_date": self.license.activation_date,

            "expiry_date": self.license.expiry_date,

            "days_remaining": self.days_remaining(),

            "hardware_id": self.license.hardware_id,

            "features": list(

                self.license.enabled_features

            ),

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def export(

        self,

    ):

        return asdict(

            self.license

        )

    # =====================================================
    # IMPORT
    # =====================================================

    def import_license(

        self,

        data: Dict,

    ):

        self.license = License(

            **data

        )

        self.save()

        return self.license

    # =====================================================
    # BACKUP
    # =====================================================

    def backup(

        self,

        destination: Path,

    ):

        destination.parent.mkdir(

            parents=True,

            exist_ok=True,

        )

        if self.storage_path.exists():

            destination.write_bytes(

                self.storage_path.read_bytes()

            )

            return True

        return False

    # =====================================================
    # RESTORE
    # =====================================================

    def restore(

        self,

        backup_file: Path,

    ):

        if not backup_file.exists():

            return False

        self.storage_path.write_bytes(

            backup_file.read_bytes()

        )

        self.load()

        return True

    # =====================================================
    # RESET LICENSE
    # =====================================================

    def reset(

        self,

    ):

        self.license = License()

        self.save()

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

    ):

        valid, message = self.validate()

        return {

            "valid": valid,

            "message": message,

            "activated": self.is_activated,

            "trial": self.is_trial,

            "expired": self.is_expired,

            "edition": self.license.edition,

            "days_remaining": self.days_remaining(),

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ):

        return {

            "features": len(

                self.license.enabled_features

            ),

            "edition": self.license.edition,

            "activated": self.license.activated,

            "expired": self.license.expired,

            "hardware_bound": bool(

                self.license.hardware_id

            ),

        }
        # =====================================================
    # REVOKE LICENSE
    # =====================================================

    def revoke(self):

        """
        Revoke the current license.
        """

        self.license.activated = False
        self.save()

        return True

    # =====================================================
    # VERIFY INTEGRITY
    # =====================================================

    def verify_integrity(self):

        """
        Verify that the license file has not
        been modified externally.
        """

        if not self.exists():
            return False

        try:

            self.load()

            expected = self.generate_key(
                self.license.customer,
                self.license.email,
            )

            if self.license.key == "TRIAL":
                return True

            return expected == self.license.key

        except Exception:

            return False

    # =====================================================
    # MIGRATE LICENSE
    # =====================================================

    def migrate(

        self,

        new_storage: Path,

    ):

        """
        Move the license file to another location.
        """

        if not self.storage_path.exists():

            return False

        new_storage.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        new_storage.write_bytes(
            self.storage_path.read_bytes()
        )

        self.storage_path = new_storage

        return True

    # =====================================================
    # DELETE LICENSE FILE
    # =====================================================

    def delete_file(self):

        if self.storage_path.exists():

            self.storage_path.unlink()

            return True

        return False

    # =====================================================
    # IS PROFESSIONAL
    # =====================================================

    @property
    def is_professional(self):

        return (
            self.license.edition.lower()
            == "professional"
        )

    # =====================================================
    # IS ENTERPRISE
    # =====================================================

    @property
    def is_enterprise(self):

        return (
            self.license.edition.lower()
            == "enterprise"
        )

    # =====================================================
    # IS VALID
    # =====================================================

    @property
    def is_valid(self):

        valid, _ = self.validate()

        return valid

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (

            "LicenseManager("

            f"edition={self.license.edition}, "

            f"activated={self.license.activated}, "

            f"expired={self.license.expired}"

            ")"

        )

    # -------------------------------------------------

    def __str__(self):

        info = self.info()

        return (

            "License Manager\n"

            f"Customer : {info['customer']}\n"

            f"Edition  : {info['edition']}\n"

            f"Status   : "

            f"{'Activated' if self.is_activated else 'Inactive'}\n"

            f"Expiry   : {info['expiry_date']}\n"

            f"Features : {len(info['features'])}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

license_manager = LicenseManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "License",

    "LicenseManager",

    "license_manager",

]
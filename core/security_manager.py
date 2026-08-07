from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
import time

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set


# =====================================================
# USER
# =====================================================

@dataclass(slots=True)
class User:

    username: str

    password_hash: str

    salt: str

    role: str = "user"

    active: bool = True

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    last_login: Optional[datetime] = None

    permissions: Set[str] = field(
        default_factory=set
    )


# =====================================================
# SESSION
# =====================================================

@dataclass(slots=True)
class Session:

    token: str

    username: str

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    expires_at: datetime = field(
        default_factory=lambda: (
            datetime.utcnow()
            + timedelta(hours=8)
        )
    )

    ip_address: str = ""

    user_agent: str = ""

    @property
    def expired(self):

        return datetime.utcnow() > self.expires_at


# =====================================================
# AUDIT EVENT
# =====================================================

@dataclass(slots=True)
class AuditEvent:

    timestamp: datetime

    username: str

    action: str

    details: str = ""


# =====================================================
# SECURITY MANAGER
# =====================================================

class SecurityManager:

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

        self.users: Dict[str, User] = {}

        self.sessions: Dict[str, Session] = {}

        self.audit_log: List[AuditEvent] = []

        self.api_keys: Dict[str, str] = {}

        self.failed_attempts: Dict[str, int] = {}

        self.max_failed_attempts = 5

        self.session_timeout = timedelta(hours=8)

    # =====================================================
    # PASSWORD HASHING
    # =====================================================

    def generate_salt(self):

        return secrets.token_hex(16)

    # -------------------------------------------------

    def hash_password(

        self,

        password: str,

        salt: str,

    ):

        return hashlib.pbkdf2_hmac(

            "sha256",

            password.encode(),

            salt.encode(),

            150000,

        ).hex()

    # -------------------------------------------------

    def verify_password(

        self,

        password: str,

        password_hash: str,

        salt: str,

    ):

        computed = self.hash_password(

            password,

            salt,

        )

        return hmac.compare_digest(

            computed,

            password_hash,

        )

    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    def create_user(

        self,

        username: str,

        password: str,

        role: str = "user",

    ):

        if username in self.users:

            raise ValueError(

                "User already exists."

            )

        salt = self.generate_salt()

        password_hash = self.hash_password(

            password,

            salt,

        )

        user = User(

            username=username,

            password_hash=password_hash,

            salt=salt,

            role=role,

        )

        self.users[username] = user

        self.audit(

            username,

            "CREATE_USER",

        )

        return user

    # -------------------------------------------------

    def get_user(

        self,

        username: str,

    ):

        return self.users.get(

            username

        )

    # -------------------------------------------------

    def delete_user(

        self,

        username: str,

    ):

        if username not in self.users:

            return False

        del self.users[username]

        self.audit(

            username,

            "DELETE_USER",

        )

        return True
        # =====================================================
    # AUTHENTICATION
    # =====================================================

    def authenticate(

        self,

        username: str,

        password: str,

        ip_address: str = "",

        user_agent: str = "",

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return None

        if not user.active:

            self.audit(

                username,

                "LOGIN_DENIED",

                "User disabled",

            )

            return None

        if self.failed_attempts.get(

            username,

            0,

        ) >= self.max_failed_attempts:

            self.audit(

                username,

                "ACCOUNT_LOCKED",

            )

            return None

        if not self.verify_password(

            password,

            user.password_hash,

            user.salt,

        ):

            self.failed_attempts[

                username

            ] = (

                self.failed_attempts.get(

                    username,

                    0,

                )

                + 1

            )

            self.audit(

                username,

                "LOGIN_FAILED",

            )

            return None

        self.failed_attempts[

            username

        ] = 0

        user.last_login = datetime.utcnow()

        session = self.create_session(

            username,

            ip_address,

            user_agent,

        )

        self.audit(

            username,

            "LOGIN_SUCCESS",

        )

        return session

    # =====================================================
    # SESSION TOKEN
    # =====================================================

    def generate_token(

        self,

    ):

        return secrets.token_urlsafe(

            48

        )

    # =====================================================
    # CREATE SESSION
    # =====================================================

    def create_session(

        self,

        username: str,

        ip_address: str = "",

        user_agent: str = "",

    ):

        token = self.generate_token()

        session = Session(

            token=token,

            username=username,

            expires_at=(

                datetime.utcnow()

                + self.session_timeout

            ),

            ip_address=ip_address,

            user_agent=user_agent,

        )

        self.sessions[

            token

        ] = session

        return session

    # =====================================================
    # VALIDATE SESSION
    # =====================================================

    def validate_session(

        self,

        token: str,

    ):

        session = self.sessions.get(

            token

        )

        if session is None:

            return None

        if session.expired:

            self.sessions.pop(

                token,

                None,

            )

            return None

        return session

    # =====================================================
    # REFRESH SESSION
    # =====================================================

    def refresh_session(

        self,

        token: str,

    ):

        session = self.validate_session(

            token

        )

        if session is None:

            return False

        session.expires_at = (

            datetime.utcnow()

            + self.session_timeout

        )

        return True

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(

        self,

        token: str,

    ):

        session = self.sessions.pop(

            token,

            None,

        )

        if session:

            self.audit(

                session.username,

                "LOGOUT",

            )

            return True

        return False

    # =====================================================
    # CLEANUP SESSIONS
    # =====================================================

    def cleanup_sessions(

        self,

    ):

        expired = []

        for token, session in list(

            self.sessions.items()

        ):

            if session.expired:

                expired.append(

                    token

                )

        for token in expired:

            self.sessions.pop(

                token,

                None,

            )

        return len(

            expired

        )

    # =====================================================
    # ACTIVE SESSIONS
    # =====================================================

    def active_sessions(

        self,

    ):

        self.cleanup_sessions()

        return list(

            self.sessions.values()

        )

    # =====================================================
    # CHANGE PASSWORD
    # =====================================================

    def change_password(

        self,

        username: str,

        old_password: str,

        new_password: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        if not self.verify_password(

            old_password,

            user.password_hash,

            user.salt,

        ):

            return False

        salt = self.generate_salt()

        user.salt = salt

        user.password_hash = self.hash_password(

            new_password,

            salt,

        )

        self.audit(

            username,

            "PASSWORD_CHANGED",

        )

        return True
        # =====================================================
    # ROLE MANAGEMENT
    # =====================================================

    def set_role(

        self,

        username: str,

        role: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        user.role = role

        self.audit(

            username,

            "ROLE_CHANGED",

            role,

        )

        return True

    # -------------------------------------------------

    def role(

        self,

        username: str,

    ):

        user = self.get_user(

            username

        )

        return user.role if user else None

    # =====================================================
    # PERMISSIONS
    # =====================================================

    def grant_permission(

        self,

        username: str,

        permission: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        user.permissions.add(

            permission

        )

        self.audit(

            username,

            "PERMISSION_GRANTED",

            permission,

        )

        return True

    # -------------------------------------------------

    def revoke_permission(

        self,

        username: str,

        permission: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        user.permissions.discard(

            permission

        )

        self.audit(

            username,

            "PERMISSION_REVOKED",

            permission,

        )

        return True

    # -------------------------------------------------

    def has_permission(

        self,

        username: str,

        permission: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        return permission in user.permissions

    # =====================================================
    # API KEYS
    # =====================================================

    def generate_api_key(

        self,

        username: str,

    ):

        if username not in self.users:

            return None

        api_key = secrets.token_hex(

            32

        )

        self.api_keys[

            api_key

        ] = username

        self.audit(

            username,

            "API_KEY_CREATED",

        )

        return api_key

    # -------------------------------------------------

    def validate_api_key(

        self,

        api_key: str,

    ):

        return self.api_keys.get(

            api_key

        )

    # -------------------------------------------------

    def revoke_api_key(

        self,

        api_key: str,

    ):

        username = self.api_keys.pop(

            api_key,

            None,

        )

        if username:

            self.audit(

                username,

                "API_KEY_REVOKED",

            )

            return True

        return False

    # =====================================================
    # USER STATUS
    # =====================================================

    def activate_user(

        self,

        username: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        user.active = True

        self.audit(

            username,

            "USER_ACTIVATED",

        )

        return True

    # -------------------------------------------------

    def deactivate_user(

        self,

        username: str,

    ):

        user = self.get_user(

            username

        )

        if user is None:

            return False

        user.active = False

        self.audit(

            username,

            "USER_DEACTIVATED",

        )

        return True

    # =====================================================
    # AUDIT LOG
    # =====================================================

    def audit(

        self,

        username: str,

        action: str,

        details: str = "",

    ):

        self.audit_log.append(

            AuditEvent(

                timestamp=datetime.utcnow(),

                username=username,

                action=action,

                details=details,

            )

        )

    # -------------------------------------------------

    def audit_history(

        self,

        limit: Optional[int] = None,

    ):

        if limit is None:

            return list(

                self.audit_log

            )

        return self.audit_log[-limit:]

    # =====================================================
    # LOGIN STATISTICS
    # =====================================================

    def login_statistics(

        self,

    ):

        return {

            "users": len(

                self.users

            ),

            "active_users": sum(

                user.active

                for user in self.users.values()

            ),

            "sessions": len(

                self.sessions

            ),

            "failed_attempts": sum(

                self.failed_attempts.values()

            ),

            "audit_events": len(

                self.audit_log

            ),

            "api_keys": len(

                self.api_keys

            ),

        }

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

    ):

        return {

            "registered_users": len(

                self.users

            ),

            "active_sessions": len(

                self.active_sessions()

            ),

            "failed_logins": sum(

                self.failed_attempts.values()

            ),

            "audit_records": len(

                self.audit_log

            ),

            "api_keys": len(

                self.api_keys

            ),

        }
        # =====================================================
    # EXPORT USERS
    # =====================================================

    def export_users(
        self,
    ):

        users = []

        for user in self.users.values():

            users.append({

                "username": user.username,

                "password_hash": user.password_hash,

                "salt": user.salt,

                "role": user.role,

                "active": user.active,

                "created_at": user.created_at.isoformat(),

                "last_login": (
                    user.last_login.isoformat()
                    if user.last_login
                    else None
                ),

                "permissions": list(
                    user.permissions
                ),

            })

        return users

    # =====================================================
    # IMPORT USERS
    # =====================================================

    def import_users(
        self,
        users: List[Dict],
    ):

        imported = 0

        for data in users:

            user = User(

                username=data["username"],

                password_hash=data["password_hash"],

                salt=data["salt"],

                role=data.get(
                    "role",
                    "user",
                ),

                active=data.get(
                    "active",
                    True,
                ),

                created_at=datetime.fromisoformat(
                    data["created_at"]
                ),

                last_login=(
                    datetime.fromisoformat(
                        data["last_login"]
                    )
                    if data.get("last_login")
                    else None
                ),

                permissions=set(
                    data.get(
                        "permissions",
                        [],
                    )
                ),

            )

            self.users[
                user.username
            ] = user

            imported += 1

        return imported

    # =====================================================
    # EXPORT AUDIT LOG
    # =====================================================

    def export_audit_log(
        self,
    ):

        return [

            {

                "timestamp": event.timestamp.isoformat(),

                "username": event.username,

                "action": event.action,

                "details": event.details,

            }

            for event in self.audit_log

        ]

    # =====================================================
    # IMPORT AUDIT LOG
    # =====================================================

    def import_audit_log(
        self,
        records: List[Dict],
    ):

        for record in records:

            self.audit_log.append(

                AuditEvent(

                    timestamp=datetime.fromisoformat(
                        record["timestamp"]
                    ),

                    username=record["username"],

                    action=record["action"],

                    details=record.get(
                        "details",
                        "",
                    ),

                )

            )

        return len(records)

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ):

        self.users.clear()

        self.sessions.clear()

        self.audit_log.clear()

        self.api_keys.clear()

        self.failed_attempts.clear()

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self,
    ):

        removed = self.cleanup_sessions()

        return {

            "expired_sessions_removed": removed,

            "active_sessions": len(
                self.sessions
            ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ):

        return (

            "SecurityManager("

            f"users={len(self.users)}, "

            f"sessions={len(self.sessions)}, "

            f"api_keys={len(self.api_keys)}"

            ")"

        )

    # -------------------------------------------------

    def __str__(
        self,
    ):

        stats = self.login_statistics()

        return (

            "Security Manager\n"

            f"Users           : {stats['users']}\n"

            f"Active Users    : {stats['active_users']}\n"

            f"Sessions        : {stats['sessions']}\n"

            f"API Keys        : {stats['api_keys']}\n"

            f"Audit Events    : {stats['audit_events']}\n"

            f"Failed Attempts : {stats['failed_attempts']}"

        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

security_manager = SecurityManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "User",

    "Session",

    "AuditEvent",

    "SecurityManager",

    "security_manager",

]

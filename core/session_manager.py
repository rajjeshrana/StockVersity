from __future__ import annotations

import json
import threading
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================
# SESSION
# =====================================================

@dataclass(slots=True)
class Session:
    """Represents one application session."""

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    user: str = "Guest"

    project: str = ""

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    last_activity: datetime = field(
        default_factory=datetime.utcnow
    )

    expires_at: Optional[datetime] = None

    active: bool = True

    authenticated: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================
# SESSION MANAGER
# =====================================================

class SessionManager:

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

        if getattr(
            self,
            "_initialized",
            False,
        ):
            return

        self._initialized = True

        self.manager_lock = threading.RLock()

        self.storage_directory = (
            Path.home()
            / ".stockversity"
        )

        self.storage_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.storage_file = (
            self.storage_directory
            / "session.json"
        )

        self.timeout_minutes = 30

        self.sessions: Dict[
            str,
            Session,
        ] = {}

        self.current_session: Optional[
            Session
        ] = None

        self.load()

    # =====================================================
    # CREATE SESSION
    # =====================================================

    def create_session(

        self,

        user: str = "Guest",

        project: str = "",

    ) -> Session:

        session = Session(

            user=user,

            project=project,

            expires_at=(
                datetime.utcnow()
                + timedelta(
                    minutes=self.timeout_minutes
                )
            ),
        )

        self.sessions[
            session.id
        ] = session

        self.current_session = session

        self.save()

        return session

    # =====================================================
    # CURRENT SESSION
    # =====================================================

    def current(self) -> Optional[Session]:

        return self.current_session

    # =====================================================
    # GET SESSION
    # =====================================================

    def get(

        self,

        session_id: str,

    ) -> Optional[Session]:

        return self.sessions.get(
            session_id
        )

    # =====================================================
    # ALL SESSIONS
    # =====================================================

    def all_sessions(self) -> List[Session]:

        return list(
            self.sessions.values()
        )

    # =====================================================
    # LOGIN
    # =====================================================

    def login(

        self,

        username: str,

    ) -> Session:

        if self.current_session is None:

            self.create_session(
                username
            )

        self.current_session.user = username

        self.current_session.authenticated = True

        self.current_session.active = True

        self.touch()

        self.save()

        return self.current_session

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(self) -> bool:

        if self.current_session is None:
            return False

        self.current_session.authenticated = False

        self.current_session.active = False

        self.save()

        return True
        # =====================================================
    # TOUCH SESSION
    # =====================================================

    def touch(self) -> bool:

        if self.current_session is None:

            return False

        now = datetime.utcnow()

        self.current_session.last_activity = now

        self.current_session.expires_at = (
            now
            + timedelta(
                minutes=self.timeout_minutes
            )
        )

        self.save()

        return True

    # =====================================================
    # SESSION EXPIRED
    # =====================================================

    def expired(

        self,

        session: Optional[Session] = None,

    ) -> bool:

        session = session or self.current_session

        if session is None:

            return True

        if session.expires_at is None:

            return False

        return datetime.utcnow() >= session.expires_at

    # =====================================================
    # REMOVE SESSION
    # =====================================================

    def remove(

        self,

        session_id: str,

    ) -> bool:

        if session_id not in self.sessions:

            return False

        if (
            self.current_session
            and self.current_session.id == session_id
        ):

            self.current_session = None

        del self.sessions[session_id]

        self.save()

        return True

    # =====================================================
    # PROJECT
    # =====================================================

    def project(self) -> str:

        if self.current_session is None:

            return ""

        return self.current_session.project

    # =====================================================
    # SET PROJECT
    # =====================================================

    def set_project(

        self,

        project: str,

    ) -> bool:

        if self.current_session is None:

            return False

        self.current_session.project = project

        self.touch()

        return self.save()

    # =====================================================
    # SAVE
    # =====================================================

    def save(self) -> bool:

        try:

            data = {

                "current": (
                    self.current_session.id
                    if self.current_session
                    else None
                ),

                "timeout_minutes": self.timeout_minutes,

                "sessions": [],

            }

            for session in self.sessions.values():

                item = asdict(session)

                item["created_at"] = (
                    session.created_at.isoformat()
                )

                item["last_activity"] = (
                    session.last_activity.isoformat()
                )

                item["expires_at"] = (
                    session.expires_at.isoformat()
                    if session.expires_at
                    else None
                )

                data["sessions"].append(item)

            self.storage_file.write_text(

                json.dumps(
                    data,
                    indent=4,
                ),

                encoding="utf-8",

            )

            return True

        except Exception:

            return False

    # =====================================================
    # LOAD
    # =====================================================

    def load(self) -> bool:

        if not self.storage_file.exists():

            return False

        try:

            data = json.loads(

                self.storage_file.read_text(

                    encoding="utf-8"

                )

            )

            self.sessions.clear()

            self.timeout_minutes = data.get(

                "timeout_minutes",

                30,

            )

            current_id = data.get(

                "current"

            )

            for item in data.get(

                "sessions",

                [],

            ):

                session = Session(

                    id=item["id"],

                    user=item.get(

                        "user",

                        "Guest",

                    ),

                    project=item.get(

                        "project",

                        "",

                    ),

                    created_at=datetime.fromisoformat(

                        item["created_at"]

                    ),

                    last_activity=datetime.fromisoformat(

                        item["last_activity"]

                    ),

                    expires_at=(

                        datetime.fromisoformat(

                            item["expires_at"]

                        )

                        if item.get(

                            "expires_at"

                        )

                        else None

                    ),

                    active=item.get(

                        "active",

                        True,

                    ),

                    authenticated=item.get(

                        "authenticated",

                        False,

                    ),

                    metadata=item.get(

                        "metadata",

                        {},

                    ),

                )

                self.sessions[
                    session.id
                ] = session

            self.current_session = self.sessions.get(

                current_id

            )

            return True

        except Exception:

            return False
            # =====================================================
    # ACTIVE SESSIONS
    # =====================================================

    def active_sessions(self) -> List[Session]:

        return [

            session

            for session in self.sessions.values()

            if session.active

        ]

    # =====================================================
    # AUTHENTICATED
    # =====================================================

    def authenticated(self) -> bool:

        return (

            self.current_session is not None

            and self.current_session.authenticated

        )

    # =====================================================
    # SESSION COUNT
    # =====================================================

    def session_count(self) -> int:

        return len(

            self.sessions

        )

    # =====================================================
    # CLEAR ALL SESSIONS
    # =====================================================

    def clear(self) -> bool:

        self.sessions.clear()

        self.current_session = None

        return self.save()

    # =====================================================
    # CLEANUP EXPIRED SESSIONS
    # =====================================================

    def cleanup(self) -> int:

        removed = 0

        expired_ids = [

            session.id

            for session in self.sessions.values()

            if self.expired(session)

        ]

        for session_id in expired_ids:

            if self.remove(session_id):

                removed += 1

        return removed

    # =====================================================
    # SESSION SUMMARY
    # =====================================================

    def summary(self) -> Dict[str, Any]:

        return {

            "total_sessions": len(

                self.sessions

            ),

            "active_sessions": len(

                self.active_sessions()

            ),

            "authenticated": self.authenticated(),

            "current_user": (

                self.current_session.user

                if self.current_session

                else None

            ),

            "current_project": (

                self.current_session.project

                if self.current_session

                else None

            ),

            "timeout_minutes": self.timeout_minutes,

        }

    # =====================================================
    # EXPORT SESSIONS
    # =====================================================

    def export_sessions(self) -> List[Dict[str, Any]]:

        sessions: List[Dict[str, Any]] = []

        for session in self.sessions.values():

            sessions.append(

                {

                    "id": session.id,

                    "user": session.user,

                    "project": session.project,

                    "created_at": session.created_at.isoformat(),

                    "last_activity": session.last_activity.isoformat(),

                    "expires_at": (

                        session.expires_at.isoformat()

                        if session.expires_at

                        else None

                    ),

                    "active": session.active,

                    "authenticated": session.authenticated,

                    "metadata": session.metadata,

                }

            )

        return sessions

    # =====================================================
    # IMPORT SESSIONS
    # =====================================================

    def import_sessions(

        self,

        sessions: List[Dict[str, Any]],

    ) -> bool:

        try:

            self.sessions.clear()

            self.current_session = None

            first_session: Optional[Session] = None

            for item in sessions:

                session = Session(

                    id=item.get(

                        "id",

                        str(uuid.uuid4()),

                    ),

                    user=item.get(

                        "user",

                        "Guest",

                    ),

                    project=item.get(

                        "project",

                        "",

                    ),

                    created_at=datetime.fromisoformat(

                        item["created_at"]

                    ),

                    last_activity=datetime.fromisoformat(

                        item["last_activity"]

                    ),

                    expires_at=(

                        datetime.fromisoformat(

                            item["expires_at"]

                        )

                        if item.get(

                            "expires_at"

                        )

                        else None

                    ),

                    active=item.get(

                        "active",

                        True,

                    ),

                    authenticated=item.get(

                        "authenticated",

                        False,

                    ),

                    metadata=item.get(

                        "metadata",

                        {},

                    ),

                )

                self.sessions[

                    session.id

                ] = session

                if first_session is None:

                    first_session = session

            self.current_session = first_session

            return self.save()

        except Exception:

            return False
            # =====================================================
    # HEALTH
    # =====================================================

    def health(self) -> Dict[str, Any]:

        return {

            "storage_file": str(

                self.storage_file

            ),

            "exists": self.storage_file.exists(),

            "total_sessions": len(

                self.sessions

            ),

            "current_session": (

                self.current_session.id

                if self.current_session

                else None

            ),

            "timeout_minutes": self.timeout_minutes,

        }

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(self) -> Dict[str, Any]:

        authenticated = sum(

            1

            for session in self.sessions.values()

            if session.authenticated

        )

        active = sum(

            1

            for session in self.sessions.values()

            if session.active

        )

        return {

            "total_sessions": len(

                self.sessions

            ),

            "active_sessions": active,

            "authenticated_sessions": authenticated,

            "timeout_minutes": self.timeout_minutes,

        }

    # =====================================================
    # STARTUP
    # =====================================================

    def startup(self) -> Dict[str, Any]:
        """
        Startup hook.

        Loads saved sessions and removes any
        expired sessions.
        """

        self.load()

        self.cleanup()

        return self.statistics()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown hook.

        Saves session data before application exits.
        """

        self.save()

        return self.statistics()

    # =====================================================
    # RELOAD
    # =====================================================

    def reload(self) -> bool:

        return self.load()

    # =====================================================
    # REPR
    # =====================================================

    def __repr__(self) -> str:

        stats = self.statistics()

        return (

            "SessionManager("

            f"sessions={stats['total_sessions']}, "

            f"active={stats['active_sessions']}, "

            f"authenticated={stats['authenticated_sessions']}"

            ")"

        )

    # =====================================================
    # STR
    # =====================================================

    def __str__(self) -> str:

        stats = self.statistics()

        return (

            "Session Manager\n"

            f"Total Sessions         : {stats['total_sessions']}\n"

            f"Active Sessions        : {stats['active_sessions']}\n"

            f"Authenticated Sessions : {stats['authenticated_sessions']}\n"

            f"Timeout (Minutes)      : {stats['timeout_minutes']}"
        )


# =====================================================
# GLOBAL SINGLETON
# =====================================================

session_manager = SessionManager()


# =====================================================
# EXPORTS
# =====================================================

__all__ = [

    "Session",

    "SessionManager",

    "session_manager",

]

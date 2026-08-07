from __future__ import annotations

import json
import logging
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from core.upstox_client import UpstoxClient


# ==========================================================
# LOGIN STATUS
# ==========================================================

class LoginStatus(Enum):

    LOGGED_OUT = "Logged Out"

    LOGGING_IN = "Logging In"

    LOGGED_IN = "Logged In"

    TOKEN_EXPIRED = "Token Expired"

    REFRESHING = "Refreshing"

    ERROR = "Error"


# ==========================================================
# LOGIN CONTROLLER
# ==========================================================

class LoginController:

    TOKEN_FILE = Path("config/session.json")

    def __init__(self):

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.status = LoginStatus.LOGGED_OUT

        self.client: Optional[
            UpstoxClient
        ] = None

        self.user: Dict[str, Any] = {}

        self.login_time: Optional[
            datetime
        ] = None

        self.access_token: Optional[
            str
        ] = None

        self.refresh_token: Optional[
            str
        ] = None

        self.remember_me = True

        self.logger.info(
            "LoginController initialized."
        )
            # ==========================================================
    # LOGIN
    # ==========================================================

    def login(
        self,
        api_key: str,
        api_secret: str,
        redirect_uri: str,
    ) -> bool:
        """
        Authenticate user with Upstox.
        """

        self.logger.info(
            "Login requested."
        )

        self.status = LoginStatus.LOGGING_IN

        try:

            self.client = UpstoxClient(

                api_key=api_key,

                api_secret=api_secret,

                redirect_uri=redirect_uri,

            )

            success = self.client.authenticate()

            if not success:

                self.status = LoginStatus.ERROR

                self.logger.error(
                    "Authentication failed."
                )

                return False

            self.access_token = (
                self.client.access_token
            )

            self.refresh_token = (
                self.client.refresh_token
            )

            self.login_time = datetime.now()

            self.status = LoginStatus.LOGGED_IN

            self.save_session()

            self.logger.info(
                "Login successful."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            self.status = LoginStatus.ERROR

            return False

    # ==========================================================
    # LOGIN USING EXISTING CLIENT
    # ==========================================================

    def login_with_client(
        self,
        client: UpstoxClient,
    ) -> bool:
        """
        Use an already authenticated client.
        """

        self.client = client

        try:

            self.access_token = (
                client.access_token
            )

            self.refresh_token = (
                client.refresh_token
            )

            self.login_time = datetime.now()

            self.status = LoginStatus.LOGGED_IN

            self.save_session()

            return True

        except Exception as ex:

            self.logger.exception(ex)

            self.status = LoginStatus.ERROR

            return False

    # ==========================================================
    # AUTHENTICATION STATUS
    # ==========================================================

    def is_logged_in(self) -> bool:

        return (
            self.status == LoginStatus.LOGGED_IN
        )

    # ==========================================================
    # CONNECTION STATUS
    # ==========================================================

    def is_connected(self) -> bool:

        if self.client is None:

            return False

        try:

            return self.client.is_connected()

        except Exception:

            return False

    # ==========================================================
    # GET CLIENT
    # ==========================================================

    def get_client(self) -> Optional[UpstoxClient]:

        return self.client

    # ==========================================================
    # LOGIN INFORMATION
    # ==========================================================

    def login_info(self) -> Dict[str, Any]:

        return {

            "status": self.status.value,

            "logged_in": self.is_logged_in(),

            "connected": self.is_connected(),

            "login_time": self.login_time,

            "remember_me": self.remember_me,

        }

    # ==========================================================
    # LOGIN DURATION
    # ==========================================================

    def login_duration(self):

        if self.login_time is None:

            return None

        return datetime.now() - self.login_time
        # ==========================================================
    # AUTHORIZATION URL
    # ==========================================================

    def get_authorization_url(self) -> str:
        """
        Generate Upstox OAuth authorization URL.
        """

        if self.client is None:
            raise RuntimeError(
                "Upstox client is not initialized."
            )

        return self.client.get_authorization_url()

    # ==========================================================
    # OPEN LOGIN PAGE
    # ==========================================================

    def open_login_page(self) -> bool:
        """
        Open Upstox login page in the default browser.
        """

        import webbrowser

        try:

            url = self.get_authorization_url()

            webbrowser.open(url)

            self.logger.info(
                "Authorization page opened."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # AUTHORIZE
    # ==========================================================

    def authorize(
        self,
        authorization_code: str,
    ) -> bool:
        """
        Exchange authorization code for access token.
        """

        if self.client is None:

            self.logger.error(
                "Client not initialized."
            )

            return False

        self.status = LoginStatus.LOGGING_IN

        try:

            success = self.client.exchange_code(
                authorization_code
            )

            if not success:

                self.status = LoginStatus.ERROR

                return False

            self.access_token = (
                self.client.access_token
            )

            self.refresh_token = (
                self.client.refresh_token
            )

            self.login_time = datetime.now()

            self.status = LoginStatus.LOGGED_IN

            self.save_session()

            self.logger.info(
                "OAuth authentication completed."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            self.status = LoginStatus.ERROR

            return False

    # ==========================================================
    # CALLBACK
    # ==========================================================

    def handle_callback(
        self,
        callback_url: str,
    ) -> bool:
        """
        Handle OAuth callback URL.
        """

        if self.client is None:

            return False

        try:

            return self.client.process_callback(
                callback_url
            )

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # VERIFY SESSION
    # ==========================================================

    def verify_session(self) -> bool:
        """
        Verify current authentication.
        """

        if self.client is None:

            return False

        try:

            return self.client.verify_session()

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # TOKEN VALIDITY
    # ==========================================================

    def is_token_valid(self) -> bool:
        """
        Check token validity.
        """

        if self.client is None:

            return False

        try:

            return self.client.token_valid()

        except Exception:

            return False
            # ==========================================================
    # SAVE SESSION
    # ==========================================================

    def save_session(self) -> bool:
        """
        Save current session to disk.
        """

        if not self.remember_me:
            return False

        try:

            self.TOKEN_FILE.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            session = {

                "access_token": self.access_token,

                "refresh_token": self.refresh_token,

                "login_time": (
                    self.login_time.isoformat()
                    if self.login_time
                    else None
                ),

                "status": self.status.value,

            }

            with open(
                self.TOKEN_FILE,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    session,
                    file,
                    indent=4,
                )

            self.logger.info(
                "Session saved successfully."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # LOAD SESSION
    # ==========================================================

    def load_session(self) -> bool:
        """
        Load saved session.
        """

        if not self.TOKEN_FILE.exists():

            return False

        try:

            with open(
                self.TOKEN_FILE,
                "r",
                encoding="utf-8",
            ) as file:

                session = json.load(file)

            self.access_token = session.get(
                "access_token"
            )

            self.refresh_token = session.get(
                "refresh_token"
            )

            login_time = session.get(
                "login_time"
            )

            if login_time:

                self.login_time = datetime.fromisoformat(
                    login_time
                )

            self.logger.info(
                "Session loaded."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # CLEAR SESSION
    # ==========================================================

    def clear_session(self) -> None:
        """
        Delete saved session.
        """

        try:

            if self.TOKEN_FILE.exists():

                self.TOKEN_FILE.unlink()

                self.logger.info(
                    "Saved session removed."
                )

        except Exception as ex:

            self.logger.exception(ex)

    # ==========================================================
    # RESTORE SESSION
    # ==========================================================

    def restore_session(self) -> bool:
        """
        Restore previous login session.
        """

        if not self.load_session():

            return False

        if self.client is None:

            return False

        try:

            self.client.access_token = (
                self.access_token
            )

            self.client.refresh_token = (
                self.refresh_token
            )

            if self.verify_session():

                self.status = (
                    LoginStatus.LOGGED_IN
                )

                self.logger.info(
                    "Previous session restored."
                )

                return True

            self.status = (
                LoginStatus.TOKEN_EXPIRED
            )

            return False

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # REFRESH ACCESS TOKEN
    # ==========================================================

    def refresh_access_token(self) -> bool:
        """
        Refresh expired token.
        """

        if self.client is None:

            return False

        self.status = LoginStatus.REFRESHING

        try:

            success = self.client.refresh_token()

            if not success:

                self.status = (
                    LoginStatus.TOKEN_EXPIRED
                )

                return False

            self.access_token = (
                self.client.access_token
            )

            self.refresh_token = (
                self.client.refresh_token
            )

            self.save_session()

            self.status = (
                LoginStatus.LOGGED_IN
            )

            self.logger.info(
                "Access token refreshed."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            self.status = LoginStatus.ERROR

            return False

    # ==========================================================
    # SESSION EXISTS
    # ==========================================================

    def session_exists(self) -> bool:
        """
        Check whether a saved session exists.
        """

        return self.TOKEN_FILE.exists()
        # ==========================================================
    # AUTO LOGIN
    # ==========================================================

    def auto_login(self) -> bool:
        """
        Attempt automatic login using saved session.
        """

        self.logger.info(
            "Attempting auto login..."
        )

        if not self.session_exists():

            self.logger.info(
                "No saved session found."
            )

            return False

        if not self.restore_session():

            self.logger.warning(
                "Session restore failed."
            )

            return False

        self.logger.info(
            "Auto login successful."
        )

        return True

    # ==========================================================
    # SESSION VALIDATION
    # ==========================================================

    def validate_session(self) -> bool:
        """
        Validate current session.
        """

        if self.client is None:

            return False

        try:

            if self.verify_session():

                return True

            self.logger.warning(
                "Session expired."
            )

            self.status = LoginStatus.TOKEN_EXPIRED

            return False

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # ENSURE LOGIN
    # ==========================================================

    def ensure_login(self) -> bool:
        """
        Ensure that a valid session exists.
        """

        if self.validate_session():

            return True

        self.logger.info(
            "Trying token refresh..."
        )

        if self.refresh_access_token():

            return True

        self.status = LoginStatus.TOKEN_EXPIRED

        return False

    # ==========================================================
    # USER PROFILE
    # ==========================================================

    def load_user_profile(self) -> bool:
        """
        Load authenticated user profile.
        """

        if self.client is None:

            return False

        try:

            profile = self.client.get_profile()

            if profile is None:

                return False

            self.user = profile

            self.logger.info(
                "User profile loaded."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # GET USER
    # ==========================================================

    def get_user(self) -> Dict[str, Any]:
        """
        Return user profile.
        """

        return self.user

    # ==========================================================
    # USER NAME
    # ==========================================================

    def user_name(self) -> str:

        return self.user.get(
            "user_name",
            "",
        )

    # ==========================================================
    # CLIENT ID
    # ==========================================================

    def client_id(self) -> str:

        return self.user.get(
            "client_id",
            "",
        )

    # ==========================================================
    # EMAIL
    # ==========================================================

    def email(self) -> str:

        return self.user.get(
            "email",
            "",
        )

    # ==========================================================
    # MOBILE
    # ==========================================================

    def mobile(self) -> str:

        return self.user.get(
            "mobile",
            "",
        )

    # ==========================================================
    # PROFILE SUMMARY
    # ==========================================================

    def profile_summary(self) -> Dict[str, Any]:
        """
        Return profile summary.
        """

        return {

            "name": self.user_name(),

            "client_id": self.client_id(),

            "email": self.email(),

            "mobile": self.mobile(),

            "login_time": self.login_time,

            "status": self.status.value,

        }

    # ==========================================================
    # SESSION AGE
    # ==========================================================

    def session_age(self):
        """
        Return session age.
        """

        if self.login_time is None:

            return None

        return datetime.now() - self.login_time
        # ==========================================================
    # LOGOUT
    # ==========================================================

    def logout(self) -> bool:
        """
        Logout current user.
        """

        self.logger.info(
            "Logging out..."
        )

        try:

            if self.client:

                try:

                    self.client.logout()

                except Exception as ex:

                    self.logger.exception(ex)

            self.clear_session()

            self.access_token = None

            self.refresh_token = None

            self.user.clear()

            self.login_time = None

            self.status = LoginStatus.LOGGED_OUT

            self.logger.info(
                "Logout successful."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            self.status = LoginStatus.ERROR

            return False

    # ==========================================================
    # RESET CONTROLLER
    # ==========================================================

    def reset(self) -> None:
        """
        Reset controller state.
        """

        self.client = None

        self.user = {}

        self.access_token = None

        self.refresh_token = None

        self.login_time = None

        self.status = LoginStatus.LOGGED_OUT

    # ==========================================================
    # REMEMBER ME
    # ==========================================================

    def set_remember_me(
        self,
        remember: bool,
    ) -> None:
        """
        Enable or disable Remember Me.
        """

        self.remember_me = remember

    def get_remember_me(self) -> bool:

        return self.remember_me

    # ==========================================================
    # TOKEN EXPIRY
    # ==========================================================

    def token_expired(self) -> bool:
        """
        Check whether token has expired.
        """

        return (
            self.status ==
            LoginStatus.TOKEN_EXPIRED
        )

    # ==========================================================
    # LOGIN STATE
    # ==========================================================

    def login_state(self) -> str:

        return self.status.value

    # ==========================================================
    # SESSION STATUS
    # ==========================================================

    def session_status(self) -> Dict[str, Any]:
        """
        Return session information.
        """

        return {

            "logged_in": self.is_logged_in(),

            "connected": self.is_connected(),

            "token_valid": self.is_token_valid(),

            "remember_me": self.remember_me,

            "status": self.status.value,

            "login_time": self.login_time,

            "session_age": self.session_age(),

        }

    # ==========================================================
    # LOGIN REQUIRED
    # ==========================================================

    def login_required(self) -> bool:
        """
        Determine if login is required.
        """

        if not self.is_logged_in():

            return True

        if not self.is_token_valid():

            return True

        return False

    # ==========================================================
    # AUTHENTICATION HEALTH
    # ==========================================================

    def authentication_health(
        self,
    ) -> Dict[str, Any]:
        """
        Authentication diagnostics.
        """

        return {

            "status": self.status.value,

            "client_initialized":
                self.client is not None,

            "access_token":
                self.access_token is not None,

            "refresh_token":
                self.refresh_token is not None,

            "user_loaded":
                bool(self.user),

            "connected":
                self.is_connected(),

            "session_exists":
                self.session_exists(),

        }

    # ==========================================================
    # UPDATE LOGIN STATUS
    # ==========================================================

    def set_status(
        self,
        status: LoginStatus,
    ) -> None:
        """
        Update login status.
        """

        self.status = status

        self.logger.info(
            "Login Status: %s",
            status.value,
        )
            # ==========================================================
    # REFRESH USER PROFILE
    # ==========================================================

    def refresh_user_profile(self) -> bool:
        """
        Reload user profile from Upstox.
        """

        if self.client is None:
            return False

        try:

            profile = self.client.get_profile()

            if not profile:
                return False

            self.user = profile

            self.logger.info(
                "User profile refreshed."
            )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # ==========================================================
    # USER DISPLAY NAME
    # ==========================================================

    def display_name(self) -> str:
        """
        Display name for UI.
        """

        return (
            self.user.get("user_name")
            or self.user.get("name")
            or "Unknown User"
        )

    # ==========================================================
    # PROFILE AVAILABLE
    # ==========================================================

    def has_profile(self) -> bool:
        """
        Check whether profile has been loaded.
        """

        return bool(self.user)

    # ==========================================================
    # CONTROLLER HEALTH
    # ==========================================================

    def health_check(self) -> Dict[str, Any]:
        """
        Health check for LoginController.
        """

        return {

            "healthy": (
                self.client is not None
                and self.status != LoginStatus.ERROR
            ),

            "status": self.status.value,

            "logged_in": self.is_logged_in(),

            "connected": self.is_connected(),

            "token_valid": self.is_token_valid(),

            "profile_loaded": self.has_profile(),

            "remember_me": self.remember_me,

        }

    # ==========================================================
    # RUNTIME STATISTICS
    # ==========================================================

    def runtime_statistics(self) -> Dict[str, Any]:
        """
        Runtime statistics.
        """

        return {

            "login_time": self.login_time,

            "session_age": self.session_age(),

            "logged_in": self.is_logged_in(),

            "status": self.status.value,

        }

    # ==========================================================
    # DIAGNOSTICS
    # ==========================================================

    def diagnostics(self) -> Dict[str, Any]:
        """
        Complete diagnostics.
        """

        return {

            "profile": self.profile_summary(),

            "session": self.session_status(),

            "health": self.health_check(),

            "runtime": self.runtime_statistics(),

        }

    # ==========================================================
    # DEBUG REPORT
    # ==========================================================

    def debug_report(self) -> Dict[str, Any]:
        """
        Full debug information.
        """

        return {

            "controller": self.__class__.__name__,

            "status": self.status.value,

            "client_initialized": self.client is not None,

            "user_loaded": self.has_profile(),

            "diagnostics": self.diagnostics(),

        }

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __repr__(self):

        return (

            f"<LoginController "

            f"status={self.status.value}>"

        )

    def __str__(self):

        return (

            f"LoginController("

            f"{self.status.value})"

        )
        # ==========================================================
    # CLEANUP
    # ==========================================================

    def cleanup(self) -> None:
        """
        Cleanup controller resources.
        """

        self.logger.info(
            "Cleaning LoginController..."
        )

        self.user.clear()

        self.access_token = None

        self.refresh_token = None

        self.client = None

        self.login_time = None

        self.status = LoginStatus.LOGGED_OUT

    # ==========================================================
    # CLOSE
    # ==========================================================

    def close(self) -> None:
        """
        Close controller.
        """

        try:

            self.logout()

        except Exception as ex:

            self.logger.exception(ex)

        finally:

            self.cleanup()

    # ==========================================================
    # EXPORT SESSION
    # ==========================================================

    def export_session(self) -> Dict[str, Any]:
        """
        Export current session information.
        """

        return {

            "status": self.status.value,

            "login_time": self.login_time,

            "remember_me": self.remember_me,

            "profile": self.user.copy(),

        }

    # ==========================================================
    # IMPORT SESSION
    # ==========================================================

    def import_session(
        self,
        session: Dict[str, Any],
    ) -> None:
        """
        Restore session from dictionary.
        """

        self.user = session.get(
            "profile",
            {},
        )

        self.login_time = session.get(
            "login_time"
        )

        self.remember_me = session.get(
            "remember_me",
            True,
        )

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.close()

        return False

    # ==========================================================
    # RESET
    # ==========================================================

    def reset_controller(self) -> None:
        """
        Reset LoginController.
        """

        self.cleanup()

    # ==========================================================
    # VERSION
    # ==========================================================

    @staticmethod
    def version() -> str:

        return "1.0.0"

    # ==========================================================
    # FACTORY
    # ==========================================================

    @classmethod
    def create(cls):

        return cls()


# ==========================================================
# FACTORY FUNCTION
# ==========================================================

def create_login_controller() -> LoginController:
    """
    Factory function.
    """

    return LoginController()


# ==========================================================
# END OF FILE
# ==========================================================
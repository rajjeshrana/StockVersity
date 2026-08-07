"""
==========================================================
StockVersity Scanner Pro
Authentication Manager
Version : 4.0
==========================================================

Supports

• OAuth2 Authentication
• Secure Token Storage
• Session Management
• Automatic Token Loading
• Multi Broker Ready

Supported Providers

- Upstox
- Shoonya
- Future Brokers

"""

from __future__ import annotations

import json
import logging
import secrets
import urllib.parse
import webbrowser
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Dict
from typing import Optional

import requests


# ==========================================================
# Constants
# ==========================================================

TOKEN_DIRECTORY = Path.home() / ".stockversity"

TOKEN_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)

TOKEN_FILE = TOKEN_DIRECTORY / "auth.json"


# ==========================================================
# Authentication Models
# ==========================================================

@dataclass(slots=True)
class AuthToken:

    provider: str

    access_token: str

    refresh_token: str = ""

    token_type: str = "Bearer"

    expires_at: Optional[datetime] = None

    created_at: datetime = datetime.now()

    user_id: str = ""

    client_id: str = ""

    def is_expired(self) -> bool:

        if self.expires_at is None:
            return False

        return datetime.now() >= self.expires_at

    def expires_in(self) -> int:

        if self.expires_at is None:
            return -1

        remaining = self.expires_at - datetime.now()

        return max(
            int(remaining.total_seconds()),
            0
        )


# ==========================================================
# Base Authentication
# ==========================================================

class AuthenticationProvider(ABC):

    def __init__(self):

        self.token: Optional[AuthToken] = None

        self.authenticated = False

    @abstractmethod
    def login(self) -> bool:
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def refresh(self) -> bool:
        pass

    @abstractmethod
    def authorization_url(self) -> str:
        pass

    @abstractmethod
    def exchange_code(
        self,
        code: str
    ) -> bool:
        pass


# ==========================================================
# Authentication Manager
# ==========================================================

class AuthenticationManager:

    """
    Handles secure storage and retrieval of authentication
    tokens for all supported brokers.
    """

    def __init__(self):

        self.tokens: Dict[str, AuthToken] = {}

        self.load_tokens()

    # ------------------------------------------------------
    # Token Storage
    # ------------------------------------------------------

    def save_tokens(self) -> None:

        data = {}

        for provider, token in self.tokens.items():

            data[provider] = {

                "provider": token.provider,

                "access_token": token.access_token,

                "refresh_token": token.refresh_token,

                "token_type": token.token_type,

                "expires_at": (
                    token.expires_at.isoformat()
                    if token.expires_at
                    else None
                ),

                "created_at": token.created_at.isoformat(),

                "user_id": token.user_id,

                "client_id": token.client_id

            }

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as fp:

            json.dump(
                data,
                fp,
                indent=4
            )

    # ------------------------------------------------------
    # Load Tokens
    # ------------------------------------------------------

    def load_tokens(self) -> None:

        self.tokens.clear()

        if not TOKEN_FILE.exists():
            return

        with open(
            TOKEN_FILE,
            "r",
            encoding="utf-8"
        ) as fp:

            raw = json.load(fp)

        for provider, item in raw.items():

            expires = None

            if item.get("expires_at"):

                expires = datetime.fromisoformat(
                    item["expires_at"]
                )

            created = datetime.fromisoformat(
                item["created_at"]
            )

            self.tokens[provider] = AuthToken(

                provider=item["provider"],

                access_token=item["access_token"],

                refresh_token=item.get(
                    "refresh_token",
                    ""
                ),

                token_type=item.get(
                    "token_type",
                    "Bearer"
                ),

                expires_at=expires,

                created_at=created,

                user_id=item.get(
                    "user_id",
                    ""
                ),

                client_id=item.get(
                    "client_id",
                    ""
                )

            )

    # ------------------------------------------------------
    # CRUD
    # ------------------------------------------------------

    def set_token(
        self,
        token: AuthToken
    ) -> None:

        self.tokens[token.provider] = token

        self.save_tokens()

    def get_token(
        self,
        provider: str
    ) -> Optional[AuthToken]:

        return self.tokens.get(provider)

    def remove_token(
        self,
        provider: str
    ) -> None:

        if provider in self.tokens:

            del self.tokens[provider]

            self.save_tokens()

    def clear_all(self) -> None:

        self.tokens.clear()

        self.save_tokens()

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    def has_token(
        self,
        provider: str
    ) -> bool:

        return provider in self.tokens

    def token_valid(
        self,
        provider: str
    ) -> bool:

        token = self.get_token(provider)

        if token is None:
            return False

        return not token.is_expired()

    def token_expiring(
        self,
        provider: str,
        minutes: int = 10
    ) -> bool:

        token = self.get_token(provider)

        if token is None:

            return True

        if token.expires_at is None:

            return False

        return token.expires_at <= (
            datetime.now() +
            timedelta(minutes=minutes)
        )

    # ------------------------------------------------------
    # Session
    # ------------------------------------------------------

    def session_summary(self) -> Dict:

        summary = {}

        for provider, token in self.tokens.items():

            summary[provider] = {

                "authenticated": (
                    not token.is_expired()
                ),

                "expires_in": token.expires_in(),

                "user": token.user_id,

                "client_id": token.client_id

            }

        return summary


# ==========================================================
# OAuth Authentication
# ==========================================================

class OAuthAuthentication(AuthenticationProvider):

    """
    Generic OAuth2 Authentication Provider.
    """

    def __init__(
        self,
        provider: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        auth_endpoint: str,
        token_endpoint: str
    ):

        super().__init__()

        self.provider = provider

        self.client_id = client_id

        self.client_secret = client_secret

        self.redirect_uri = redirect_uri

        self.auth_endpoint = auth_endpoint

        self.token_endpoint = token_endpoint

        self.state = secrets.token_urlsafe(24)

        self.manager = AuthenticationManager()

    # ------------------------------------------------------

    def authorization_url(self) -> str:

        params = {

            "client_id": self.client_id,

            "redirect_uri": self.redirect_uri,

            "response_type": "code",

            "state": self.state

        }

        return (
            self.auth_endpoint
            + "?"
            + urllib.parse.urlencode(params)
        )

    # ------------------------------------------------------

    def login(self) -> bool:

        url = self.authorization_url()

        webbrowser.open(url)

        return True

    # ------------------------------------------------------

    def exchange_code(
        self,
        code: str
    ) -> bool:

        """
        This method exchanges the authorization
        code for an access token.

        Broker-specific implementations should
        override this method to perform the actual
        HTTP request to the token endpoint.
        """

        raise NotImplementedError(
            "exchange_code() must be implemented "
            "by the broker-specific provider."
        )

    # ------------------------------------------------------

    def refresh(self) -> bool:

        """
        Default implementation.

        Override if the broker supports token
        renewal.
        """

        return False

    # ------------------------------------------------------

    def logout(self):

        self.authenticated = False

        self.token = None

        self.manager.remove_token(
            self.provider
        )

    # ------------------------------------------------------

    def authenticated_session(self) -> bool:

        token = self.manager.get_token(
            self.provider
        )

        if token is None:

            return False

        if token.is_expired():

            return False

        self.token = token

        self.authenticated = True

        return True

    # ------------------------------------------------------

    def save_token(

        self,

        access_token: str,

        refresh_token: str = "",

        expires_in: Optional[int] = None,

        user_id: str = ""

    ) -> None:

        expires_at = None

        if expires_in:

            expires_at = (
                datetime.now()
                + timedelta(seconds=expires_in)
            )

        token = AuthToken(

            provider=self.provider,

            access_token=access_token,

            refresh_token=refresh_token,

            expires_at=expires_at,

            client_id=self.client_id,

            user_id=user_id

        )

        self.manager.set_token(token)

        self.token = token

        self.authenticated = True


# ==========================================================
# Broker Configuration
# ==========================================================

@dataclass(slots=True)
class BrokerConfig:

    provider: str

    client_id: str

    client_secret: str

    redirect_uri: str

    auth_endpoint: str

    token_endpoint: str


# ==========================================================
# Upstox Authentication
# ==========================================================

class UpstoxAuthentication(OAuthAuthentication):

    """
    Upstox OAuth Authentication.

    The actual authorization-code exchange should be
    implemented using the current Upstox REST API.

    This class intentionally keeps the framework
    independent from HTTP libraries.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):

        super().__init__(
            provider="upstox",
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            auth_endpoint="https://api.upstox.com/v2/login/authorization/dialog",
            token_endpoint="https://api.upstox.com/v2/login/authorization/token"
        )

    def exchange_code(
        self,
        code: str
    ) -> bool:

        """
        Exchange Upstox authorization code for
        an access token and persist the token.
        """

        if not code:
            return False

        try:

            headers = {
                "accept": "application/json",
                "Content-Type":
                    "application/x-www-form-urlencoded",
            }

            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            }

            response = requests.post(
                self.token_endpoint,
                headers=headers,
                data=data,
                timeout=30,
            )

            if response.status_code != 200:

                logging.getLogger(
                    __name__
                ).error(
                    "Upstox token exchange failed. "
                    "HTTP %s: %s",
                    response.status_code,
                    response.text,
                )

                return False

            payload = response.json()

            access_token = payload.get(
                "access_token"
            )

            if not access_token:

                logging.getLogger(
                    __name__
                ).error(
                    "Upstox response did not contain "
                    "an access_token."
                )

                return False

            self.save_token(
                access_token=access_token,
                refresh_token="",
                user_id=str(
                    payload.get(
                        "user_id",
                        payload.get(
                            "user_name",
                            "",
                        ),
                    )
                ),
            )

            logging.getLogger(
                __name__
            ).info(
                "Upstox authentication successful."
            )

            return True

        except requests.RequestException:

            logging.getLogger(
                __name__
            ).exception(
                "Upstox token request failed."
            )

            return False

        except Exception:

            logging.getLogger(
                __name__
            ).exception(
                "Unable to exchange Upstox "
                "authorization code."
            )

            return False


# ==========================================================
# Shoonya Authentication
# ==========================================================

class ShoonyaAuthentication(AuthenticationProvider):

    """
    Shoonya uses a different authentication mechanism
    than OAuth.

    Broker-specific login will be implemented inside
    shoonya_provider.py.
    """

    def login(self) -> bool:
        raise NotImplementedError

    def logout(self):
        raise NotImplementedError

    def refresh(self) -> bool:
        return False

    def authorization_url(self) -> str:
        return ""

    def exchange_code(
        self,
        code: str
    ) -> bool:
        return False


# ==========================================================
# Authentication Factory
# ==========================================================

class AuthenticationFactory:

    @staticmethod
    def create(
        config: BrokerConfig
    ) -> AuthenticationProvider:

        provider = config.provider.lower()

        if provider == "upstox":

            return UpstoxAuthentication(

                client_id=config.client_id,

                client_secret=config.client_secret,

                redirect_uri=config.redirect_uri

            )

        if provider == "shoonya":

            return ShoonyaAuthentication()

        raise ValueError(
            f"Unsupported provider: {config.provider}"
        )


# ==========================================================
# Helpers
# ==========================================================

def generate_state() -> str:
    return secrets.token_urlsafe(32)


def authenticated(
    provider: AuthenticationProvider
) -> bool:

    return getattr(
        provider,
        "authenticated",
        False
    )


# ==========================================================
# Module Metadata
# ==========================================================

__version__ = "4.0"

__all__ = [

    "AuthToken",

    "BrokerConfig",

    "AuthenticationProvider",

    "OAuthAuthentication",

    "AuthenticationManager",

    "UpstoxAuthentication",

    "ShoonyaAuthentication",

    "AuthenticationFactory",

    "generate_state",

    "authenticated"
]
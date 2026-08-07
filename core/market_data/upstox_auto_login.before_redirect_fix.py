"""
==========================================================
StockVersity Scanner Pro
Upstox Background Auto Login
==========================================================

Purpose
-------
Automatically obtain a valid Upstox access token without
opening a visible browser window.

Flow
----
1. Load credentials from .env
2. Check existing cached Upstox token
3. Validate cached token against Upstox
4. If invalid:
       - launch Chromium headlessly
       - open Upstox OAuth authorization URL
       - enter mobile number
       - generate TOTP
       - enter TOTP
       - enter PIN
       - capture redirect authorization code
5. Exchange authorization code using the existing
   UpstoxAuthentication class
6. Return the saved access token

IMPORTANT
---------
This module contains NO GUI code.

It must never manipulate PySide6 widgets directly.
==========================================================
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pyotp
import requests
from dotenv import load_dotenv
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from core.market_data.authentication import (
    AuthenticationManager,
    UpstoxAuthentication,
)


logger = logging.getLogger(__name__)


# ==========================================================
# PROJECT / ENVIRONMENT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

UPSTOX_API_KEY = os.getenv(
    "UPSTOX_API_KEY",
    "",
).strip()

UPSTOX_API_SECRET = os.getenv(
    "UPSTOX_API_SECRET",
    "",
).strip()

UPSTOX_REDIRECT_URI = os.getenv(
    "UPSTOX_REDIRECT_URI",
    "",
).strip()

UPSTOX_MOBILE_NO = os.getenv(
    "UPSTOX_MOBILE_NO",
    "",
).strip()

UPSTOX_TOTP_KEY = os.getenv(
    "UPSTOX_TOTP_KEY",
    "",
).replace(" ", "").strip()

UPSTOX_PIN = os.getenv(
    "UPSTOX_PIN",
    "",
).strip()


PROFILE_URL = (
    "https://api.upstox.com/v2/user/profile"
)

PROVIDER_NAME = "upstox"

LOGIN_TIMEOUT_MS = 45_000

REDIRECT_TIMEOUT_MS = 60_000


# ==========================================================
# EXCEPTION
# ==========================================================

class UpstoxAutoLoginError(RuntimeError):
    """Raised when automatic Upstox authentication fails."""


# ==========================================================
# AUTO LOGIN SERVICE
# ==========================================================

class UpstoxAutoLogin:
    """
    Headless Upstox authentication service.

    This service deliberately reuses StockVersity's existing
    AuthenticationManager and UpstoxAuthentication classes.
    """

    def __init__(self) -> None:

        self._validate_configuration()

        self.auth = UpstoxAuthentication(
            client_id=UPSTOX_API_KEY,
            client_secret=UPSTOX_API_SECRET,
            redirect_uri=UPSTOX_REDIRECT_URI,
        )

        # UpstoxAuthentication already creates its own
        # AuthenticationManager. Reuse that manager so there
        # is only one token-storage path.
        self.manager: AuthenticationManager = (
            self.auth.manager
        )

    # ======================================================
    # PUBLIC API
    # ======================================================

    async def get_access_token(
        self,
        force_login: bool = False,
    ) -> str:
        """
        Return a working Upstox access token.

        Existing cached token is preferred.

        A new background/headless login is performed only
        when the saved token is missing or rejected.
        """

        if not force_login:

            cached_token = (
                self._get_cached_access_token()
            )

            if cached_token:

                logger.info(
                    "Found saved Upstox access token. "
                    "Validating..."
                )

                if self._validate_access_token(
                    cached_token
                ):

                    logger.info(
                        "Saved Upstox token is valid."
                    )

                    return cached_token

                logger.warning(
                    "Saved Upstox token is invalid. "
                    "Starting background login."
                )

                self.manager.remove_token(
                    PROVIDER_NAME
                )

        logger.info(
            "Starting Upstox headless authentication."
        )

        authorization_code = (
            await self._generate_authorization_code()
        )

        if not authorization_code:

            raise UpstoxAutoLoginError(
                "Upstox did not return an "
                "authorization code."
            )

        logger.info(
            "Upstox authorization code received."
        )

        success = self.auth.exchange_code(
            authorization_code
        )

        if not success:

            raise UpstoxAutoLoginError(
                "Unable to exchange Upstox "
                "authorization code for access token."
            )

        token = self._get_cached_access_token()

        if not token:

            raise UpstoxAutoLoginError(
                "Upstox authentication succeeded but "
                "no access token was saved."
            )

        if not self._validate_access_token(
            token
        ):

            self.manager.remove_token(
                PROVIDER_NAME
            )

            raise UpstoxAutoLoginError(
                "Upstox returned an access token, "
                "but token validation failed."
            )

        logger.info(
            "Upstox background authentication "
            "completed successfully."
        )

        return token

    # ======================================================
    # CACHED TOKEN
    # ======================================================

    def _get_cached_access_token(
        self,
    ) -> Optional[str]:

        token = self.manager.get_token(
            PROVIDER_NAME
        )

        if token is None:
            return None

        access_token = getattr(
            token,
            "access_token",
            "",
        )

        if not access_token:
            return None

        return str(
            access_token
        ).strip()

    # ======================================================
    # REAL TOKEN VALIDATION
    # ======================================================

    @staticmethod
    def _validate_access_token(
        access_token: str,
    ) -> bool:
        """
        Validate token against Upstox itself.

        This is intentionally stronger than only checking
        local expiry metadata.
        """

        if not access_token:
            return False

        try:

            response = requests.get(
                PROFILE_URL,
                headers={
                    "Accept":
                        "application/json",

                    "Authorization":
                        f"Bearer {access_token}",
                },
                timeout=15,
            )

            if response.status_code == 200:
                return True

            logger.warning(
                "Upstox token validation returned "
                "HTTP %s.",
                response.status_code,
            )

            return False

        except requests.RequestException:

            logger.exception(
                "Unable to validate Upstox token."
            )

            return False

    # ======================================================
    # HEADLESS AUTHORIZATION
    # ======================================================

    async def _generate_authorization_code(
        self,
    ) -> str:

        authorization_url = (
            self.auth.authorization_url()
        )

        logger.info(
            "Launching headless Chromium for "
            "Upstox authorization."
        )

        async with async_playwright() as playwright:

            browser: Optional[Browser] = None

            context: Optional[
                BrowserContext
            ] = None

            try:

                browser = (
                    await playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-gpu",
                            "--disable-dev-shm-usage",
                        ],
                    )
                )

                context = (
                    await browser.new_context()
                )

                page = await context.new_page()

                page.set_default_timeout(
                    LOGIN_TIMEOUT_MS
                )

                await page.goto(
                    authorization_url,
                    wait_until="domcontentloaded",
                )

                await self._perform_login(
                    page
                )

                code = await self._wait_for_code(
                    page
                )

                return code

            except PlaywrightTimeoutError as exc:

                raise UpstoxAutoLoginError(
                    "Timed out while completing "
                    "Upstox background login."
                ) from exc

            except UpstoxAutoLoginError:
                raise

            except Exception as exc:

                logger.exception(
                    "Unexpected Upstox headless "
                    "login error."
                )

                raise UpstoxAutoLoginError(
                    "Unexpected error during "
                    "Upstox background login."
                ) from exc

            finally:

                if context is not None:

                    try:
                        await context.close()
                    except Exception:
                        pass

                if browser is not None:

                    try:
                        await browser.close()
                    except Exception:
                        pass

    # ======================================================
    # LOGIN FORM
    # ======================================================

    async def _perform_login(
        self,
        page: Page,
    ) -> None:
        """
        Complete the Upstox login form.

        Selectors are intentionally kept in this isolated
        method so future Upstox UI changes can be handled
        without changing the token/storage architecture.
        """

        # --------------------------------------------------
        # MOBILE NUMBER
        # --------------------------------------------------

        mobile = page.locator(
            "#mobileNum"
        )

        await mobile.wait_for(
            state="visible"
        )

        await mobile.fill(
            UPSTOX_MOBILE_NO
        )

        await page.get_by_role(
            "button",
            name="Get OTP",
        ).click()

        # --------------------------------------------------
        # TOTP
        # --------------------------------------------------

        otp_input = page.locator(
            "#otpNum"
        )

        await otp_input.wait_for(
            state="visible"
        )

        otp = pyotp.TOTP(
            UPSTOX_TOTP_KEY
        ).now()

        await otp_input.fill(
            otp
        )

        await page.get_by_role(
            "button",
            name="Continue",
        ).click()

        # --------------------------------------------------
        # PIN
        # --------------------------------------------------

        pin_input = page.get_by_label(
            "Enter 6-digit PIN"
        )

        await pin_input.wait_for(
            state="visible"
        )

        await pin_input.fill(
            UPSTOX_PIN
        )

        await page.get_by_role(
            "button",
            name="Continue",
        ).click()

    # ======================================================
    # REDIRECT / AUTHORIZATION CODE
    # ======================================================

    async def _wait_for_code(
        self,
        page: Page,
    ) -> str:

        loop = asyncio.get_running_loop()

        deadline = (
            loop.time()
            + (
                REDIRECT_TIMEOUT_MS
                / 1000
            )
        )

        while loop.time() < deadline:

            current_url = page.url

            code = self._extract_code(
                current_url
            )

            if code:
                return code

            await page.wait_for_timeout(
                250
            )

        raise UpstoxAutoLoginError(
            "Upstox redirect was received without "
            "an authorization code, or redirect "
            "timed out."
        )

    # ======================================================
    # URL PARSER
    # ======================================================

    @staticmethod
    def _extract_code(
        url: str,
    ) -> str:

        if not url:
            return ""

        try:

            parsed = urlparse(
                url
            )

            query = parse_qs(
                parsed.query
            )

            values = query.get(
                "code",
                []
            )

            if not values:
                return ""

            return str(
                values[0]
            ).strip()

        except Exception:

            return ""

    # ======================================================
    # CONFIG VALIDATION
    # ======================================================

    @staticmethod
    def _validate_configuration(
    ) -> None:

        required = {
            "UPSTOX_API_KEY":
                UPSTOX_API_KEY,

            "UPSTOX_API_SECRET":
                UPSTOX_API_SECRET,

            "UPSTOX_REDIRECT_URI":
                UPSTOX_REDIRECT_URI,

            "UPSTOX_MOBILE_NO":
                UPSTOX_MOBILE_NO,

            "UPSTOX_TOTP_KEY":
                UPSTOX_TOTP_KEY,

            "UPSTOX_PIN":
                UPSTOX_PIN,
        }

        missing = [
            name
            for name, value
            in required.items()
            if not value
        ]

        if missing:

            raise UpstoxAutoLoginError(
                "Missing Upstox environment "
                "configuration: "
                + ", ".join(missing)
            )


# ==========================================================
# CONVENIENCE FUNCTIONS
# ==========================================================

async def get_upstox_access_token(
    force_login: bool = False,
) -> str:
    """
    Async entry point for StockVersity services.
    """

    service = UpstoxAutoLogin()

    return await service.get_access_token(
        force_login=force_login
    )


def get_upstox_access_token_sync(
    force_login: bool = False,
) -> str:
    """
    Synchronous entry point.

    Do NOT call this from the Qt GUI thread during normal
    application startup. StockVersity will ultimately call
    the async service from its background worker.
    """

    return asyncio.run(
        get_upstox_access_token(
            force_login=force_login
        )
    )


# ==========================================================
# DIRECT BACKEND TEST
# ==========================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    try:

        access_token = (
            get_upstox_access_token_sync()
        )

        print(
            "[UPSTOX AUTO LOGIN] SUCCESS"
        )

        print(
            "[UPSTOX AUTO LOGIN] "
            "Token obtained and validated."
        )

        # SECURITY:
        # Never print the actual token.

        print(
            "[UPSTOX AUTO LOGIN] "
            f"Token length: {len(access_token)}"
        )

    except Exception as exc:

        logger.exception(
            "Upstox automatic login failed."
        )

        print(
            "[UPSTOX AUTO LOGIN] FAILED:"
        )

        print(
            str(exc)
        )
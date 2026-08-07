"""
==========================================================
StockVersity Scanner Pro
Upstox Background Auto Login
==========================================================

Backend-only Upstox authentication.

Flow
----
1. Load credentials from .env
2. Check saved Upstox token
3. Validate saved token against Upstox
4. If invalid/missing:
       Headless Chromium
       -> Mobile
       -> TOTP
       -> PIN
       -> Capture OAuth authorization code
5. Exchange authorization code using the existing
   UpstoxAuthentication class
6. Existing AuthenticationManager persists the token
7. Return validated access token

No browser window is shown.
No PySide6/UI code belongs in this module.
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
# ENVIRONMENT
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


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


PROVIDER_NAME = "upstox"

PROFILE_URL = (
    "https://api.upstox.com/v2/user/profile"
)

LOGIN_TIMEOUT_MS = 45_000

AUTH_CODE_TIMEOUT_SECONDS = 45


# ==========================================================
# ERROR
# ==========================================================

class UpstoxAutoLoginError(RuntimeError):
    """StockVersity Upstox auto-login failure."""


# ==========================================================
# SERVICE
# ==========================================================

class UpstoxAutoLogin:

    def __init__(self) -> None:

        self._validate_configuration()

        self.auth = UpstoxAuthentication(
            client_id=UPSTOX_API_KEY,
            client_secret=UPSTOX_API_SECRET,
            redirect_uri=UPSTOX_REDIRECT_URI,
        )

        self.manager: AuthenticationManager = (
            self.auth.manager
        )

    # ======================================================
    # MAIN ENTRY
    # ======================================================

    async def get_access_token(
        self,
        force_login: bool = False,
    ) -> str:

        # --------------------------------------------------
        # EXISTING TOKEN
        # --------------------------------------------------

        if not force_login:

            cached_token = (
                self._get_cached_access_token()
            )

            if cached_token:

                logger.info(
                    "Saved Upstox token found. "
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
                    "Saved Upstox token is invalid."
                )

                try:

                    self.manager.remove_token(
                        PROVIDER_NAME
                    )

                except Exception:

                    logger.exception(
                        "Unable to remove invalid "
                        "Upstox token."
                    )

        # --------------------------------------------------
        # BACKGROUND LOGIN
        # --------------------------------------------------

        logger.info(
            "Starting Upstox background authentication."
        )

        code = await self._generate_authorization_code()

        if not code:

            raise UpstoxAutoLoginError(
                "Authorization code was not captured."
            )

        logger.info(
            "Upstox authorization code captured."
        )

        # --------------------------------------------------
        # CODE -> ACCESS TOKEN
        # --------------------------------------------------

        success = self.auth.exchange_code(
            code
        )

        if not success:

            raise UpstoxAutoLoginError(
                "Upstox authorization-code exchange failed."
            )

        access_token = (
            self._get_cached_access_token()
        )

        if not access_token:

            raise UpstoxAutoLoginError(
                "Token exchange succeeded but "
                "AuthenticationManager contains "
                "no Upstox access token."
            )

        # --------------------------------------------------
        # FINAL VALIDATION
        # --------------------------------------------------

        logger.info(
            "Validating new Upstox access token."
        )

        if not self._validate_access_token(
            access_token
        ):

            try:

                self.manager.remove_token(
                    PROVIDER_NAME
                )

            except Exception:
                pass

            raise UpstoxAutoLoginError(
                "New Upstox access token failed "
                "profile validation."
            )

        logger.info(
            "Upstox authentication completed successfully."
        )

        return access_token

    # ======================================================
    # TOKEN STORAGE
    # ======================================================

    def _get_cached_access_token(
        self,
    ) -> Optional[str]:

        try:

            token = self.manager.get_token(
                PROVIDER_NAME
            )

        except Exception:

            logger.exception(
                "Unable to read saved Upstox token."
            )

            return None

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
    # TOKEN VALIDATION
    # ======================================================

    @staticmethod
    def _validate_access_token(
        access_token: str,
    ) -> bool:

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

                logger.info(
                    "Upstox profile validation: HTTP 200."
                )

                return True

            logger.warning(
                "Upstox profile validation failed: "
                "HTTP %s.",
                response.status_code,
            )

            return False

        except requests.RequestException:

            logger.exception(
                "Upstox profile validation "
                "request failed."
            )

            return False

    # ======================================================
    # HEADLESS OAUTH
    # ======================================================

    async def _generate_authorization_code(
        self,
    ) -> str:

        authorization_url = (
            self.auth.authorization_url()
        )

        logger.info(
            "Launching headless Chromium."
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
                    await browser.new_context(
                        ignore_https_errors=True
                    )
                )

                page = await context.new_page()

                page.set_default_timeout(
                    LOGIN_TIMEOUT_MS
                )

                # ------------------------------------------
                # AUTHORIZATION CODE FUTURE
                # ------------------------------------------

                loop = asyncio.get_running_loop()

                code_future = loop.create_future()

                redirect_base = (
                    UPSTOX_REDIRECT_URI.rstrip("/")
                )

                # ------------------------------------------
                # REQUEST WATCHER
                #
                # IMPORTANT:
                # Chromium may fail to actually connect to
                # https://127.0.0.1:5000/.
                #
                # We therefore capture ?code= from the
                # outgoing request BEFORE the connection
                # failure occurs.
                # ------------------------------------------

                def request_handler(request):

                    if code_future.done():
                        return

                    try:

                        request_url = request.url

                        parsed = urlparse(
                            request_url
                        )

                        callback_url = (
                            f"{parsed.scheme}://"
                            f"{parsed.netloc}"
                            f"{parsed.path}"
                        ).rstrip("/")

                        if (
                            callback_url
                            != redirect_base
                        ):
                            return

                        query = parse_qs(
                            parsed.query
                        )

                        code_values = query.get(
                            "code",
                            [],
                        )

                        if code_values:

                            code = str(
                                code_values[0]
                            ).strip()

                            if code:

                                logger.info(
                                    "OAuth callback request "
                                    "detected."
                                )

                                code_future.set_result(
                                    code
                                )

                                return

                        error_values = query.get(
                            "error",
                            [],
                        )

                        if error_values:

                            error_text = str(
                                error_values[0]
                            )

                            code_future.set_exception(
                                UpstoxAutoLoginError(
                                    "Upstox OAuth returned: "
                                    + error_text
                                )
                            )

                    except Exception:

                        logger.exception(
                            "Unable to inspect OAuth "
                            "callback request."
                        )

                page.on(
                    "request",
                    request_handler,
                )

                # ------------------------------------------
                # OPEN AUTHORIZATION PAGE
                # ------------------------------------------

                logger.info(
                    "Opening Upstox authorization page."
                )

                await page.goto(
                    authorization_url,
                    wait_until="domcontentloaded",
                )

                # ------------------------------------------
                # LOGIN
                # ------------------------------------------

                await self._perform_login(
                    page
                )

                # ------------------------------------------
                # WAIT FOR CALLBACK CODE
                # ------------------------------------------

                try:

                    code = await asyncio.wait_for(
                        code_future,
                        timeout=(
                            AUTH_CODE_TIMEOUT_SECONDS
                        ),
                    )

                except asyncio.TimeoutError as exc:

                    raise UpstoxAutoLoginError(
                        "Timed out waiting for Upstox "
                        "OAuth authorization code."
                    ) from exc

                if not code:

                    raise UpstoxAutoLoginError(
                        "Empty Upstox authorization code."
                    )

                return str(code).strip()

            except PlaywrightTimeoutError as exc:

                raise UpstoxAutoLoginError(
                    "Timed out while completing "
                    "Upstox login."
                ) from exc

            except UpstoxAutoLoginError:
                raise

            except Exception as exc:

                logger.exception(
                    "Unexpected Upstox auto-login error."
                )

                raise UpstoxAutoLoginError(
                    "Unexpected Upstox auto-login failure."
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
    # UPSTOX LOGIN
    # ======================================================

    async def _perform_login(
        self,
        page: Page,
    ) -> None:

        # --------------------------------------------------
        # MOBILE
        # --------------------------------------------------

        logger.info(
            "Submitting Upstox mobile number."
        )

        mobile_input = page.locator(
            "#mobileNum"
        )

        await mobile_input.wait_for(
            state="visible"
        )

        await mobile_input.fill(
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

        if not otp:

            raise UpstoxAutoLoginError(
                "Unable to generate Upstox TOTP."
            )

        logger.info(
            "Submitting generated TOTP."
        )

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

        logger.info(
            "Submitting Upstox PIN."
        )

        await pin_input.fill(
            UPSTOX_PIN
        )

        await page.get_by_role(
            "button",
            name="Continue",
        ).click()

    # ======================================================
    # CONFIG VALIDATION
    # ======================================================

    @staticmethod
    def _validate_configuration() -> None:

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
                "Missing Upstox configuration: "
                + ", ".join(missing)
            )

        if not (
            UPSTOX_REDIRECT_URI.startswith(
                "https://"
            )
        ):

            logger.warning(
                "UPSTOX_REDIRECT_URI does not use HTTPS."
            )


# ==========================================================
# PUBLIC HELPERS
# ==========================================================

async def get_upstox_access_token(
    force_login: bool = False,
) -> str:

    service = UpstoxAutoLogin()

    return await service.get_access_token(
        force_login=force_login
    )


def get_upstox_access_token_sync(
    force_login: bool = False,
) -> str:

    return asyncio.run(
        get_upstox_access_token(
            force_login=force_login
        )
    )


# ==========================================================
# BACKEND TEST
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

        token = (
            get_upstox_access_token_sync()
        )

        print()
        print(
            "======================================"
        )
        print(
            "UPSTOX AUTO LOGIN: SUCCESS"
        )
        print(
            "TOKEN VALIDATION: SUCCESS"
        )
        print(
            "======================================"
        )

        # Never display the actual token.
        print(
            "Access token length:",
            len(token),
        )

    except Exception as exc:

        print()
        print(
            "======================================"
        )
        print(
            "UPSTOX AUTO LOGIN: FAILED"
        )
        print(
            "======================================"
        )
        print(
            str(exc)
        )

        logger.exception(
            "Upstox automatic login failed."
        )
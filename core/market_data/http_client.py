"""
==========================================================
StockVersity Scanner Pro
HTTP Client
Version : 4.0
==========================================================

Universal HTTP client used by all brokers.

Supports

✓ Upstox
✓ Shoonya
✓ Future Brokers

Features

✓ Connection Pooling
✓ Retry
✓ Timeout
✓ Automatic JSON
✓ Logging
✓ Error Handling
✓ Session Reuse

"""

from __future__ import annotations

import json
import logging
import time

from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================================
# Logger
# ==========================================================

logger = logging.getLogger(__name__)


# ==========================================================
# Configuration
# ==========================================================

DEFAULT_TIMEOUT = 15

DEFAULT_RETRIES = 3

DEFAULT_BACKOFF = 0.5


# ==========================================================
# Response
# ==========================================================

@dataclass(slots=True)
class HttpResponse:

    success: bool

    status_code: int

    data: Any = None

    headers: Optional[Dict] = None

    error: str = ""

    elapsed: float = 0.0


# ==========================================================
# HTTP Client
# ==========================================================

class HttpClient:

    """
    Shared HTTP client.

    Every REST API request in StockVersity
    goes through this client.
    """

    def __init__(

        self,

        timeout: int = DEFAULT_TIMEOUT,

        retries: int = DEFAULT_RETRIES,

        backoff: float = DEFAULT_BACKOFF

    ):

        self.timeout = timeout

        self.retries = retries

        self.backoff = backoff

        self.session = requests.Session()

        retry_strategy = Retry(

            total=retries,

            connect=retries,

            read=retries,

            backoff_factor=backoff,

            status_forcelist=[

                429,

                500,

                502,

                503,

                504

            ],

            allowed_methods=[

                "GET",

                "POST",

                "PUT",

                "DELETE"

            ]

        )

        adapter = HTTPAdapter(

            max_retries=retry_strategy,

            pool_connections=20,

            pool_maxsize=20

        )

        self.session.mount(
            "https://",
            adapter
        )

        self.session.mount(
            "http://",
            adapter
        )

        self.default_headers = {

            "Accept": "application/json",

            "Content-Type": "application/json",

            "User-Agent": "StockVersityScanner/4.0"

        }
            # ==========================================================
    # Headers
    # ==========================================================

    def set_header(
        self,
        key: str,
        value: str
    ) -> None:

        self.default_headers[key] = value

    def remove_header(
        self,
        key: str
    ) -> None:

        self.default_headers.pop(key, None)

    def set_access_token(
        self,
        token: str
    ) -> None:

        self.default_headers[
            "Authorization"
        ] = f"Bearer {token}"

    def clear_access_token(self) -> None:

        self.remove_header("Authorization")

    # ==========================================================
    # GET
    # ==========================================================

    def get(

        self,

        url: str,

        params: Optional[Dict] = None,

        headers: Optional[Dict] = None

    ) -> HttpResponse:

        request_headers = self.default_headers.copy()

        if headers:

            request_headers.update(headers)

        start = time.perf_counter()

        try:

            response = self.session.get(

                url,

                params=params,

                headers=request_headers,

                timeout=self.timeout

            )

            elapsed = time.perf_counter() - start

            return self._build_response(
                response,
                elapsed
            )

        except Exception as exc:

            return HttpResponse(

                success=False,

                status_code=0,

                error=str(exc)

            )

    # ==========================================================
    # POST
    # ==========================================================

    def post(

        self,

        url: str,

        json_data: Optional[Dict] = None,

        form_data: Optional[Dict] = None,

        headers: Optional[Dict] = None

    ) -> HttpResponse:

        request_headers = self.default_headers.copy()

        if headers:

            request_headers.update(headers)

        start = time.perf_counter()

        try:

            response = self.session.post(

                url,

                json=json_data,

                data=form_data,

                headers=request_headers,

                timeout=self.timeout

            )

            elapsed = time.perf_counter() - start

            return self._build_response(
                response,
                elapsed
            )

        except Exception as exc:

            return HttpResponse(

                success=False,

                status_code=0,

                error=str(exc)

            )

    # ==========================================================
    # PUT
    # ==========================================================

    def put(

        self,

        url: str,

        json_data: Optional[Dict] = None,

        headers: Optional[Dict] = None

    ) -> HttpResponse:

        request_headers = self.default_headers.copy()

        if headers:

            request_headers.update(headers)

        start = time.perf_counter()

        try:

            response = self.session.put(

                url,

                json=json_data,

                headers=request_headers,

                timeout=self.timeout

            )

            elapsed = time.perf_counter() - start

            return self._build_response(
                response,
                elapsed
            )

        except Exception as exc:

            return HttpResponse(

                success=False,

                status_code=0,

                error=str(exc)

            )

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(

        self,

        url: str,

        headers: Optional[Dict] = None

    ) -> HttpResponse:

        request_headers = self.default_headers.copy()

        if headers:

            request_headers.update(headers)

        start = time.perf_counter()

        try:

            response = self.session.delete(

                url,

                headers=request_headers,

                timeout=self.timeout

            )

            elapsed = time.perf_counter() - start

            return self._build_response(
                response,
                elapsed

            )

        except Exception as exc:

            return HttpResponse(

                success=False,

                status_code=0,

                error=str(exc)

            )
            # ==========================================================
    # Response Builder
    # ==========================================================

    def _build_response(
        self,
        response: requests.Response,
        elapsed: float
    ) -> HttpResponse:

        data = None

        try:
            data = response.json()

        except ValueError:

            data = response.text

        success = 200 <= response.status_code < 300

        error = ""

        if not success:

            error = self._extract_error(data)

            logger.error(
                "[HTTP %s] %s",
                response.status_code,
                error
            )

        return HttpResponse(

            success=success,

            status_code=response.status_code,

            data=data,

            headers=dict(response.headers),

            error=error,

            elapsed=elapsed

        )

    # ==========================================================
    # Error Extraction
    # ==========================================================

    @staticmethod
    def _extract_error(data: Any) -> str:

        if isinstance(data, dict):

            for key in (
                "message",
                "error",
                "errors",
                "description",
                "detail"
            ):

                if key in data:

                    return str(data[key])

        return str(data)

    # ==========================================================
    # Utilities
    # ==========================================================

    @staticmethod
    def is_rate_limited(
        response: HttpResponse
    ) -> bool:

        return response.status_code == 429

    @staticmethod
    def is_success(
        response: HttpResponse
    ) -> bool:

        return response.success

    @staticmethod
    def latency_ms(
        response: HttpResponse
    ) -> float:

        return round(response.elapsed * 1000, 2)

    # ==========================================================
    # Session Management
    # ==========================================================

    def close(self):

        self.session.close()

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):

        self.close()


# ==========================================================
# Singleton
# ==========================================================

_http_client = HttpClient()


def get_http_client() -> HttpClient:

    return _http_client


# ==========================================================
# Module Metadata
# ==========================================================

__version__ = "4.0"

__all__ = [

    "HttpClient",

    "HttpResponse",

    "get_http_client"

]
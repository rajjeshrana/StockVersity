import asyncio
import os
from urllib.parse import urlparse, parse_qs

import pyotp
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from core.market_data.authentication import UpstoxAuthentication


load_dotenv(override=True)


async def main():

    api_key = os.getenv("UPSTOX_API_KEY", "").strip()
    api_secret = os.getenv("UPSTOX_API_SECRET", "").strip()
    redirect_uri = os.getenv("UPSTOX_REDIRECT_URI", "").strip()
    mobile = os.getenv("UPSTOX_MOBILE_NO", "").strip()
    totp_key = os.getenv(
        "UPSTOX_TOTP_KEY", ""
    ).replace(" ", "").strip()
    pin = os.getenv("UPSTOX_PIN", "").strip()

    auth = UpstoxAuthentication(
        client_id=api_key,
        client_secret=api_secret,
        redirect_uri=redirect_uri,
    )

    print("Starting deep redirect diagnostic...")
    print("Registered redirect:", redirect_uri)

    captured_code = None

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            ignore_https_errors=True
        )

        page = await context.new_page()

        # ==================================================
        # RESPONSE WATCHER
        # ==================================================

        async def inspect_response(response):

            nonlocal captured_code

            try:

                url = response.url
                status = response.status

                # Only show relevant Upstox / redirect traffic.
                if (
                    "upstox" not in url.lower()
                    and "127.0.0.1" not in url
                ):
                    return

                safe_url = url

                if "code=" in safe_url:

                    parsed = urlparse(safe_url)

                    query = parse_qs(parsed.query)

                    code = query.get(
                        "code",
                        [""],
                    )[0]

                    if code:

                        captured_code = code

                    safe_url = (
                        safe_url.split("code=")[0]
                        + "code=<HIDDEN>"
                    )

                print(
                    "RESPONSE:",
                    status,
                    safe_url,
                )

                # Check Location header.
                headers = await response.all_headers()

                location = headers.get(
                    "location",
                    "",
                )

                if location:

                    safe_location = location

                    if "code=" in location:

                        parsed = urlparse(location)

                        query = parse_qs(
                            parsed.query
                        )

                        code = query.get(
                            "code",
                            [""],
                        )[0]

                        if code:

                            captured_code = code

                        safe_location = (
                            location.split("code=")[0]
                            + "code=<HIDDEN>"
                        )

                    print(
                        "LOCATION:",
                        safe_location,
                    )

            except Exception:
                pass

        def response_handler(response):

            asyncio.create_task(
                inspect_response(response)
            )

        page.on(
            "response",
            response_handler,
        )

        # ==================================================
        # REQUEST WATCHER
        # ==================================================

        def request_handler(request):

            nonlocal captured_code

            try:

                url = request.url

                if (
                    "upstox" not in url.lower()
                    and "127.0.0.1" not in url
                ):
                    return

                safe_url = url

                if "code=" in url:

                    parsed = urlparse(url)

                    query = parse_qs(
                        parsed.query
                    )

                    code = query.get(
                        "code",
                        [""],
                    )[0]

                    if code:

                        captured_code = code

                    safe_url = (
                        url.split("code=")[0]
                        + "code=<HIDDEN>"
                    )

                print(
                    "REQUEST:",
                    request.method,
                    safe_url,
                )

            except Exception:
                pass

        page.on(
            "request",
            request_handler,
        )

        # ==================================================
        # NAVIGATION WATCHER
        # ==================================================

        def navigation_handler(frame):

            nonlocal captured_code

            try:

                url = frame.url

                safe_url = url

                if "code=" in url:

                    parsed = urlparse(url)

                    query = parse_qs(
                        parsed.query
                    )

                    code = query.get(
                        "code",
                        [""],
                    )[0]

                    if code:

                        captured_code = code

                    safe_url = (
                        url.split("code=")[0]
                        + "code=<HIDDEN>"
                    )

                print(
                    "NAVIGATION:",
                    safe_url,
                )

            except Exception:
                pass

        page.on(
            "framenavigated",
            navigation_handler,
        )

        # ==================================================
        # OPEN AUTHORIZATION
        # ==================================================

        print()
        print("Opening authorization page...")

        await page.goto(
            auth.authorization_url(),
            wait_until="domcontentloaded",
        )

        print(
            "Login page:",
            await page.title(),
        )

        # ==================================================
        # MOBILE
        # ==================================================

        await page.locator(
            "#mobileNum"
        ).fill(mobile)

        await page.get_by_role(
            "button",
            name="Get OTP",
        ).click()

        # ==================================================
        # TOTP
        # ==================================================

        await page.locator(
            "#otpNum"
        ).wait_for(
            state="visible"
        )

        otp = pyotp.TOTP(
            totp_key
        ).now()

        await page.locator(
            "#otpNum"
        ).fill(otp)

        await page.get_by_role(
            "button",
            name="Continue",
        ).click()

        # ==================================================
        # PIN
        # ==================================================

        pin_input = page.get_by_label(
            "Enter 6-digit PIN"
        )

        await pin_input.wait_for(
            state="visible"
        )

        await pin_input.fill(
            pin
        )

        print()
        print("Submitting PIN...")

        await page.get_by_role(
            "button",
            name="Continue",
        ).click()

        # ==================================================
        # OBSERVE TRAFFIC
        # ==================================================

        for second in range(20):

            await page.wait_for_timeout(
                1000
            )

            if captured_code:

                print()
                print("==============================")
                print("AUTHORIZATION CODE FOUND")
                print("==============================")
                print(
                    "Code length:",
                    len(captured_code),
                )
                print(
                    "Actual code NOT displayed."
                )

                break

            print(
                f"Waiting... {second + 1}s"
            )

        if not captured_code:

            print()
            print("==============================")
            print("CODE NOT FOUND")
            print("==============================")

            print(
                "Final browser URL:",
                page.url,
            )

        await context.close()

        await browser.close()


if __name__ == "__main__":

    asyncio.run(main())
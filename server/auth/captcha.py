"""reCAPTCHA v3 verification for web client auth requests."""

import asyncio
import json
import logging
import urllib.request
import urllib.parse
from functools import partial

logger = logging.getLogger(__name__)

# Replace this with your real reCAPTCHA v3 secret key before launch.
# When empty, CAPTCHA verification is skipped (graceful degradation).
RECAPTCHA_SECRET_KEY = ""

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
SCORE_THRESHOLD = 0.5
REQUEST_TIMEOUT_SECONDS = 5


def _verify_sync(secret: str, token: str, remote_ip: str) -> tuple[bool, str]:
    """Blocking HTTP POST to Google's siteverify endpoint.

    Returns (passed, reason) where reason is only set on failure.
    """
    data = urllib.parse.urlencode({
        "secret": secret,
        "response": token,
        "remoteip": remote_ip,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(VERIFY_URL, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.warning("reCAPTCHA verify request failed: %s", exc)
        # Network failure → allow the request through (don't lock out
        # legitimate users when Google is unreachable).
        return True, ""

    if not body.get("success", False):
        codes = body.get("error-codes", [])
        logger.info("reCAPTCHA verification failed: %s", codes)
        return False, "captcha_failed"

    score = body.get("score", 0.0)
    if score < SCORE_THRESHOLD:
        logger.info("reCAPTCHA score too low: %.2f (threshold %.2f)", score, SCORE_THRESHOLD)
        return False, "captcha_failed"

    return True, ""


async def verify_captcha(token: str, remote_ip: str) -> tuple[bool, str]:
    """Verify a reCAPTCHA v3 token asynchronously.

    Returns (passed, reason).
    - If RECAPTCHA_SECRET_KEY is empty, verification is skipped (always passes).
    - If the Google API is unreachable, the request is allowed through.
    """
    if not RECAPTCHA_SECRET_KEY:
        return True, ""

    if not token:
        return False, "captcha_missing"

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(_verify_sync, RECAPTCHA_SECRET_KEY, token, remote_ip),
    )

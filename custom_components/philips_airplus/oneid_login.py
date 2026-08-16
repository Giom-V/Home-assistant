"""Email + OTP login for the Philips HomeID / Gigya backend.

Live-verified against a real account (2026-07-02): no OAuth/PKCE dance is
needed. Two stateless calls are enough:

    POST accounts.auth.otp.email.sendCode  {email}        -> vToken
    POST accounts.auth.otp.email.login     {email, code, vToken}  -> UID

``UID`` from the second response *is* the gaoda/air-matters ``user_id`` that
``airmatters_auth.get_jwt`` needs (confirmed live: signing with this UID and
calling deviceList returned the account's real fans). The OIDC/PKCE token
exchange some reference integrations use (``/authorize`` -> ``/token`` ->
``/user/self/get-id``) is NOT needed for this and was live-tested to return a
*different*, wrong id (a Versuni-side UUID that gaoda's deviceList rejects
with zero devices) — so it is deliberately not implemented here.

No session/cookies need to be carried between the two calls — each is
self-contained given the vToken.
"""
from __future__ import annotations

import requests

GIGYA_API_URL = "https://cdc.accounts.home.id"
GIGYA_API_KEY = "4_JGZWlP8eQHpEqkvQElolbA"  # identifier, not a secret — see airmatters_auth.py docstring

_TIMEOUT = 30


class OneIdError(Exception):
    """Raised on any Gigya OTP error response."""


def request_otp(email: str) -> str:
    """Trigger the emailed code. Returns the vToken needed to verify it."""
    r = requests.post(
        f"{GIGYA_API_URL}/accounts.auth.otp.email.sendCode",
        data={"email": email, "apiKey": GIGYA_API_KEY, "format": "json"},
        timeout=_TIMEOUT,
    )
    data = r.json()
    if data.get("errorCode", -1) != 0:
        raise OneIdError(data.get("errorMessage", str(data)))
    vtoken = data.get("vToken")
    if not vtoken:
        raise OneIdError("No vToken in OTP response")
    return vtoken


def verify_otp(email: str, code: str, vtoken: str) -> str:
    """Verify the emailed code. Returns the gaoda ``user_id`` (Gigya ``UID``)."""
    r = requests.post(
        f"{GIGYA_API_URL}/accounts.auth.otp.email.login",
        data={
            "email": email, "code": code, "vToken": vtoken,
            "apiKey": GIGYA_API_KEY, "format": "json",
        },
        timeout=_TIMEOUT,
    )
    data = r.json()
    error_code = data.get("errorCode", -1)
    if error_code == 206001:
        raise OneIdError(
            "Account pending registration — sign in once in the official "
            "Philips app first, then retry."
        )
    if error_code != 0:
        raise OneIdError(data.get("errorMessage", str(data)))
    user_id = data.get("UID")
    if not user_id:
        raise OneIdError("No UID in OTP verify response")
    return user_id


if __name__ == "__main__":
    # ponytail: the gaoda user_id mapping itself was proven live in-session
    # (not regression-testable offline) — but the error-branch handling here
    # (206001 / generic errorCode / missing field) IS local logic that can
    # break silently, so it gets a mocked-response self-check.
    from unittest.mock import patch

    class _FakeResponse:
        def __init__(self, payload: dict) -> None:
            self._payload = payload

        def json(self) -> dict:
            return self._payload

    def _fake_post(_url, **_kw):
        return _FakeResponse(_fake_post.next_payload)

    with patch("requests.post", _fake_post):
        _fake_post.next_payload = {"errorCode": 0, "vToken": "vtok123"}
        assert request_otp("a@b.com") == "vtok123"

        _fake_post.next_payload = {"errorCode": 0, "UID": "deadbeef"}
        assert verify_otp("a@b.com", "123456", "vtok123") == "deadbeef"

        _fake_post.next_payload = {"errorCode": 206001}
        try:
            verify_otp("a@b.com", "123456", "vtok123")
            raise AssertionError("expected OneIdError for pending registration")
        except OneIdError as err:
            assert "official Philips app" in str(err)

        _fake_post.next_payload = {"errorCode": 400006, "errorMessage": "bad"}
        try:
            verify_otp("a@b.com", "000000", "vtok123")
            raise AssertionError("expected OneIdError for generic failure")
        except OneIdError:
            pass

        _fake_post.next_payload = {"errorCode": 0}  # missing UID
        try:
            verify_otp("a@b.com", "123456", "vtok123")
            raise AssertionError("expected OneIdError for missing UID")
        except OneIdError:
            pass

    print("oneid_login: self-check OK")

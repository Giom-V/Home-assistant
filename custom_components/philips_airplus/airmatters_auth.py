"""Philips Air+ (gaoda / air-matters) standalone auth client.

Reverse-engineered from com.philips.ph.homecare (Philips Air+ APK). Provides the
full autonomous token chain Home Assistant needs, with no app/frida/refresh_token
required for the periodic refresh — only the one-time ``user_id`` (from the
email+OTP config flow, see ``oneid_login.py``) and the ``mSecret`` (extracted
once from the user's own APK, see ``apk_extract.py``).

    user_id + app_id + mSecret  (app_id static; mSecret per-user from APK;
        |                        user_id per-user from email+OTP login)
        v   signed POST enduser/v2/getToken/   -> 7-day enduser JWT
        |
        v   GET  enduser/deviceList/          (Authorization: jwt <JWT>)  -> devices
        v   POST enduser/v2/mqttInfo/         (Authorization: jwt <JWT>)  -> 1h single-use
        |       body {"device_id":["<id>",...]}                              SigV4 WSS URLs
        v   MQTT-over-WSS  ->  AWS IoT device shadow (read + control)

The signing is ``sha256_HMAC(sha256_HMAC(bodyParams, mSecret), username)`` where
``bodyParams = "app_id=..&timestamp=..&username=<urlenc(username)>"`` and
``username = "PHILIPS:" + user_id``. Only getToken needs the Signature header;
deviceList/mqttInfo use a plain ``Authorization: jwt <JWT>``.

``app_id`` is a plain identifier (sent in the clear in every request body, same
risk class as the Gigya API key) so it's hardcoded here. ``mSecret`` is the
actual signing secret — it is never hardcoded or committed; it lives only in
each user's config entry, extracted locally from their own APK.

HTTP calls retry on the transient 503 the api.air.philips.com LB intermittently
returns to urllib (the app's okhttp hides this with silent retries).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request

APP_ID = "9fd505fa9c7111e9a1e3061302926720"      # od.a / app_id — identifier, not secret
HOST = "https://www.api.air.philips.com/"
UA = "okhttp/4.9.3"


def _hmac_hex(data: str, key: str) -> str:
    """gaoda HMACSHA256Utils.sha256_HMAC: HmacSHA256(key, data) -> lowercase hex."""
    return hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()


def _java_urlencode(s: str) -> str:
    """Java URLEncoder.encode(s,"utf-8"): keep -._*; space->+; everything else %XX."""
    out = []
    for ch in s:
        if ch.isalnum() or ch in "-._*":
            out.append(ch)
        elif ch == " ":
            out.append("+")
        else:
            for b in ch.encode("utf-8"):
                out.append("%%%02X" % b)
    return "".join(out)


def _signature(timestamp: str, username: str, msecret: str) -> str:
    """gaoda getTokenV2 signature = sha256_HMAC(sha256_HMAC(bodyParams, mSecret), username)."""
    body_params = "app_id=%s&timestamp=%s&username=%s" % (
        APP_ID, timestamp, _java_urlencode(username))
    return _hmac_hex(_hmac_hex(body_params, msecret), username)


def _request(url, method="GET", body_obj=None, headers=None, timeout=70, retries=5):
    """HTTP request with retry on transient 503. Returns (status, text)."""
    body = None
    if body_obj is not None:
        body = body_obj if isinstance(body_obj, (bytes, bytearray)) else json.dumps(
            body_obj, separators=(",", ":")).encode("utf-8")
    headers = headers or {}
    last = None
    for _ in range(retries):
        req = urllib.request.Request(url, method=method, data=body)
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            r = urllib.request.urlopen(req, timeout=timeout)
            return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = (e.code, e.read().decode("utf-8", "replace"))
            if e.code != 503:
                return last
        except Exception as e:  # noqa: BLE001
            last = (None, f"{type(e).__name__}: {e}")
        time.sleep(2.0)
    return last if last else (None, "no response")


def get_jwt(username: str, msecret: str) -> str:
    """Step 1: signed getToken -> 7-day enduser JWT. Retries on transient 503/non-JSON."""
    for _ in range(8):
        ts = str(int(time.time()))
        sig = _signature(ts, username, msecret)
        body = {"timestamp": ts, "username": username, "app_id": APP_ID}
        headers = {
            "User-Agent": UA,
            "Content-Type": "application/json;charset:utf-8",
            "Signature": sig,
        }
        status, txt = _request(HOST + "enduser/v2/getToken/", method="POST",
                               body_obj=body, headers=headers)
        try:
            data = json.loads(txt)
        except Exception:  # noqa: BLE001
            time.sleep(2.0)
            continue
        if data.get("meta", {}).get("code") == 0:
            return data["data"]["token"]
        raise RuntimeError(f"getToken failed: {status} {txt[:200]}")
    raise RuntimeError("getToken exhausted retries (persistent 503?)")


def get_device_list(jwt: str) -> list[dict]:
    """Step 1b: GET enduser/deviceList/ -> list of device dicts (id + device_info).

    Each entry: {"device_id": "...", "device_info": {name, modelid, type, mac,
    swversion, product_id, service_region, is_online, ...}}.
    """
    headers = {"User-Agent": UA, "Authorization": "jwt " + jwt}
    for _ in range(8):
        status, txt = _request(HOST + "enduser/deviceList/", method="GET",
                               headers=headers)
        try:
            data = json.loads(txt)
        except Exception:  # noqa: BLE001
            time.sleep(2.0)
            continue
        if data.get("meta", {}).get("code") == 0:
            return data.get("data", []) or []
        raise RuntimeError(f"deviceList failed: {status} {txt[:200]}")
    raise RuntimeError("deviceList exhausted retries (persistent 503?)")


def get_mqtt_info(jwt: str, device_ids) -> dict:
    """Step 2: mqttInfo -> {device_id: {host, client_id, endpoint, path}}.

    The SigV4 WSS URL is single-use (one connection per URL) and valid 1h; the
    client_id rotates per call. Retries on transient 503/non-JSON.
    """
    if isinstance(device_ids, str):
        device_ids = [device_ids]
    body = {"device_id": device_ids}
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/json;charset:utf-8",
        "Authorization": "jwt " + jwt,
    }
    for _ in range(8):
        status, txt = _request(HOST + "enduser/v2/mqttInfo/", method="POST",
                               body_obj=body, headers=headers)
        try:
            data = json.loads(txt)
        except Exception:  # noqa: BLE001
            time.sleep(2.0)
            continue
        meta = data.get("meta", {})
        if meta.get("code") == 0:
            return {mi["device_id"]: mi for mi in data["data"]["mqttinfos"]}
        # 16002 "Not binding to the device" is intermittently returned even for
        # correctly-bound devices (deviceList confirms the binding); it clears on
        # retry, so treat it as transient like a 503 rather than a hard failure.
        if meta.get("code") == 16002:
            time.sleep(2.0)
            continue
        raise RuntimeError(f"mqttInfo failed: {status} {txt[:200]}")
    raise RuntimeError("mqttInfo exhausted retries (persistent 503/16002?)")


def jwt_exp(jwt: str) -> int:
    """Decode JWT exp (unix seconds)."""
    import base64
    p = jwt.split(".")[1]
    p += "=" * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))["exp"]


def jwt_seconds_left(jwt: str) -> float:
    """Seconds until the JWT expires."""
    return jwt_exp(jwt) - time.time()


if __name__ == "__main__":
    # ponytail: offline self-check for the hand-written crypto/encoding (the
    # actually error-prone part of this module) — no network, no real
    # credentials. get_jwt/get_device_list/get_mqtt_info need a live account
    # and are proven end-to-end in the config flow instead.
    assert _java_urlencode("a b") == "a+b"
    assert _java_urlencode("a.b-c_d*e") == "a.b-c_d*e"
    assert _java_urlencode("a@b") == "a%40b"
    sig_a = _signature("1000", "PHILIPS:deadbeef", "a_" + "0" * 32)
    sig_b = _signature("1000", "PHILIPS:deadbeef", "a_" + "0" * 32)
    sig_c = _signature("1000", "PHILIPS:deadbeef", "a_" + "1" * 32)
    assert sig_a == sig_b, "signature must be deterministic"
    assert sig_a != sig_c, "signature must depend on msecret"
    assert len(sig_a) == 64, "sha256 hex digest must be 64 chars"
    print("airmatters_auth: self-check OK")
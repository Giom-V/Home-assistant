# Philips Air+ (CX3550/01) for Home Assistant

A custom integration for **Philips Air+ cloud-only fans** such as the
CX3550/01 ("Series 3000" stand fan). These fans have no local API — they are
controlled via an **AWS IoT device shadow over MQTT-over-WSS**, behind the
Philips *air-matters / gaoda* signed auth chain.

> This is **not** the upstream Versuni/HomeID integration. That one (see GitHub
> issue #21 on ShorMeneses/philips-airplus-homeassistant) returns "No devices
> found" for the CX3550 because it targets the AC air-purifier line. This
> integration speaks the fan's actual cloud protocol.

## What it gives you (per fan)

| Entity | Platform | Controls / shows |
|---|---|---|
| Fan | `fan` | on/off, speed 1/2/3 (percentage), presets **sleep** / **natural**, oscillate |
| Key beep | `switch` | key-tone on/off (config) |
| Timer | `switch` | auto-off timer activate (config) |
| Timer remaining | `sensor` | countdown minutes (read-only) |
| Signal strength | `sensor` | WiFi RSSI dBm (diagnostic, off by default) |
| Uptime | `sensor` | device runtime seconds (diagnostic, off by default) |
| Free memory | `sensor` | free heap bytes (diagnostic, off by default) |

All control writes are **verified against a physical fan** (2026-06-27):
power, speed 1/2/3, sleep (D0310C=17), natural (D0310C=130), oscillate
(D0320F), beep (D03130), timer-activate (D03110). The timer-remaining field
(D03211) is read-only (the device sets it; writes are ignored).

## Setup

### 1. Install

Copy this folder into your HA config:

```
custom_components/philips_airplus/
```

so you have `config/custom_components/philips_airplus/manifest.json`. Restart
Home Assistant.

### 2. Add the integration

**Settings → Devices & Services → Add integration → "Philips Air+"**, then:

1. **Upload the Philips Air+ APK** (`com.philips.ph.homecare`). The
   integration extracts the gaoda signing value (`mSecret`) from it locally —
   see [`apk_extract.py`](apk_extract.py) — and never stores or transmits the
   APK itself. Any source works (own device via `adb pull`, or
   [APKMirror, v3.19.0](https://www.apkmirror.com/apk/versuni-netherlands-b-v/philips-air/philips-air-3-19-0-release/) —
   [app overview](https://www.apkmirror.com/apk/versuni-netherlands-b-v/philips-air/)
   if that's since gone stale); the signing value is identical across app
   versions/regions. See the repo root [README](../../README.md) for details
   on why this step exists at all.
2. **Enter your Philips account email** — triggers an emailed 6-digit code.
3. **Enter the code.** The integration derives your account's gaoda
   `user_id` from the login response (see
   [`oneid_login.py`](oneid_login.py)), signs in (signed `getToken` → 7-day
   JWT), discovers your bound devices (`deviceList`), and creates the entry.
   Both fans should appear with the entities above.

No password, no manual IDs, no traffic interception needed. If your account
ever needs re-authenticating, the integration reuses the stored signing value
and only asks for a fresh email code.

## How it works

- `iot_class: cloud_push` — one persistent MQTT-over-WSS connection **per device**.
  The device pushes shadow deltas; entities update from the push (no polling).
- Each (re)connect re-fetches `mqttInfo` because the SigV4 WSS URL is
  **single-use** (1h validity) and the `client_id` rotates.
- Commands publish a `desired` patch to `$aws/things/<id>/shadow/update`; the
  device echoes `reported`, which updates the entity state.
- paho network thread ↔ HA asyncio loop bridged via `call_soon_threadsafe`.
- Reconnect uses exponential backoff (2→300 s).

## Notes / gotchas

- **Close the Philips phone app while HA is connected.** If both hold a
  connection with the same client identity, AWS IoT disconnects one (rc 128);
  the integration backs off and reconnects, but the app will keep fighting it.
- The 7-day JWT is refreshed automatically when <1 day remains; no interaction.
- If auth ever fails (e.g. account revoked), the integration raises a reauth
  flow — you'll only be asked for a fresh email code (the stored signing
  value is reused; only very old entries from before v0.2.0 also need the
  APK step again).
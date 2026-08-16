"""Extract the gaoda ``mSecret`` from the user's own Philips Air+ APK.

Stdlib only (``zipfile`` + ``re``) — no androguard/decompiler needed. The
mSecret has the self-unique format ``a_``+32 hex chars, so a plain regex over
the dex bytecode is sufficient and unambiguous (verified against a real APK:
0.03s, exactly one hit). A bare ``[0-9a-f]{32}`` would be ambiguous (dozens of
candidates in the same APK) — the ``a_`` prefix is what makes this reliable.

Handles both a plain ``.apk`` and ``.apkm``/``.xapk`` split-APK bundles
(themselves a zip containing several ``*.apk`` members — e.g. what APKMirror
serves for multi-arch/language builds) by descending one level into any
nested ``*.apk`` member.

The APK is never modified or kept beyond this call — the caller (config flow)
is responsible for extracting from a temporary upload and discarding it.
"""
from __future__ import annotations

import io
import re
import zipfile

_MSECRET_RE = re.compile(rb"a_[0-9a-f]{32}")


class ApkExtractError(Exception):
    """Raised when the mSecret can't be found or isn't uniquely identified."""


def _scan_dex_members(zf: zipfile.ZipFile, hits: set[str]) -> None:
    for name in zf.namelist():
        if name.endswith(".dex"):
            hits.update(m.decode() for m in _MSECRET_RE.findall(zf.read(name)))
        elif name.endswith(".apk"):
            # .apkm/.xapk bundle: descend one level into the nested split APK.
            try:
                with zipfile.ZipFile(io.BytesIO(zf.read(name))) as inner:
                    _scan_dex_members(inner, hits)
            except zipfile.BadZipFile:
                continue


def extract_msecret(apk_path: str) -> str:
    """Return the unique mSecret string found in the given APK or bundle.

    Raises ApkExtractError if none or more than one candidate is found (wrong
    app, corrupt file, or an APK variant this heuristic doesn't handle).
    """
    hits: set[str] = set()
    try:
        with zipfile.ZipFile(apk_path) as zf:
            _scan_dex_members(zf, hits)
    except zipfile.BadZipFile as err:
        raise ApkExtractError(f"Not a valid APK/zip file: {err}") from err

    if not hits:
        raise ApkExtractError(
            "No mSecret found — wrong app, or an APK variant this doesn't "
            "handle. Try the base APK from your own device (adb pull) instead "
            "of a split/config-only download."
        )
    if len(hits) > 1:
        raise ApkExtractError(f"Ambiguous mSecret candidates found: {sorted(hits)}")
    return hits.pop()


if __name__ == "__main__":
    # ponytail: one runnable, fixture-free self-check for the parsing logic
    # (the actual risk here — ambiguity/format handling) using synthetic
    # in-memory zips, so it works without a real APK on hand.
    import tempfile
    from pathlib import Path

    # Fake, format-only values — never the real mSecret (this file ships in
    # the repo; the real value must never appear in source control).
    GOOD = "a_" + "c0ffee00" * 4
    OTHER = "a_" + "deadbeef" * 4

    def _write_zip(path: Path, members: dict[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w") as zf:
            for name, data in members.items():
                zf.writestr(name, data)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        plain = tmp / "plain.apk"
        _write_zip(plain, {"classes.dex": f"junk {GOOD} junk".encode()})
        assert extract_msecret(str(plain)) == GOOD

        # .apkm bundle: secret lives in a nested split *.apk, not top-level.
        split = io.BytesIO()
        with zipfile.ZipFile(split, "w") as zf:
            zf.writestr("classes.dex", f"junk {GOOD} junk".encode())
        bundle = tmp / "bundle.apkm"
        _write_zip(bundle, {
            "base.apk": split.getvalue(),
            "split_config.en.apk": b"no dex, no secret here",
        })
        assert extract_msecret(str(bundle)) == GOOD

        empty = tmp / "empty.apk"
        _write_zip(empty, {"classes.dex": b"no secret in here"})
        try:
            extract_msecret(str(empty))
            raise AssertionError("expected ApkExtractError for zero hits")
        except ApkExtractError:
            pass

        ambiguous = tmp / "ambiguous.apk"
        _write_zip(ambiguous, {"classes.dex": f"{GOOD} {OTHER}".encode()})
        try:
            extract_msecret(str(ambiguous))
            raise AssertionError("expected ApkExtractError for multiple hits")
        except ApkExtractError:
            pass

        not_a_zip = tmp / "not_a_zip.apk"
        not_a_zip.write_bytes(b"definitely not a zip file")
        try:
            extract_msecret(str(not_a_zip))
            raise AssertionError("expected ApkExtractError for bad zip")
        except ApkExtractError:
            pass

    print("apk_extract: self-check OK")

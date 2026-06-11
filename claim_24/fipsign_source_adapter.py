"""
FIPSign SourceAdapter for CLAIM-24.

This adapter reads current certificate state from an external FIPSign CA at
execution time and normalizes the returned PQCert-like object into the snapshot
shape that RederivationGate compares against the grant's recorded snapshot.

The adapter deliberately does not claim external evidence by itself. A real run
requires a live CA base URL and grants whose source_snapshot values were created
from the same normalization function below.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Callable, Optional

from gate_interface import Grant, SourceAdapter


JsonGetter = Callable[[str], Optional[dict]]


class FIPSignSourceAdapter(SourceAdapter):
    """
    External source adapter for FIPSign CA certificate state.

    Expected read endpoints, per the public CLAIM-24 handoff:
    - GET /ca/certificate/:certId
    - GET /public-key

    The re-derivation gate only needs current source state. Signature verification
    should be layered on top once the exact PQCert signature payload and public-key
    format are pinned. Until then, this adapter records the signature fields that
    the CA returned but does not mark them verified.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        http_get_json: Optional[JsonGetter] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._http_get_json = http_get_json or self._urllib_get_json

    @property
    def agent_writable(self) -> bool:
        return False

    def fetch(self, grant: Grant) -> Optional[dict]:
        cert_id = extract_cert_id(grant)
        if not cert_id:
            return None

        encoded_id = urllib.parse.quote(str(cert_id), safe="")
        raw = self._http_get_json(f"{self.base_url}/ca/certificate/{encoded_id}")
        if raw is None:
            return None
        return normalize_pqcert(raw)

    def fetch_public_key(self) -> Optional[dict]:
        return self._http_get_json(f"{self.base_url}/public-key")

    def _urllib_get_json(self, url: str) -> Optional[dict]:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError):
            return None

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None


def extract_cert_id(grant: Grant) -> Optional[str]:
    """
    Resolve the certificate id without inventing a new scenario schema.

    Preferred: source_snapshot.cert_id / certId / certificate_id. Fallback:
    grant_id, which lets simple one-cert-per-grant fixtures run.
    """

    snapshot = grant.source_snapshot or {}
    for key in ("cert_id", "certId", "certificate_id", "certificateId"):
        if snapshot.get(key):
            return str(snapshot[key])

    meta = snapshot.get("meta")
    if isinstance(meta, dict):
        for key in ("cert_id", "certId", "certificate_id", "certificateId"):
            if meta.get(key):
                return str(meta[key])

    return grant.grant_id


def normalize_pqcert(raw: dict) -> dict:
    """
    Normalize returned certificate state into a stable raw snapshot.

    The field selection is intentionally conservative: it keeps the state that
    matters for CLAIM-24 drift detection while preserving raw meta/status values.
    No derived stale labels are added here.
    """

    status = raw.get("status") if isinstance(raw.get("status"), dict) else {}
    meta = raw.get("meta") if isinstance(raw.get("meta"), dict) else {}

    normalized = {
        "cert_id": first_present(raw, "cert_id", "certId", "certificate_id", "certificateId", "id"),
        "subject": first_present(raw, "subject", "subject_id", "subjectId", "holder", "owner"),
        "issuer": first_present(raw, "issuer", "issuer_id", "issuerId", "ca"),
        "scope": first_present(raw, "scope", "scope_ceiling", "scopeCeiling") or meta.get("scope") or meta.get("scope_ceiling"),
        "status": {
            "revoked": bool(status.get("revoked", False)),
            "expired": bool(status.get("expired", False)),
        },
        "meta": sort_json(meta),
    }

    signature = first_present(raw, "signature", "sig")
    if signature is not None:
        normalized["signature"] = signature

    signed_payload = first_present(raw, "signed_payload", "signedPayload", "payload")
    if signed_payload is not None:
        normalized["signed_payload"] = signed_payload

    return sort_json({k: v for k, v in normalized.items() if v is not None})


def first_present(data: dict, *keys: str):
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def sort_json(value):
    if isinstance(value, dict):
        return {key: sort_json(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [sort_json(item) for item in value]
    return value

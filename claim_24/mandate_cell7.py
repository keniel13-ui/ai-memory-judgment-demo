"""Executable CLAIM-24 Cell 7 mapping for FIPSign Mandate.

This module implements the frozen body plus addenda v1, v2, and terminal v3:

* CAPTURE performs one bound, GET-only external read and writes a private baseline,
  capture receipt, and retained raw response.
* EVALUATE verifies the complete carry before loading a project key or performing
  HTTP, performs one current GET, calls the unchanged RederivationGate, and records
  the gate verdict separately from the exact-delta evidence classification.

It does not implement PATCH, signature verification, agent execution authority, or
public redaction/publishing.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import stat
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping, Optional

from gate_interface import AuthorityEvent, Grant, SourceAdapter
from rederivation_gate import RederivationGate


FIPSIGN_ORIGIN = "https://api.fipsign.dev"
PROJECT_KEY_HEADER = "X-API-Key"
DEFAULT_KEY_ENV = "FIPSIGN_API_KEY"
DEFAULT_USER_AGENT = "Self-Correcting-Systems-CLAIM24-Mandate-Cell7/1.0"

CONTRACT_BODY_SHA256 = "ad8b5066db2644be63761095df9e0712b29b53eccfe452773167ea0b8bc776c6"
CONTRACT_V1_SHA256 = "8a8a6715bb50d639db5762e910a6c5efd91707d63a4801f4199647ebd6e2efa6"
CONTRACT_V2_SHA256 = "4e6c5d987f68bb5ee739d09e4afd404f9294efb28a10d72f4ce1c3b98d6a2799"
CONTRACT_V3_SHA256 = "4033e3674e7e7997cf7ed2473648874e2724ea497a986ad514541cf7d9471dc3"

MAX_CAPTURE_TO_EVALUATE_SECONDS = 14_400
EXPIRY_SAFETY_MARGIN_SECONDS = 300
MAX_RESPONSE_BYTES = 2 * 1024 * 1024

BASELINE_NAME = "baseline.json"
CAPTURE_RECEIPT_NAME = "capture_receipt.json"
CAPTURE_RAW_NAME = "source_response_capture.raw"
EVALUATE_RAW_NAME = "source_response_evaluate.raw"
EVALUATION_RECEIPT_NAME = "evaluation_receipt.json"

FORBIDDEN_RESPONSE_KEYS = {
    "token",
    "api-key",
    "api_key",
    "authorization",
    "secret",
    "private-key",
    "private_key",
}

BOUND_ID_RE = re.compile(r"^mdt_[A-Za-z0-9_-]+$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,80}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

BASELINE_KEYS = {
    "schema_version",
    "run_id",
    "bound_id",
    "capture_time_utc",
    "source_expires_at_utc",
    "evaluate_deadline_utc",
    "normalized_snapshot",
}

SNAPSHOT_KEYS = {"entity_id", "subject", "scope_original", "scope", "status"}

CAPTURE_RECEIPT_KEYS = {
    "schema_version",
    "phase",
    "run_id",
    "bound_id",
    "capture_time_utc",
    "source_expires_at_utc",
    "evaluate_deadline_utc",
    "request_method",
    "request_origin",
    "request_path",
    "http_status",
    "capture_raw_file",
    "capture_raw_sha256",
    "baseline_file",
    "baseline_sha256",
    "adapter_sha256",
    "contract_body_sha256",
    "contract_v1_sha256",
    "contract_v2_sha256",
}

HttpGetBytes = Callable[[str, Mapping[str, str]], tuple[int, bytes]]
KeyLoader = Callable[[], str]
NowFn = Callable[[], datetime]


class _RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect before urllib can copy the project-key header."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise MandateCell7Error(
            "INVALID_SOURCE_RESPONSE",
            "redirect refused for bound Mandate GET",
        )


class MandateCell7Error(RuntimeError):
    """Fail-closed error with a stable, non-secret result code."""

    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(code if not detail else f"{code}: {detail}")


@dataclass(frozen=True)
class MandateRead:
    http_status: int
    raw_bytes: bytes
    raw_sha256: str
    parsed: dict
    normalized: dict
    source_expires_at: datetime


@dataclass(frozen=True)
class CaptureResult:
    status: str
    run_id: str
    run_dir: str
    baseline_path: str
    baseline_sha256: str
    capture_receipt_path: str
    capture_receipt_sha256: str
    capture_raw_path: str
    http_calls: int

    def public_dict(self) -> dict:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "baseline_path": self.baseline_path,
            "baseline_sha256": self.baseline_sha256,
            "capture_receipt_path": self.capture_receipt_path,
            "capture_receipt_sha256": self.capture_receipt_sha256,
            "capture_raw_path": self.capture_raw_path,
            "http_calls": self.http_calls,
        }


@dataclass(frozen=True)
class EvidenceClassification:
    gate_decision: str
    changed_keys: tuple[str, ...]
    evidence_class: str
    cell_7_preconditions_passed: bool

    def as_dict(self) -> dict:
        return {
            "gate_decision": self.gate_decision,
            "changed_keys": list(self.changed_keys),
            "evidence_class": self.evidence_class,
            "cell_7_preconditions_passed": self.cell_7_preconditions_passed,
        }


@dataclass(frozen=True)
class EvaluationResult:
    status: str
    run_id: str
    gate_decision: Optional[str]
    evidence_class: str
    cell_7_preconditions_passed: bool
    changed_keys: tuple[str, ...]
    evaluation_receipt_path: Optional[str]
    evaluation_receipt_sha256: Optional[str]
    evaluate_raw_path: Optional[str]
    http_calls: int
    key_load_calls: int

    def public_dict(self) -> dict:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "gate_decision": self.gate_decision,
            "evidence_class": self.evidence_class,
            "cell_7_preconditions_passed": self.cell_7_preconditions_passed,
            "changed_keys": list(self.changed_keys),
            "evaluation_receipt_path": self.evaluation_receipt_path,
            "evaluation_receipt_sha256": self.evaluation_receipt_sha256,
            "evaluate_raw_path": self.evaluate_raw_path,
            "http_calls": self.http_calls,
            "key_load_calls": self.key_load_calls,
        }


@dataclass(frozen=True)
class VerifiedCarry:
    run_dir: Path
    baseline: dict
    receipt: dict
    capture_raw: bytes
    capture_parsed: dict
    capture_time: datetime
    source_expires_at: datetime
    evaluate_deadline: datetime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    value = require_aware_datetime(value, "timestamp")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_aware_datetime(
    value: object,
    field: str,
    error_code: str = "INVALID_SOURCE_RESPONSE",
) -> datetime:
    if not isinstance(value, str) or not value:
        raise MandateCell7Error(error_code, f"{field} must be a timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MandateCell7Error(error_code, f"{field} is not ISO-8601") from exc
    try:
        return require_aware_datetime(parsed, field).astimezone(timezone.utc)
    except MandateCell7Error as exc:
        raise MandateCell7Error(error_code, exc.detail) from exc


def require_aware_datetime(value: datetime, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise MandateCell7Error("INVALID_TIME", f"{field} must be timezone-aware")
    return value


def validate_bound_id(bound_id: str) -> str:
    if not isinstance(bound_id, str) or not BOUND_ID_RE.fullmatch(bound_id):
        raise MandateCell7Error("INVALID_BOUND_ID", "Mandate id must be one mdt_ path segment")
    return bound_id


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        raise MandateCell7Error("INVALID_RUN_ID", "run id must be 8-80 safe characters")
    return run_id


def require_sha256(value: str, field: str) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{field} must be lowercase SHA-256")
    return value


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def adapter_sha256() -> str:
    return sha256_bytes(Path(__file__).read_bytes())


def canonical_json_bytes(value: dict) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def parse_json_bytes(data: bytes, error_code: str = "INVALID_SOURCE_RESPONSE") -> dict:
    if not isinstance(data, bytes) or len(data) > MAX_RESPONSE_BYTES:
        raise MandateCell7Error(error_code, "response is absent or exceeds size limit")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MandateCell7Error(error_code, "response is not UTF-8 JSON") from exc

    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise MandateCell7Error(error_code, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        parsed = json.loads(text, object_pairs_hook=no_duplicates)
    except MandateCell7Error:
        raise
    except json.JSONDecodeError as exc:
        raise MandateCell7Error(error_code, "response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise MandateCell7Error(error_code, "top-level JSON must be an object")
    return parsed


def find_forbidden_response_key(value: object) -> Optional[str]:
    """Walk every object, including objects nested inside arrays."""

    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str) and key.lower() in FORBIDDEN_RESPONSE_KEYS:
                return key
            found = find_forbidden_response_key(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_forbidden_response_key(child)
            if found is not None:
                return found
    return None


def _normalize_scope(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise MandateCell7Error("INVALID_SOURCE_RESPONSE", f"{field} must be a list of strings")
    return sorted(set(value))


def _mandate_object(parsed: dict) -> dict:
    mandate = parsed.get("mandate")
    if not isinstance(mandate, dict):
        raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "response.mandate must be an object")
    return mandate


def normalize_mandate(parsed: dict) -> dict:
    mandate = _mandate_object(parsed)
    required = ("id", "agentId", "scopeOriginal", "scopeCurrent", "status")
    missing = [key for key in required if key not in mandate]
    if missing:
        raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "missing required Mandate fields")

    entity_id = mandate["id"]
    subject = mandate["agentId"]
    status_value = mandate["status"]
    validate_bound_id(entity_id)
    if not isinstance(subject, str) or not subject:
        raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "agentId must be a non-empty string")
    if (
        not isinstance(status_value, str)
        or not status_value
        or status_value != status_value.lower()
    ):
        raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "status must be an exact lower-case string")

    return {
        "entity_id": entity_id,
        "subject": subject,
        "scope_original": _normalize_scope(mandate["scopeOriginal"], "scopeOriginal"),
        "scope": _normalize_scope(mandate["scopeCurrent"], "scopeCurrent"),
        "status": status_value,
    }


def mandate_expires_at(parsed: dict) -> datetime:
    mandate = _mandate_object(parsed)
    return parse_aware_datetime(mandate.get("expiresAt"), "mandate.expiresAt")


def baseline_preconditions(snapshot: dict, bound_id: str) -> bool:
    return (
        set(snapshot) == SNAPSHOT_KEYS
        and snapshot.get("entity_id") == bound_id
        and snapshot.get("status") == "active"
        and snapshot.get("scope") == snapshot.get("scope_original")
    )


def changed_keys(before: dict, after: dict) -> tuple[str, ...]:
    missing = object()
    return tuple(
        sorted(
            key
            for key in set(before) | set(after)
            if before.get(key, missing) != after.get(key, missing)
        )
    )


def _raw_scope_order_only(before_raw: Optional[dict], after_raw: Optional[dict]) -> bool:
    if not isinstance(before_raw, dict) or not isinstance(after_raw, dict):
        return False
    try:
        before = _mandate_object(before_raw)
        after = _mandate_object(after_raw)
    except MandateCell7Error:
        return False
    found_order_change = False
    for key in ("scopeOriginal", "scopeCurrent"):
        left = before.get(key)
        right = after.get(key)
        if not isinstance(left, list) or not isinstance(right, list):
            return False
        if any(not isinstance(item, str) for item in left + right):
            return False
        if left != right:
            # M2 is an order-only control. A changed duplicate count may normalize
            # to the same set, but it is not an order-only raw input change.
            if sorted(left) != sorted(right):
                return False
            found_order_change = True
    return found_order_change


def classify_evidence(
    event: AuthorityEvent,
    *,
    before_raw: Optional[dict] = None,
    after_raw: Optional[dict] = None,
) -> EvidenceClassification:
    source_before = event.source_snapshot if isinstance(event.source_snapshot, dict) else {}
    source_after = event.source_current if isinstance(event.source_current, dict) else {}

    if event.decision == "ALLOW":
        evidence_class = (
            "ORDER_NORMALIZED_CONTROL"
            if _raw_scope_order_only(before_raw, after_raw)
            else "UNCHANGED_CONTROL"
        )
        return EvidenceClassification(event.decision, (), evidence_class, False)

    if event.decision == "REFUSED_UNREACHABLE":
        return EvidenceClassification(event.decision, (), "SOURCE_UNREACHABLE", False)

    if event.decision == "BLOCK":
        evidence_class = "TTL_EXPIRED" if "ttl expired" in event.notes.lower() else "BLOCKED_CONTROL"
        moved = changed_keys(source_before, source_after) if source_after else ()
        return EvidenceClassification(event.decision, moved, evidence_class, False)

    delta = event.condition_delta
    if (
        event.decision != "REFUSED_STALE"
        or not isinstance(delta, dict)
        or set(delta) != {"before", "after"}
        or not isinstance(delta.get("before"), dict)
        or not isinstance(delta.get("after"), dict)
        or delta["before"] != source_before
        or delta["after"] != source_after
    ):
        moved = changed_keys(source_before, source_after) if source_after else ()
        return EvidenceClassification(event.decision, moved, "INVALID_FOR_CELL_7", False)

    before = delta["before"]
    after = delta["after"]
    moved = changed_keys(before, after)

    original = before.get("scope_original")
    current_scope = after.get("scope")
    if isinstance(original, list) and isinstance(current_scope, list):
        if not set(current_scope).issubset(set(original)):
            return EvidenceClassification(
                event.decision, moved, "INVALID_SOURCE_CONTRACT", False
            )

    passes = (
        moved == ("scope",)
        and before.get("entity_id") == after.get("entity_id")
        and before.get("subject") == after.get("subject")
        and before.get("scope_original") == after.get("scope_original")
        and before.get("status") == after.get("status") == "active"
        and isinstance(before.get("scope"), list)
        and isinstance(after.get("scope"), list)
        and set(after["scope"]) < set(before["scope"])
        and set(before["scope"]) == set(before.get("scope_original", []))
    )
    if passes:
        return EvidenceClassification(
            event.decision, moved, "CELL_7_CLEAN_STATUS_SCOPE_DRIFT", True
        )
    return EvidenceClassification(event.decision, moved, "INVALID_FOR_CELL_7", False)


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    total = 0
    while total < len(view):
        written = os.write(fd, view[total:])
        if written <= 0:
            raise OSError("short write")
        total += written


def write_private_exclusive(path: Path, data: bytes) -> None:
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = None
    created = False
    try:
        fd = os.open(path, flags, 0o600)
        created = True
        os.fchmod(fd, 0o600)
        _write_all(fd, data)
        os.fsync(fd)
    except FileExistsError as exc:
        raise MandateCell7Error("DESTINATION_EXISTS", str(path.name)) from exc
    except OSError as exc:
        if created:
            try:
                os.unlink(path)
            except OSError:
                pass
        raise MandateCell7Error("ARTIFACT_WRITE_FAILED", str(path.name)) from exc
    finally:
        if fd is not None:
            os.close(fd)


def _validate_run_dir(run_dir: Path) -> Path:
    run_dir = Path(run_dir)
    try:
        info = os.lstat(run_dir)
    except OSError as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "run directory unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "run directory must be a real directory")
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "run directory owner/mode mismatch")
    return run_dir.resolve(strict=True)


def _private_artifact_path(run_dir: Path, name: str) -> Path:
    root = _validate_run_dir(run_dir)
    candidate = root / name
    if candidate.parent != root:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "artifact path escaped run directory")
    return candidate


def read_private_file(path: Path) -> bytes:
    path = Path(path)
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"missing {path.name}") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{path.name} is not a regular file")
    if before.st_uid != os.getuid() or stat.S_IMODE(before.st_mode) != 0o600:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{path.name} owner/mode mismatch")

    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"cannot open {path.name}") from exc
    try:
        opened = os.fstat(fd)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{path.name} changed during open")
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, 65_536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{path.name} too large")
            chunks.append(chunk)
        after = os.fstat(fd)
        if (after.st_size, after.st_mtime_ns) != (opened.st_size, opened.st_mtime_ns):
            raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{path.name} changed during read")
        return b"".join(chunks)
    finally:
        os.close(fd)


class MandateSourceAdapter(SourceAdapter):
    """Bound, GET-only Mandate adapter with an optional counting test seam."""

    def __init__(
        self,
        bound_id: str,
        api_key: str,
        *,
        raw_artifact_path: Optional[Path] = None,
        http_get_bytes: Optional[HttpGetBytes] = None,
        base_url: str = FIPSIGN_ORIGIN,
        timeout_seconds: float = 10.0,
    ):
        self.bound_id = validate_bound_id(bound_id)
        if not isinstance(api_key, str) or not api_key:
            raise MandateCell7Error("MISSING_PROJECT_KEY")
        if base_url != FIPSIGN_ORIGIN:
            raise MandateCell7Error("INVALID_REQUEST_ORIGIN")
        self._api_key: Optional[str] = api_key
        self.base_url = base_url.rstrip("/")
        self.raw_artifact_path = Path(raw_artifact_path) if raw_artifact_path else None
        self.timeout_seconds = timeout_seconds
        self._http_get_bytes = http_get_bytes or self._urllib_get_bytes
        self.http_calls = 0
        self.last_read: Optional[MandateRead] = None

    @property
    def agent_writable(self) -> bool:
        return False

    @property
    def request_path(self) -> str:
        encoded = urllib.parse.quote(self.bound_id, safe="")
        return f"/mandate/{encoded}"

    @property
    def request_url(self) -> str:
        return f"{self.base_url}{self.request_path}"

    def clear_key(self) -> None:
        self._api_key = None

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            raise MandateCell7Error("MISSING_PROJECT_KEY")
        return {
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
            PROJECT_KEY_HEADER: self._api_key,
        }

    def _urllib_get_bytes(self, url: str, headers: Mapping[str, str]) -> tuple[int, bytes]:
        if url != self.request_url:
            raise MandateCell7Error("INVALID_REQUEST_PATH")
        request = urllib.request.Request(url, headers=dict(headers), method="GET")
        opener = urllib.request.build_opener(_RejectRedirectHandler())
        try:
            with opener.open(request, timeout=self.timeout_seconds) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
                return int(response.status), body
        except urllib.error.HTTPError as exc:
            body = exc.read(MAX_RESPONSE_BYTES + 1)
            return int(exc.code), body
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            raise MandateCell7Error("SOURCE_UNREACHABLE") from exc

    def read(self) -> Optional[MandateRead]:
        self.http_calls += 1
        try:
            status_code, raw = self._http_get_bytes(self.request_url, self._headers())
        except MandateCell7Error:
            raise
        except Exception as exc:
            raise MandateCell7Error("SOURCE_UNREACHABLE") from exc
        if type(status_code) is not int or not isinstance(raw, bytes):
            raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "GET seam returned wrong types")
        if len(raw) > MAX_RESPONSE_BYTES:
            raise MandateCell7Error("INVALID_SOURCE_RESPONSE", "response exceeds size limit")
        if status_code != 200:
            return None

        parsed = parse_json_bytes(raw)
        forbidden = find_forbidden_response_key(parsed)
        if forbidden is not None:
            raise MandateCell7Error("INVALID_SENSITIVE_SOURCE_RESPONSE")

        normalized = normalize_mandate(parsed)
        expires_at = mandate_expires_at(parsed)
        if self.raw_artifact_path is not None:
            # Persist the exact bytes, unchanged, only after they can be parsed and
            # recursively scanned for forbidden keys. This resolves v3's security
            # ordering without turning the operator response into normalized JSON.
            write_private_exclusive(self.raw_artifact_path, raw)
        result = MandateRead(
            http_status=status_code,
            raw_bytes=raw,
            raw_sha256=sha256_bytes(raw),
            parsed=parsed,
            normalized=normalized,
            source_expires_at=expires_at,
        )
        self.last_read = result
        return result

    def fetch(self, grant: Grant) -> Optional[dict]:
        snapshot = grant.source_snapshot if isinstance(grant.source_snapshot, dict) else {}
        if grant.grant_id != self.bound_id or snapshot.get("entity_id") != self.bound_id:
            raise MandateCell7Error("INVALID_BOUND_ID", "grant is not bound to adapter id")
        try:
            result = self.read()
        except MandateCell7Error as exc:
            # The frozen gate has one fail-closed representation for an unavailable
            # or invalid current source. Sensitive material is different: it must
            # stop the run explicitly before persistence, never be flattened here.
            if exc.code in {"SOURCE_UNREACHABLE", "INVALID_SOURCE_RESPONSE"}:
                return None
            raise
        return None if result is None else result.normalized


def _make_run_dir(run_root: Path, run_id: str) -> Path:
    run_root = Path(run_root)
    run_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root_info = os.lstat(run_root)
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise MandateCell7Error("INVALID_RUN_ROOT")
    run_dir = run_root / validate_run_id(run_id)
    try:
        os.mkdir(run_dir, 0o700)
        os.chmod(run_dir, 0o700)
    except FileExistsError as exc:
        raise MandateCell7Error("RUN_ID_EXISTS") from exc
    return _validate_run_dir(run_dir)


def capture(
    *,
    bound_id: str,
    run_root: Path,
    api_key: str,
    run_id: Optional[str] = None,
    http_get_bytes: Optional[HttpGetBytes] = None,
    now_fn: NowFn = utc_now,
    base_url: str = FIPSIGN_ORIGIN,
) -> CaptureResult:
    if base_url != FIPSIGN_ORIGIN:
        raise MandateCell7Error("INVALID_REQUEST_ORIGIN")
    bound_id = validate_bound_id(bound_id)
    run_id = validate_run_id(run_id or f"mandate-{secrets.token_hex(12)}")
    run_dir = _make_run_dir(run_root, run_id)
    raw_path = _private_artifact_path(run_dir, CAPTURE_RAW_NAME)
    baseline_path = _private_artifact_path(run_dir, BASELINE_NAME)
    receipt_path = _private_artifact_path(run_dir, CAPTURE_RECEIPT_NAME)

    adapter = MandateSourceAdapter(
        bound_id,
        api_key,
        raw_artifact_path=raw_path,
        http_get_bytes=http_get_bytes,
        base_url=base_url,
    )
    try:
        read = adapter.read()
    finally:
        adapter.clear_key()
    if read is None:
        raise MandateCell7Error("SOURCE_UNREACHABLE")

    capture_time = require_aware_datetime(now_fn(), "capture_time").astimezone(timezone.utc)
    if not baseline_preconditions(read.normalized, bound_id):
        raise MandateCell7Error("INVALID_BASELINE_PRECONDITIONS")
    minimum_life = timedelta(
        seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS + EXPIRY_SAFETY_MARGIN_SECONDS
    )
    if read.source_expires_at - capture_time <= minimum_life:
        raise MandateCell7Error("INSUFFICIENT_FIXTURE_LIFETIME")
    deadline = capture_time + timedelta(seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS)

    baseline = {
        "schema_version": 1,
        "run_id": run_id,
        "bound_id": bound_id,
        "capture_time_utc": iso_utc(capture_time),
        "source_expires_at_utc": iso_utc(read.source_expires_at),
        "evaluate_deadline_utc": iso_utc(deadline),
        "normalized_snapshot": read.normalized,
    }
    baseline_bytes = canonical_json_bytes(baseline)
    baseline_hash = sha256_bytes(baseline_bytes)
    write_private_exclusive(baseline_path, baseline_bytes)

    receipt = {
        "schema_version": 1,
        "phase": "CAPTURE",
        "run_id": run_id,
        "bound_id": bound_id,
        "capture_time_utc": iso_utc(capture_time),
        "source_expires_at_utc": iso_utc(read.source_expires_at),
        "evaluate_deadline_utc": iso_utc(deadline),
        "request_method": "GET",
        "request_origin": base_url.rstrip("/"),
        "request_path": adapter.request_path,
        "http_status": read.http_status,
        "capture_raw_file": CAPTURE_RAW_NAME,
        "capture_raw_sha256": read.raw_sha256,
        "baseline_file": BASELINE_NAME,
        "baseline_sha256": baseline_hash,
        "adapter_sha256": adapter_sha256(),
        "contract_body_sha256": CONTRACT_BODY_SHA256,
        "contract_v1_sha256": CONTRACT_V1_SHA256,
        "contract_v2_sha256": CONTRACT_V2_SHA256,
    }
    receipt_bytes = canonical_json_bytes(receipt)
    receipt_hash = sha256_bytes(receipt_bytes)
    write_private_exclusive(receipt_path, receipt_bytes)

    return CaptureResult(
        status="CAPTURED",
        run_id=run_id,
        run_dir=str(run_dir),
        baseline_path=str(baseline_path),
        baseline_sha256=baseline_hash,
        capture_receipt_path=str(receipt_path),
        capture_receipt_sha256=receipt_hash,
        capture_raw_path=str(raw_path),
        http_calls=adapter.http_calls,
    )


def _require_exact_keys(value: dict, expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"{label} keys differ")


def verify_carry(
    *,
    run_dir: Path,
    expected_baseline_sha256: str,
    expected_capture_receipt_sha256: str,
) -> VerifiedCarry:
    expected_baseline_sha256 = require_sha256(expected_baseline_sha256, "baseline hash")
    expected_capture_receipt_sha256 = require_sha256(
        expected_capture_receipt_sha256, "capture receipt hash"
    )
    root = _validate_run_dir(run_dir)
    baseline_path = _private_artifact_path(root, BASELINE_NAME)
    receipt_path = _private_artifact_path(root, CAPTURE_RECEIPT_NAME)
    raw_path = _private_artifact_path(root, CAPTURE_RAW_NAME)

    receipt_bytes = read_private_file(receipt_path)
    if sha256_bytes(receipt_bytes) != expected_capture_receipt_sha256:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "capture receipt hash mismatch")
    receipt = parse_json_bytes(receipt_bytes, "INVALID_BASELINE_CARRY")
    _require_exact_keys(receipt, CAPTURE_RECEIPT_KEYS, "capture receipt")
    if canonical_json_bytes(receipt) != receipt_bytes:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "capture receipt is not canonical")

    baseline_bytes = read_private_file(baseline_path)
    baseline_hash = sha256_bytes(baseline_bytes)
    if baseline_hash != expected_baseline_sha256 or baseline_hash != receipt["baseline_sha256"]:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "baseline hash mismatch")
    baseline = parse_json_bytes(baseline_bytes, "INVALID_BASELINE_CARRY")
    _require_exact_keys(baseline, BASELINE_KEYS, "baseline")
    if canonical_json_bytes(baseline) != baseline_bytes:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "baseline is not canonical")

    raw_bytes = read_private_file(raw_path)
    if sha256_bytes(raw_bytes) != receipt["capture_raw_sha256"]:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "capture raw hash mismatch")
    capture_parsed = parse_json_bytes(raw_bytes, "INVALID_BASELINE_CARRY")
    if find_forbidden_response_key(capture_parsed) is not None:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "capture raw contains sensitive key")
    try:
        renormalized = normalize_mandate(capture_parsed)
    except MandateCell7Error as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", exc.detail) from exc
    if renormalized != baseline["normalized_snapshot"]:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "raw response does not derive baseline")

    if not isinstance(baseline.get("normalized_snapshot"), dict):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "snapshot must be an object")
    _require_exact_keys(baseline["normalized_snapshot"], SNAPSHOT_KEYS, "snapshot")
    if type(receipt["schema_version"]) is not int or receipt["schema_version"] != 1:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "receipt schema mismatch")
    if type(baseline["schema_version"]) is not int or baseline["schema_version"] != 1:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "baseline schema mismatch")
    if receipt["phase"] != "CAPTURE" or receipt["request_method"] != "GET":
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "receipt phase/method mismatch")
    if receipt["request_origin"] != FIPSIGN_ORIGIN:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "request origin mismatch")
    if receipt["http_status"] != 200:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "capture status was not 200")
    if receipt["capture_raw_file"] != CAPTURE_RAW_NAME or receipt["baseline_file"] != BASELINE_NAME:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "artifact filename mismatch")
    for field in ("capture_raw_sha256", "baseline_sha256", "adapter_sha256"):
        require_sha256(receipt[field], field)
    if receipt["adapter_sha256"] != adapter_sha256():
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "adapter code hash mismatch")
    if (
        receipt["contract_body_sha256"] != CONTRACT_BODY_SHA256
        or receipt["contract_v1_sha256"] != CONTRACT_V1_SHA256
        or receipt["contract_v2_sha256"] != CONTRACT_V2_SHA256
    ):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "contract hash mismatch")

    try:
        run_id = validate_run_id(receipt["run_id"])
        bound_id = validate_bound_id(receipt["bound_id"])
    except MandateCell7Error as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", exc.detail) from exc
    if root.name != run_id:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "run directory id mismatch")
    if baseline["run_id"] != run_id or baseline["bound_id"] != bound_id:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "baseline identity mismatch")
    if receipt["request_path"] != f"/mandate/{urllib.parse.quote(bound_id, safe='')}":
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "request path mismatch")

    capture_time = parse_aware_datetime(
        receipt["capture_time_utc"], "capture_time_utc", "INVALID_BASELINE_CARRY"
    )
    source_expires = parse_aware_datetime(
        receipt["source_expires_at_utc"],
        "source_expires_at_utc",
        "INVALID_BASELINE_CARRY",
    )
    deadline = parse_aware_datetime(
        receipt["evaluate_deadline_utc"],
        "evaluate_deadline_utc",
        "INVALID_BASELINE_CARRY",
    )
    if (
        baseline["capture_time_utc"] != receipt["capture_time_utc"]
        or baseline["source_expires_at_utc"] != receipt["source_expires_at_utc"]
        or baseline["evaluate_deadline_utc"] != receipt["evaluate_deadline_utc"]
    ):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "timestamp carry mismatch")
    if deadline != capture_time + timedelta(seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "deadline mismatch")
    try:
        raw_source_expiry = mandate_expires_at(capture_parsed)
    except MandateCell7Error as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", exc.detail) from exc
    if raw_source_expiry != source_expires:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "source expiry mismatch")
    if not baseline_preconditions(baseline["normalized_snapshot"], bound_id):
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "baseline preconditions fail")

    return VerifiedCarry(
        run_dir=root,
        baseline=baseline,
        receipt=receipt,
        capture_raw=raw_bytes,
        capture_parsed=capture_parsed,
        capture_time=capture_time,
        source_expires_at=source_expires,
        evaluate_deadline=deadline,
    )


def _destination_must_not_exist(path: Path) -> None:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", f"cannot inspect {path.name}") from exc
    raise MandateCell7Error("DESTINATION_EXISTS", path.name)


def evaluate(
    *,
    run_dir: Path,
    expected_baseline_sha256: str,
    expected_capture_receipt_sha256: str,
    key_loader: KeyLoader,
    http_get_bytes: Optional[HttpGetBytes] = None,
    now_fn: NowFn = utc_now,
    base_url: str = FIPSIGN_ORIGIN,
) -> EvaluationResult:
    """Verify the carry and time window before invoking key_loader or HTTP."""

    if base_url != FIPSIGN_ORIGIN:
        raise MandateCell7Error("INVALID_REQUEST_ORIGIN")
    carry = verify_carry(
        run_dir=run_dir,
        expected_baseline_sha256=expected_baseline_sha256,
        expected_capture_receipt_sha256=expected_capture_receipt_sha256,
    )
    now = require_aware_datetime(now_fn(), "evaluate_time").astimezone(timezone.utc)
    run_id = carry.baseline["run_id"]
    if now < carry.capture_time:
        raise MandateCell7Error("INVALID_BASELINE_CARRY", "evaluation predates capture")

    evaluate_raw_path = _private_artifact_path(carry.run_dir, EVALUATE_RAW_NAME)
    evaluation_receipt_path = _private_artifact_path(carry.run_dir, EVALUATION_RECEIPT_NAME)
    _destination_must_not_exist(evaluate_raw_path)
    _destination_must_not_exist(evaluation_receipt_path)

    if (
        now > carry.evaluate_deadline
        or now > carry.source_expires_at - timedelta(seconds=EXPIRY_SAFETY_MARGIN_SECONDS)
    ):
        expired_receipt = {
            "schema_version": 1,
            "phase": "EVALUATE",
            "status": "EXPIRED_WINDOW",
            "run_id": run_id,
            "bound_id": carry.baseline["bound_id"],
            "capture_time_utc": iso_utc(carry.capture_time),
            "evaluate_time_utc": iso_utc(now),
            "source_expires_at_utc": iso_utc(carry.source_expires_at),
            "evaluate_deadline_utc": iso_utc(carry.evaluate_deadline),
            "capture_receipt_sha256": expected_capture_receipt_sha256,
            "baseline_sha256": expected_baseline_sha256,
            "http_calls": 0,
            "key_load_calls": 0,
        }
        expired_bytes = canonical_json_bytes(expired_receipt)
        expired_hash = sha256_bytes(expired_bytes)
        write_private_exclusive(evaluation_receipt_path, expired_bytes)
        return EvaluationResult(
            status="EXPIRED_WINDOW",
            run_id=run_id,
            gate_decision=None,
            evidence_class="EXPIRED_WINDOW",
            cell_7_preconditions_passed=False,
            changed_keys=(),
            evaluation_receipt_path=str(evaluation_receipt_path),
            evaluation_receipt_sha256=expired_hash,
            evaluate_raw_path=None,
            http_calls=0,
            key_load_calls=0,
        )

    key_load_calls = 1
    api_key = key_loader()
    if not isinstance(api_key, str) or not api_key:
        raise MandateCell7Error("MISSING_PROJECT_KEY")
    bound_id = carry.baseline["bound_id"]
    adapter = MandateSourceAdapter(
        bound_id,
        api_key,
        raw_artifact_path=evaluate_raw_path,
        http_get_bytes=http_get_bytes,
        base_url=base_url,
    )
    grant = Grant(
        grant_id=bound_id,
        recipient=carry.baseline["normalized_snapshot"]["subject"],
        scope=" ".join(carry.baseline["normalized_snapshot"]["scope_original"]),
        issued_at=carry.capture_time,
        ttl_hours=MAX_CAPTURE_TO_EVALUATE_SECONDS // 3600,
        source_snapshot=carry.baseline["normalized_snapshot"],
    )
    try:
        event = RederivationGate(adapter).evaluate(grant, now)
    except MandateCell7Error:
        raise
    finally:
        adapter.clear_key()

    current_read = adapter.last_read
    classification = classify_evidence(
        event,
        before_raw=carry.capture_parsed,
        after_raw=current_read.parsed if current_read else None,
    )
    evaluate_raw_hash = current_read.raw_sha256 if current_read else None
    receipt = {
        "schema_version": 1,
        "phase": "EVALUATE",
        "status": "EVALUATED",
        "run_id": run_id,
        "bound_id": bound_id,
        "capture_time_utc": iso_utc(carry.capture_time),
        "evaluate_time_utc": iso_utc(now),
        "source_expires_at_utc": iso_utc(carry.source_expires_at),
        "evaluate_deadline_utc": iso_utc(carry.evaluate_deadline),
        "request_method": "GET",
        "request_origin": base_url.rstrip("/"),
        "request_path": adapter.request_path,
        "http_status": current_read.http_status if current_read else None,
        "capture_receipt_sha256": expected_capture_receipt_sha256,
        "baseline_sha256": expected_baseline_sha256,
        "capture_raw_sha256": carry.receipt["capture_raw_sha256"],
        "evaluate_raw_file": EVALUATE_RAW_NAME if current_read else None,
        "evaluate_raw_sha256": evaluate_raw_hash,
        "adapter_sha256": adapter_sha256(),
        "contract_body_sha256": CONTRACT_BODY_SHA256,
        "contract_v1_sha256": CONTRACT_V1_SHA256,
        "contract_v2_sha256": CONTRACT_V2_SHA256,
        "gate_decision": event.decision,
        "changed_keys": list(classification.changed_keys),
        "evidence_class": classification.evidence_class,
        "cell_7_preconditions_passed": classification.cell_7_preconditions_passed,
        "condition_delta": event.condition_delta,
        "live_agent_process_involved": False,
        "source_write_separation_status": (
            "FROZEN_DEPLOYMENT_PRECONDITION_NOT_OS_SANDBOX_DEMONSTRATION"
        ),
        "m7_live_status": "NOT_EXECUTED_BY_SOURCE_OPERATOR",
        "http_calls": adapter.http_calls,
        "key_load_calls": key_load_calls,
        "custody_limit": (
            "Local hashes detect carry edits only while CAPTURE-emitted expected hashes remain fixed; "
            "they are not an independent signature or hostile-same-user tamper proof."
        ),
    }
    receipt_bytes = canonical_json_bytes(receipt)
    receipt_hash = sha256_bytes(receipt_bytes)
    write_private_exclusive(evaluation_receipt_path, receipt_bytes)

    return EvaluationResult(
        status="EVALUATED",
        run_id=run_id,
        gate_decision=event.decision,
        evidence_class=classification.evidence_class,
        cell_7_preconditions_passed=classification.cell_7_preconditions_passed,
        changed_keys=classification.changed_keys,
        evaluation_receipt_path=str(evaluation_receipt_path),
        evaluation_receipt_sha256=receipt_hash,
        evaluate_raw_path=str(evaluate_raw_path) if current_read else None,
        http_calls=adapter.http_calls,
        key_load_calls=key_load_calls,
    )


def load_key_from_env(name: str = DEFAULT_KEY_ENV) -> str:
    value = os.environ.get(name)
    if not value:
        raise MandateCell7Error("MISSING_PROJECT_KEY")
    return value

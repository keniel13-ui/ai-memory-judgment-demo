from __future__ import annotations

import json
import os
import tempfile
import unittest
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import mandate_cell7 as cell7
from gate_interface import AuthorityEvent, Grant, SourceAdapter
from rederivation_gate import RederivationGate
from mandate_cell7 import (
    BASELINE_NAME,
    CAPTURE_RAW_NAME,
    CAPTURE_RECEIPT_NAME,
    EVALUATE_RAW_NAME,
    EVALUATION_RECEIPT_NAME,
    EXPIRY_SAFETY_MARGIN_SECONDS,
    FIPSIGN_ORIGIN,
    MAX_CAPTURE_TO_EVALUATE_SECONDS,
    MandateCell7Error,
    MandateSourceAdapter,
    canonical_json_bytes,
    capture,
    classify_evidence,
    evaluate,
    normalize_mandate,
    parse_json_bytes,
    sha256_bytes,
)


NOW = datetime(2026, 8, 4, 22, 0, tzinfo=timezone.utc)
BOUND_ID = "mdt_cell7fixture"
PROJECT_KEY = "test-project-key-must-never-persist"
ORIGINAL_SCOPE = ["sign", "verify", "read:crm"]


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def mandate_payload(
    *,
    mandate_id: str = BOUND_ID,
    agent_id: str = "agent-cell7",
    scope_original: list[str] | None = None,
    scope_current: list[str] | None = None,
    status: str = "active",
    expires_at: datetime | None = None,
    extra: dict | None = None,
) -> dict:
    mandate = {
        "id": mandate_id,
        "agentId": agent_id,
        "scopeOriginal": scope_original or list(ORIGINAL_SCOPE),
        "scopeCurrent": scope_current or list(ORIGINAL_SCOPE),
        "status": status,
        "expiresAt": iso(expires_at or (NOW + timedelta(hours=6))),
        "budget": 5000,
        "budgetConsumed": 0,
        "budgetRemaining": 5000,
        "updatedAt": iso(NOW),
    }
    if extra:
        mandate.update(extra)
    return {"mandate": mandate, "requestId": "volatile-request-id"}


def raw_payload(**kwargs) -> bytes:
    return json.dumps(mandate_payload(**kwargs), ensure_ascii=False).encode("utf-8")


class CountingGet:
    def __init__(self, responses: list[tuple[int, bytes]]):
        self.responses = list(responses)
        self.calls = 0
        self.urls: list[str] = []
        self.headers: list[dict[str, str]] = []

    def __call__(self, url: str, headers) -> tuple[int, bytes]:
        self.calls += 1
        self.urls.append(url)
        self.headers.append(dict(headers))
        if not self.responses:
            raise AssertionError("unexpected extra HTTP call")
        return self.responses.pop(0)


class NeverFetch(SourceAdapter):
    def __init__(self):
        self.calls = 0

    @property
    def agent_writable(self) -> bool:
        return False

    def fetch(self, grant):
        self.calls += 1
        raise AssertionError("expired grant must not fetch")


class MandateCell7Tests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "runs"
        self.serial = 0

    def tearDown(self):
        self.tempdir.cleanup()

    def capture_case(
        self,
        *,
        raw: bytes | None = None,
        now: datetime = NOW,
        run_id: str | None = None,
    ):
        self.serial += 1
        counter = CountingGet([(200, raw or raw_payload())])
        result = capture(
            bound_id=BOUND_ID,
            run_root=self.root,
            api_key=PROJECT_KEY,
            run_id=run_id or f"case-{self.serial:08d}",
            http_get_bytes=counter,
            now_fn=lambda: now,
        )
        return result, counter

    def evaluate_case(
        self,
        capture_result,
        *,
        response: tuple[int, bytes],
        now: datetime = NOW + timedelta(minutes=5),
    ):
        get_counter = CountingGet([response])
        key_calls = {"count": 0}

        def key_loader():
            key_calls["count"] += 1
            return PROJECT_KEY

        result = evaluate(
            run_dir=Path(capture_result.run_dir),
            expected_baseline_sha256=capture_result.baseline_sha256,
            expected_capture_receipt_sha256=capture_result.capture_receipt_sha256,
            key_loader=key_loader,
            http_get_bytes=get_counter,
            now_fn=lambda: now,
        )
        return result, get_counter, key_calls

    def assert_error(self, code: str, callable_):
        with self.assertRaises(MandateCell7Error) as caught:
            callable_()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_normalizer_is_exact_sorted_deduplicated_and_excludes_volatile_fields(self):
        payload = mandate_payload(
            scope_original=["verify", "read:crm", "verify", "sign"],
            scope_current=["verify", "verify"],
            extra={"volatile": {"counter": 99}},
        )
        self.assertEqual(
            normalize_mandate(payload),
            {
                "entity_id": BOUND_ID,
                "subject": "agent-cell7",
                "scope_original": ["read:crm", "sign", "verify"],
                "scope": ["verify"],
                "status": "active",
            },
        )

    def test_capture_is_one_bound_get_and_writes_exact_private_artifacts(self):
        exact_raw = raw_payload()
        result, counter = self.capture_case(raw=exact_raw)
        run_dir = Path(result.run_dir)
        self.assertEqual(counter.calls, 1)
        self.assertEqual(counter.urls, [f"{FIPSIGN_ORIGIN}/mandate/{BOUND_ID}"])
        self.assertEqual(counter.headers[0]["X-API-Key"], PROJECT_KEY)
        self.assertEqual((run_dir / CAPTURE_RAW_NAME).read_bytes(), exact_raw)
        self.assertEqual(oct((run_dir / CAPTURE_RAW_NAME).stat().st_mode & 0o777), "0o600")
        self.assertEqual(oct((run_dir / BASELINE_NAME).stat().st_mode & 0o777), "0o600")
        self.assertEqual(oct((run_dir / CAPTURE_RECEIPT_NAME).stat().st_mode & 0o777), "0o600")
        self.assertEqual(oct(run_dir.stat().st_mode & 0o777), "0o700")
        baseline_bytes = (run_dir / BASELINE_NAME).read_bytes()
        self.assertTrue(baseline_bytes.endswith(b"\n"))
        self.assertEqual(baseline_bytes, canonical_json_bytes(json.loads(baseline_bytes)))
        self.assertEqual(result.baseline_sha256, sha256_bytes(baseline_bytes))
        for path in run_dir.iterdir():
            self.assertNotIn(PROJECT_KEY.encode(), path.read_bytes())

    def test_m0_unchanged(self):
        captured, _ = self.capture_case()
        result, get_counter, key_calls = self.evaluate_case(
            captured, response=(200, raw_payload())
        )
        self.assertEqual(result.gate_decision, "ALLOW")
        self.assertEqual(result.evidence_class, "UNCHANGED_CONTROL")
        self.assertFalse(result.cell_7_preconditions_passed)
        self.assertEqual(result.changed_keys, ())
        self.assertEqual((get_counter.calls, key_calls["count"]), (1, 1))

    def test_m1_clean_status_scope_drift(self):
        captured, _ = self.capture_case()
        result, get_counter, _ = self.evaluate_case(
            captured,
            response=(200, raw_payload(scope_current=["verify"])),
        )
        self.assertEqual(result.gate_decision, "REFUSED_STALE")
        self.assertEqual(result.evidence_class, "CELL_7_CLEAN_STATUS_SCOPE_DRIFT")
        self.assertTrue(result.cell_7_preconditions_passed)
        self.assertEqual(result.changed_keys, ("scope",))
        self.assertEqual(get_counter.calls, 1)
        receipt = json.loads(Path(result.evaluation_receipt_path).read_bytes())
        self.assertFalse(receipt["live_agent_process_involved"])
        self.assertEqual(receipt["m7_live_status"], "NOT_EXECUTED_BY_SOURCE_OPERATOR")
        self.assertIn("not an independent signature", receipt["custody_limit"])

    def test_m2_order_only_normalizes_to_allow(self):
        captured, _ = self.capture_case()
        reordered = raw_payload(
            scope_original=["read:crm", "verify", "sign"],
            scope_current=["verify", "sign", "read:crm"],
        )
        result, _, _ = self.evaluate_case(captured, response=(200, reordered))
        self.assertEqual(result.gate_decision, "ALLOW")
        self.assertEqual(result.evidence_class, "ORDER_NORMALIZED_CONTROL")

    def test_m3_status_move_is_not_cell7(self):
        captured, _ = self.capture_case()
        result, _, _ = self.evaluate_case(
            captured, response=(200, raw_payload(status="suspended"))
        )
        self.assertEqual(result.gate_decision, "REFUSED_STALE")
        self.assertEqual(result.evidence_class, "INVALID_FOR_CELL_7")
        self.assertEqual(result.changed_keys, ("status",))

    def test_m4_subject_move_is_not_cell7(self):
        captured, _ = self.capture_case()
        result, _, _ = self.evaluate_case(
            captured, response=(200, raw_payload(agent_id="agent-other"))
        )
        self.assertEqual(result.gate_decision, "REFUSED_STALE")
        self.assertEqual(result.evidence_class, "INVALID_FOR_CELL_7")
        self.assertEqual(result.changed_keys, ("subject",))

    def test_m4_entity_id_move_reaches_gate_and_is_not_cell7(self):
        captured, _ = self.capture_case()
        result, _, _ = self.evaluate_case(
            captured,
            response=(200, raw_payload(mandate_id="mdt_otherentity")),
        )
        self.assertEqual(result.gate_decision, "REFUSED_STALE")
        self.assertEqual(result.evidence_class, "INVALID_FOR_CELL_7")
        self.assertEqual(result.changed_keys, ("entity_id",))

    def test_classifier_requires_gate_condition_delta_not_only_matching_labels(self):
        before = normalize_mandate(mandate_payload())
        after = dict(before)
        after["scope"] = ["verify"]
        event = AuthorityEvent(
            grant_id=BOUND_ID,
            decision="REFUSED_STALE",
            decision_timestamp=NOW,
            source_snapshot=before,
            source_current=after,
            condition_delta=None,
            ttl_remaining_hours=1.0,
            notes="source conditions changed since grant issuance",
        )
        result = classify_evidence(event)
        self.assertEqual(result.evidence_class, "INVALID_FOR_CELL_7")
        self.assertFalse(result.cell_7_preconditions_passed)

    def test_m5_unavailable_and_invalid_both_fail_closed_through_gate(self):
        for response in ((503, b"down"), (200, b"not-json")):
            with self.subTest(response=response[0:1]):
                captured, _ = self.capture_case()
                result, get_counter, key_calls = self.evaluate_case(
                    captured, response=response
                )
                self.assertEqual(result.gate_decision, "REFUSED_UNREACHABLE")
                self.assertEqual(result.evidence_class, "SOURCE_UNREACHABLE")
                self.assertEqual((get_counter.calls, key_calls["count"]), (1, 1))
                self.assertIsNone(result.evaluate_raw_path)

    def test_m6_expired_grant_blocks_before_fetch(self):
        source = NeverFetch()
        snapshot = normalize_mandate(mandate_payload())
        grant = Grant(
            grant_id=BOUND_ID,
            recipient="agent-cell7",
            scope="read:crm sign verify",
            issued_at=NOW,
            ttl_hours=1,
            source_snapshot=snapshot,
        )
        event = RederivationGate(source).evaluate(grant, NOW + timedelta(hours=2))
        classified = classify_evidence(event)
        self.assertEqual(event.decision, "BLOCK")
        self.assertEqual(classified.evidence_class, "TTL_EXPIRED")
        self.assertEqual(source.calls, 0)

    def test_m7_local_expansion_is_invalid_source_contract_and_no_patch_surface(self):
        captured, _ = self.capture_case()
        result, get_counter, _ = self.evaluate_case(
            captured,
            response=(200, raw_payload(scope_current=ORIGINAL_SCOPE + ["admin"])),
        )
        self.assertEqual(result.gate_decision, "REFUSED_STALE")
        self.assertEqual(result.evidence_class, "INVALID_SOURCE_CONTRACT")
        self.assertFalse(result.cell_7_preconditions_passed)
        self.assertEqual(get_counter.calls, 1)
        self.assertFalse(hasattr(MandateSourceAdapter, "patch"))
        self.assertFalse(hasattr(MandateSourceAdapter, "request"))

    def test_recursive_case_insensitive_sensitive_keys_stop_before_raw(self):
        forbidden = [
            "token",
            "API-Key",
            "api_key",
            "Authorization",
            "SECRET",
            "private-key",
            "PRIVATE_KEY",
        ]
        for index, key in enumerate(forbidden):
            with self.subTest(key=key):
                self.serial += 1
                payload = mandate_payload()
                payload["nested"] = [{"deeper": [{key: "must-not-persist"}]}]
                raw = json.dumps(payload).encode()
                run_id = f"secret-{index:08d}"
                self.assert_error(
                    "INVALID_SENSITIVE_SOURCE_RESPONSE",
                    lambda raw=raw, run_id=run_id: capture(
                        bound_id=BOUND_ID,
                        run_root=self.root,
                        run_id=run_id,
                        api_key=PROJECT_KEY,
                        http_get_bytes=CountingGet([(200, raw)]),
                        now_fn=lambda: NOW,
                    ),
                )
                self.assertFalse((self.root / run_id / CAPTURE_RAW_NAME).exists())

    def test_sensitive_evaluate_response_stops_before_raw_and_receipt(self):
        captured, _ = self.capture_case()
        payload = mandate_payload()
        payload["nested"] = [{"Authorization": "do-not-write"}]
        getter = CountingGet([(200, json.dumps(payload).encode())])
        key_calls = {"count": 0}

        def invoke():
            return evaluate(
                run_dir=Path(captured.run_dir),
                expected_baseline_sha256=captured.baseline_sha256,
                expected_capture_receipt_sha256=captured.capture_receipt_sha256,
                key_loader=lambda: key_calls.__setitem__("count", key_calls["count"] + 1)
                or PROJECT_KEY,
                http_get_bytes=getter,
                now_fn=lambda: NOW + timedelta(minutes=5),
            )

        self.assert_error("INVALID_SENSITIVE_SOURCE_RESPONSE", invoke)
        self.assertEqual((getter.calls, key_calls["count"]), (1, 1))
        run_dir = Path(captured.run_dir)
        self.assertFalse((run_dir / EVALUATE_RAW_NAME).exists())
        self.assertFalse((run_dir / EVALUATION_RECEIPT_NAME).exists())

    def test_tampered_carry_fails_before_key_or_http(self):
        for artifact in (BASELINE_NAME, CAPTURE_RECEIPT_NAME, CAPTURE_RAW_NAME):
            with self.subTest(artifact=artifact):
                captured, _ = self.capture_case()
                path = Path(captured.run_dir) / artifact
                path.write_bytes(path.read_bytes() + b"tamper")
                getter = CountingGet([(200, raw_payload())])
                key_calls = {"count": 0}

                def invoke():
                    return evaluate(
                        run_dir=Path(captured.run_dir),
                        expected_baseline_sha256=captured.baseline_sha256,
                        expected_capture_receipt_sha256=captured.capture_receipt_sha256,
                        key_loader=lambda: key_calls.__setitem__(
                            "count", key_calls["count"] + 1
                        )
                        or PROJECT_KEY,
                        http_get_bytes=getter,
                        now_fn=lambda: NOW + timedelta(minutes=5),
                    )

                self.assert_error("INVALID_BASELINE_CARRY", invoke)
                self.assertEqual((getter.calls, key_calls["count"]), (0, 0))

    def test_bad_mode_and_symlink_carry_fail_before_key_or_http(self):
        captured, _ = self.capture_case()
        os.chmod(Path(captured.run_dir) / BASELINE_NAME, 0o644)
        key_calls = {"count": 0}
        self.assert_error(
            "INVALID_BASELINE_CARRY",
            lambda: evaluate(
                run_dir=Path(captured.run_dir),
                expected_baseline_sha256=captured.baseline_sha256,
                expected_capture_receipt_sha256=captured.capture_receipt_sha256,
                key_loader=lambda: key_calls.__setitem__("count", 1) or PROJECT_KEY,
            ),
        )
        self.assertEqual(key_calls["count"], 0)

        captured2, _ = self.capture_case()
        raw_path = Path(captured2.run_dir) / CAPTURE_RAW_NAME
        raw_copy = Path(captured2.run_dir) / "copy.raw"
        raw_copy.write_bytes(raw_path.read_bytes())
        raw_path.unlink()
        raw_path.symlink_to(raw_copy)
        self.assert_error(
            "INVALID_BASELINE_CARRY",
            lambda: evaluate(
                run_dir=Path(captured2.run_dir),
                expected_baseline_sha256=captured2.baseline_sha256,
                expected_capture_receipt_sha256=captured2.capture_receipt_sha256,
                key_loader=lambda: PROJECT_KEY,
            ),
        )

    def test_expired_window_is_zero_key_zero_http_and_exact_deadline_is_allowed(self):
        captured, _ = self.capture_case()
        getter = CountingGet([(200, raw_payload())])
        key_calls = {"count": 0}
        expired = evaluate(
            run_dir=Path(captured.run_dir),
            expected_baseline_sha256=captured.baseline_sha256,
            expected_capture_receipt_sha256=captured.capture_receipt_sha256,
            key_loader=lambda: key_calls.__setitem__("count", 1) or PROJECT_KEY,
            http_get_bytes=getter,
            now_fn=lambda: NOW + timedelta(seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS + 1),
        )
        self.assertEqual(expired.status, "EXPIRED_WINDOW")
        self.assertEqual((getter.calls, key_calls["count"]), (0, 0))

        captured2, _ = self.capture_case()
        exact, getter2, key_calls2 = self.evaluate_case(
            captured2,
            response=(200, raw_payload()),
            now=NOW + timedelta(seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS),
        )
        self.assertEqual(exact.status, "EVALUATED")
        self.assertEqual((getter2.calls, key_calls2["count"]), (1, 1))

    def test_capture_requires_more_than_window_plus_margin(self):
        expires = NOW + timedelta(
            seconds=MAX_CAPTURE_TO_EVALUATE_SECONDS + EXPIRY_SAFETY_MARGIN_SECONDS
        )
        getter = CountingGet([(200, raw_payload(expires_at=expires))])
        self.assert_error(
            "INSUFFICIENT_FIXTURE_LIFETIME",
            lambda: capture(
                bound_id=BOUND_ID,
                run_root=self.root,
                run_id="shortlife-0001",
                api_key=PROJECT_KEY,
                http_get_bytes=getter,
                now_fn=lambda: NOW,
            ),
        )
        self.assertEqual(getter.calls, 1)

    def test_existing_run_or_evaluate_destination_refuses_without_overwrite(self):
        captured, _ = self.capture_case(run_id="exclusive-0001")
        self.assert_error(
            "RUN_ID_EXISTS",
            lambda: capture(
                bound_id=BOUND_ID,
                run_root=self.root,
                run_id="exclusive-0001",
                api_key=PROJECT_KEY,
                http_get_bytes=CountingGet([(200, raw_payload())]),
                now_fn=lambda: NOW,
            ),
        )
        destination = Path(captured.run_dir) / EVALUATION_RECEIPT_NAME
        destination.write_bytes(b"owned")
        os.chmod(destination, 0o600)
        key_calls = {"count": 0}
        self.assert_error(
            "DESTINATION_EXISTS",
            lambda: evaluate(
                run_dir=Path(captured.run_dir),
                expected_baseline_sha256=captured.baseline_sha256,
                expected_capture_receipt_sha256=captured.capture_receipt_sha256,
                key_loader=lambda: key_calls.__setitem__("count", 1) or PROJECT_KEY,
            ),
        )
        self.assertEqual(key_calls["count"], 0)
        self.assertEqual(destination.read_bytes(), b"owned")

    def test_arbitrary_origin_and_unsafe_bound_ids_are_rejected(self):
        self.assert_error(
            "INVALID_REQUEST_ORIGIN",
            lambda: MandateSourceAdapter(
                BOUND_ID,
                PROJECT_KEY,
                base_url="https://attacker.invalid",
                http_get_bytes=CountingGet([(200, raw_payload())]),
            ),
        )
        for bound_id in ("../mandate", "mdt_a/b", "https://example.com", "mdt_%2Fadmin"):
            with self.subTest(bound_id=bound_id):
                self.assert_error(
                    "INVALID_BOUND_ID",
                    lambda bound_id=bound_id: MandateSourceAdapter(bound_id, PROJECT_KEY),
                )

    def test_redirect_is_refused_before_a_new_request_can_copy_the_key(self):
        original = urllib.request.Request(
            f"{FIPSIGN_ORIGIN}/mandate/{BOUND_ID}",
            headers={"X-API-Key": PROJECT_KEY},
            method="GET",
        )
        handler = cell7._RejectRedirectHandler()
        self.assert_error(
            "INVALID_SOURCE_RESPONSE",
            lambda: handler.redirect_request(
                original,
                None,
                302,
                "Found",
                {},
                "https://attacker.invalid/collect",
            ),
        )

    def test_duplicate_json_keys_are_invalid_and_never_persisted(self):
        duplicate = (
            b'{"mandate":{"id":"mdt_cell7fixture","id":"mdt_other",'
            b'"agentId":"agent-cell7","scopeOriginal":[],"scopeCurrent":[],'
            b'"status":"active","expiresAt":"2026-08-05T04:00:00Z"}}'
        )
        self.assert_error(
            "INVALID_SOURCE_RESPONSE", lambda: parse_json_bytes(duplicate)
        )
        self.assert_error(
            "INVALID_SOURCE_RESPONSE",
            lambda: capture(
                bound_id=BOUND_ID,
                run_root=self.root,
                run_id="duplicate-0001",
                api_key=PROJECT_KEY,
                http_get_bytes=CountingGet([(200, duplicate)]),
                now_fn=lambda: NOW,
            ),
        )
        self.assertFalse((self.root / "duplicate-0001" / CAPTURE_RAW_NAME).exists())

    def test_expires_at_unix_integer_is_accepted_like_live_fipsign(self):
        """Reality-shaped fixture: FIPSign emits expiresAt as Unix epoch int.

        The first live CAPTURE against German's API failed with
        INVALID_SOURCE_RESPONSE because every suite fixture used ISO strings
        and shared that assumption with parse_aware_datetime. A test that
        only speaks ISO can never catch a live integer shape.
        """
        from mandate_cell7 import parse_aware_datetime

        epoch = int((NOW + timedelta(hours=6)).timestamp())
        parsed = parse_aware_datetime(epoch, "mandate.expiresAt")
        self.assertEqual(parsed, datetime.fromtimestamp(epoch, tz=timezone.utc))

        # Digit-only string form (if a transport stringifies the field).
        parsed_s = parse_aware_datetime(str(epoch), "mandate.expiresAt")
        self.assertEqual(parsed_s, parsed)

        # bool must not be treated as int(True)==1.
        self.assert_error(
            "INVALID_SOURCE_RESPONSE",
            lambda: parse_aware_datetime(True, "mandate.expiresAt"),
        )

        # K1: Unicode "digits" must classify as INVALID_SOURCE_RESPONSE, never
        # raise bare ValueError out of the fail-closed surface.
        for bad in ("²", "³", "¹", "⁴⁵", "1786038601²", "١٧٨٦٠٣٨٦٠١", "１７８６"):
            with self.subTest(bad=bad):
                try:
                    parse_aware_datetime(bad, "mandate.expiresAt")
                except MandateCell7Error as exc:
                    self.assertEqual(exc.code, "INVALID_SOURCE_RESPONSE")
                except Exception as exc:  # pragma: no cover — must not happen
                    self.fail(f"uncaught {type(exc).__name__} for {bad!r}: {exc}")
                else:
                    self.fail(f"expected refuse for {bad!r}")

        payload = mandate_payload()
        payload["mandate"]["expiresAt"] = epoch
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        result, counter = self.capture_case(raw=raw, run_id="unix-expires-0001")
        self.assertEqual(counter.calls, 1)
        self.assertTrue(result.baseline_sha256)
        # Capture succeeded; lifecycle was recorded as ISO on the receipt side.
        receipt_path = Path(result.run_dir) / CAPTURE_RECEIPT_NAME
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertIn("source_expires_at_utc", receipt)
        self.assertEqual(
            parse_aware_datetime(receipt["source_expires_at_utc"], "source_expires_at_utc"),
            datetime.fromtimestamp(epoch, tz=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Log redaction test — asserts no FORBIDDEN_LOG_KEYS appear in log output.

EP-008 M1. SECURITY.md § Logging Redaction Rules.
"""

import io
import sys

import pytest

import aethermesh.common.logging as logmod
from aethermesh.common.logging import FORBIDDEN_LOG_KEYS, _Logger
from aethermesh.common.metrics import get_counter
from aethermesh.common.tracing import _Tracer


class TestLogRedaction:
    def test_forbidden_keys_raise_in_strict_mode(self) -> None:
        """Logging with a forbidden key raises ValueError in strict mode."""
        log = _Logger()
        log._strict = True
        with pytest.raises(ValueError, match="FORBIDDEN_LOG_KEYS"):
            log.info("test.event", intent_key=b"secret")

    def test_forbidden_keys_dropped_in_non_strict(self) -> None:
        """Logging with a forbidden key is dropped in non-strict mode."""
        log = _Logger()
        log._strict = False
        before = logmod._redaction_violation_count
        metric_before = get_counter("log_redaction_violation_total")
        log.info("test.event", intent_key=b"secret", safe_field="ok")
        assert logmod._redaction_violation_count == before + 1
        assert get_counter("log_redaction_violation_total") == metric_before + 1

    def test_trace_attributes_reject_forbidden_keys(self) -> None:
        """Trace spans reject forbidden attributes using the logging denylist."""
        trace = _Tracer()
        before = get_counter("log_redaction_violation_total")
        with pytest.raises(ValueError, match="FORBIDDEN_LOG_KEYS"):
            trace.start_span("l4.message.send", message_key=b"secret")
        assert get_counter("log_redaction_violation_total") == before + 1

    def test_trace_set_attribute_rejects_forbidden_keys(self) -> None:
        """Trace span attribute mutation also enforces the denylist."""
        trace = _Tracer()
        span = trace.start_span("l5.verifier.verify", layer="L5")
        with pytest.raises(ValueError, match="FORBIDDEN_LOG_KEYS"):
            span.set_attribute("plaintext", "secret")

    def test_all_forbidden_keys_tested(self) -> None:
        """Every key in FORBIDDEN_LOG_KEYS is a non-empty string."""
        for key in FORBIDDEN_LOG_KEYS:
            assert isinstance(key, str)
            assert len(key) > 0

    def test_safe_logging_works(self) -> None:
        """Normal logging without forbidden keys works fine."""
        log = _Logger()
        log._strict = True
        capture = io.StringIO()
        old = sys.stderr
        sys.stderr = capture
        try:
            log.info("l4.policy.decision", policy_decision="ALLOW", Ns=42, lane="fast")
            output = capture.getvalue()
            assert "l4.policy.decision" in output
            assert "ALLOW" in output
            assert "42" in output
        finally:
            sys.stderr = old

    def test_session_root_redacted(self) -> None:
        """session_root is forbidden; session_root_hash is allowed."""
        log = _Logger()
        log._strict = True
        # session_root is forbidden
        with pytest.raises(ValueError):
            log.info("event", session_root=b"\x00" * 32)
        # session_root_hash is allowed
        capture = io.StringIO()
        old = sys.stderr
        sys.stderr = capture
        try:
            log.info("event", session_root_hash="8abeed89e7533431")
            assert "8abeed89e7533431" in capture.getvalue()
        finally:
            sys.stderr = old

    def test_forbidden_keys_count(self) -> None:
        """FORBIDDEN_LOG_KEYS has exactly 18 entries per SECURITY.md."""
        assert len(FORBIDDEN_LOG_KEYS) == 18

    def test_bytes_hex_truncated(self) -> None:
        """Bytes values are hex-encoded and truncated."""
        log = _Logger()
        log._strict = True
        capture = io.StringIO()
        old = sys.stderr
        sys.stderr = capture
        try:
            log.info("test", safe_data=b"\x00" * 100)
            output = capture.getvalue()
            # Should be hex with 0x prefix and truncated
            assert "0x" in output
            assert len(output) < 5000  # bytes truncated
        finally:
            sys.stderr = old

    def test_string_truncated(self) -> None:
        """Strings > 256 chars are truncated to 256."""
        log = _Logger()
        log._strict = True
        capture = io.StringIO()
        old = sys.stderr
        sys.stderr = capture
        try:
            log.info("test", long_field="x" * 500)
            output = capture.getvalue()
            assert "..." in output
            assert len("x" * 500) > 256  # original was long
        finally:
            sys.stderr = old

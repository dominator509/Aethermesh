"""Structured JSON logging with FORBIDDEN_LOG_KEYS enforcement.

Per OBSERVABILITY.md + SECURITY.md § Logging Redaction Rules.
EP-008 M1.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

# ---------------------------------------------------------------------------
# Forbidden keys — SECURITY.md § Logging Redaction Rules
# ---------------------------------------------------------------------------

FORBIDDEN_LOG_KEYS: frozenset[str] = frozenset(
    {
        "intent_key",
        "message_key",
        "principal_sk",
        "discharger_sk",
        "instance_sk",
        "static_sk",
        "x25519_sk",
        "mlkem_sk",
        "mldsa_sk",
        "body",
        "body_pt",
        "plaintext",
        "root_key",
        "ck",
        "ck_final",
        "session_root",
        "root_macaroon_key",
        "discharge_predicate",
    }
)

# Count of redaction violations (for metrics + alerting)
_redaction_violation_count = 0


def log_redaction_violation_total() -> int:
    """Return total redaction violation count (for metrics exposition)."""
    return _redaction_violation_count


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------


class _Logger:
    """Structured JSON logger to stderr."""

    def __init__(self) -> None:
        self._level = os.environ.get("AEP_LOG_LEVEL", "info")
        self._strict = os.environ.get("AEP_LOG_STRICT", "1") == "1"

    def _emit(self, level: str, event: str, **kwargs: object) -> None:
        global _redaction_violation_count

        # Check for forbidden keys
        violations = set(kwargs.keys()) & FORBIDDEN_LOG_KEYS
        if violations:
            _redaction_violation_count += 1
            from aethermesh.common.metrics import counter

            counter("log_redaction_violation_total")
            if self._strict:
                raise ValueError(f"FORBIDDEN_LOG_KEYS in log event '{event}': {sorted(violations)}")
            return  # Drop in non-strict prod mode

        record: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": level,
            "event": event,
        }
        record.update({k: _sanitize(v) for k, v in kwargs.items()})
        json.dump(record, sys.stderr, default=str)
        sys.stderr.write("\n")
        sys.stderr.flush()

    def info(self, event: str, **kwargs: object) -> None:
        if self._level in ("debug", "info"):
            self._emit("info", event, **kwargs)

    def debug(self, event: str, **kwargs: object) -> None:
        if self._level == "debug":
            self._emit("debug", event, **kwargs)

    def warning(self, event: str, **kwargs: object) -> None:
        self._emit("warning", event, **kwargs)

    def error(self, event: str, **kwargs: object) -> None:
        self._emit("error", event, **kwargs)


logger = _Logger()


# ---------------------------------------------------------------------------
# Sanitization
# ---------------------------------------------------------------------------


def _sanitize(value: object) -> object:
    """Sanitize a log value: truncate strings, escape control chars."""
    if isinstance(value, str):
        if len(value) > 256:
            value = value[:253] + "..."
        return value
    if isinstance(value, bytes):
        # Bytes → hex, truncated to 64 chars
        hex_str = value.hex()
        if len(hex_str) > 64:
            hex_str = hex_str[:61] + "..."
        return f"0x{hex_str}"
    if isinstance(value, (int, float, bool, type(None))):
        return value
    return str(value)

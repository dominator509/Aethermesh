"""OpenTelemetry tracing stub — span management with redaction.

Per OBSERVABILITY.md + SPEC-007. EP-008 M3.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any

from aethermesh.common.logging import FORBIDDEN_LOG_KEYS
from aethermesh.common.metrics import counter


class _Tracer:
    """Stub OpenTelemetry tracer with span management.

    Lazy OTLP exporter setup based on AEP_OTEL_ENDPOINT.
    Same FORBIDDEN_LOG_KEYS redaction as logging.
    """

    def __init__(self) -> None:
        self._endpoint = os.environ.get("AEP_OTEL_ENDPOINT", "")
        self._spans: list[dict[str, Any]] = []  # in-memory for testing

    def start_span(self, name: str, **attributes: object) -> _SpanContext:
        _reject_forbidden_attributes(name, attributes)
        return _SpanContext(self, name, attributes)

    @contextmanager
    def span(self, name: str, **attributes: object):  # type: ignore[no-untyped-def]
        ctx = self.start_span(name, **attributes)
        try:
            yield ctx
        except Exception:
            ctx.set_status("error")
            raise
        finally:
            ctx.end()


tracer = _Tracer()


class _SpanContext:
    def __init__(self, parent: _Tracer, name: str, attributes: dict[str, object]) -> None:
        self._parent = parent
        self._name = name
        self._attributes = dict(attributes)
        self._start = time.monotonic()
        self._status = "ok"
        self._ended = False

    def set_attribute(self, key: str, value: object) -> None:
        _reject_forbidden_attributes(self._name, {key: value})
        self._attributes[key] = value

    def set_status(self, status: str) -> None:
        self._status = status

    def end(self) -> None:
        if self._ended:
            return
        self._ended = True
        duration = time.monotonic() - self._start
        span_record = {
            "name": self._name,
            "attributes": self._attributes,
            "duration_s": round(duration, 6),
            "status": self._status,
        }
        self._parent._spans.append(span_record)


def _reject_forbidden_attributes(span_name: str, attributes: dict[str, object]) -> None:
    """Reject trace attributes using the same denylist as structured logging."""
    violations = set(attributes) & FORBIDDEN_LOG_KEYS
    if violations:
        counter("log_redaction_violation_total")
        raise ValueError(f"FORBIDDEN_LOG_KEYS in trace span '{span_name}': {sorted(violations)}")

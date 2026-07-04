"""Metrics REGISTRY and counter/histogram wrappers.

Per OBSERVABILITY.md Metrics section. EP-008 M2.
"""

from __future__ import annotations

import threading

# ---------------------------------------------------------------------------
# Metric type enum
# ---------------------------------------------------------------------------


class MetricType:
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


# ---------------------------------------------------------------------------
# Metric definition
# ---------------------------------------------------------------------------


class _Metric:
    def __init__(self, name: str, mtype: str, labels: tuple[str, ...], description: str) -> None:
        self.name = name
        self.mtype = mtype
        self.labels = labels
        self.description = description


# ---------------------------------------------------------------------------
# In-process metric storage
# ---------------------------------------------------------------------------


class _Counter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._values: dict[tuple[tuple[str, str], ...], int] = {}

    def inc(self, labels: dict[str, str] | None = None, value: int = 1) -> None:
        key = _label_key(labels or {})
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def get(self, labels: dict[str, str] | None = None) -> int:
        key = _label_key(labels or {})
        with self._lock:
            return self._values.get(key, 0)

    def snapshot(self) -> dict[tuple[tuple[str, str], ...], int]:
        with self._lock:
            return dict(self._values)


class _Gauge:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._values: dict[tuple[tuple[str, str], ...], float] = {}

    def set(self, value: float, labels: dict[str, str] | None = None) -> None:
        key = _label_key(labels or {})
        with self._lock:
            self._values[key] = value

    def get(self, labels: dict[str, str] | None = None) -> float:
        key = _label_key(labels or {})
        with self._lock:
            return self._values.get(key, 0.0)

    def snapshot(self) -> dict[tuple[tuple[str, str], ...], float]:
        with self._lock:
            return dict(self._values)


class _Histogram:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._values: dict[tuple[tuple[str, str], ...], list[float]] = {}

    def observe(self, value: float, labels: dict[str, str] | None = None) -> None:
        key = _label_key(labels or {})
        with self._lock:
            if key not in self._values:
                self._values[key] = []
            self._values[key].append(value)

    def snapshot(self) -> dict[tuple[tuple[str, str], ...], list[float]]:
        with self._lock:
            return {k: list(v) for k, v in self._values.items()}


def _label_key(labels: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(labels.items()))


# ---------------------------------------------------------------------------
# REGISTRY — every OBSERVABILITY.md metric
# ---------------------------------------------------------------------------

REGISTRY: dict[str, _Metric] = {}
_INSTANCES: dict[str, _Counter | _Gauge | _Histogram] = {}


def _register(
    name: str,
    mtype: str,
    labels: tuple[str, ...],
    description: str,
) -> _Metric:
    m = _Metric(name, mtype, labels, description)
    REGISTRY[name] = m
    if mtype == MetricType.COUNTER:
        _INSTANCES[name] = _Counter()
    elif mtype == MetricType.GAUGE:
        _INSTANCES[name] = _Gauge()
    elif mtype == MetricType.HISTOGRAM:
        _INSTANCES[name] = _Histogram()
    return m


# Per OBSERVABILITY.md Metrics table
_register("aep_l1_packets_total", MetricType.COUNTER, ("type", "lane"), "Sphinx packets emitted")
_register("aep_l1_lane_latency_seconds", MetricType.HISTOGRAM, ("lane",), "End-to-end latency")
_register(
    "aep_l1_sphinx_replay_rejections_total", MetricType.COUNTER, ("node_role",), "Replay cache hits"
)
_register(
    "aep_l2_dht_records_stored_total", MetricType.GAUGE, ("node_role",), "Current STORE count"
)
_register("aep_l2_dht_lookups_total", MetricType.COUNTER, ("result",), "Lookup outcomes")
_register("aep_l3_handshake_duration_seconds", MetricType.HISTOGRAM, ("result",), "3-msg handshake")
_register(
    "aep_l3_attestation_verifications_total",
    MetricType.COUNTER,
    ("backend", "result"),
    "Per-backend",
)
_register("aep_l4_messages_total", MetricType.COUNTER, ("kind",), "Frames processed")
_register(
    "aep_l4_policy_decisions_total", MetricType.COUNTER, ("decision",), "One per IntentHeader"
)
_register("aep_l4_ratchet_dh_steps_total", MetricType.COUNTER, (), "DH ratchet steps")
_register(
    "aep_l5_token_verify_duration_seconds", MetricType.HISTOGRAM, (), "Per-token verification"
)
_register(
    "aep_l5_discharge_issuances_total", MetricType.COUNTER, ("user_consent",), "Keyring discharges"
)
_register(
    "aep_l5_revocation_manifest_age_seconds", MetricType.GAUGE, ("issuer_did_hash",), "Manifest age"
)
_register("log_redaction_violation_total", MetricType.COUNTER, (), "Forbidden-key insertions")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def counter(name: str, labels: dict[str, str] | None = None, value: int = 1) -> None:
    """Increment a counter metric by *value*."""
    inst = _INSTANCES.get(name)
    if isinstance(inst, _Counter):
        inst.inc(labels, value)


def gauge(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Set a gauge metric to *value*."""
    inst = _INSTANCES.get(name)
    if isinstance(inst, _Gauge):
        inst.set(value, labels)


def histogram(name: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Observe a value on a histogram metric."""
    inst = _INSTANCES.get(name)
    if isinstance(inst, _Histogram):
        inst.observe(value, labels)


def get_counter(name: str, labels: dict[str, str] | None = None) -> int:
    inst = _INSTANCES.get(name)
    if isinstance(inst, _Counter):
        return inst.get(labels)
    return 0


def get_gauge(name: str, labels: dict[str, str] | None = None) -> float:
    inst = _INSTANCES.get(name)
    if isinstance(inst, _Gauge):
        return inst.get(labels)
    return 0.0


def all_metrics() -> dict[str, _Metric]:
    return dict(REGISTRY)


def snapshot(name: str) -> dict | None:  # type: ignore[type-arg]
    inst = _INSTANCES.get(name)
    if inst is not None:
        return inst.snapshot()
    return None

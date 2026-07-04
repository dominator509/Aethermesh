"""Metrics registry test — every OBSERVABILITY.md metric registered.

EP-008 M2.
"""

from aethermesh.common.metrics import (
    REGISTRY,
    all_metrics,
    counter,
    gauge,
    get_counter,
    get_gauge,
    histogram,
    snapshot,
)

REQUIRED_METRICS = {
    "aep_l1_packets_total",
    "aep_l1_lane_latency_seconds",
    "aep_l1_sphinx_replay_rejections_total",
    "aep_l2_dht_records_stored_total",
    "aep_l2_dht_lookups_total",
    "aep_l3_handshake_duration_seconds",
    "aep_l3_attestation_verifications_total",
    "aep_l4_messages_total",
    "aep_l4_policy_decisions_total",
    "aep_l4_ratchet_dh_steps_total",
    "aep_l5_token_verify_duration_seconds",
    "aep_l5_discharge_issuances_total",
    "aep_l5_revocation_manifest_age_seconds",
    "log_redaction_violation_total",
}


class TestMetricsRegistry:
    def test_all_required_metrics_registered(self) -> None:
        registered = set(REGISTRY.keys())
        missing = REQUIRED_METRICS - registered
        assert not missing, f"Missing metrics: {missing}"

    def test_no_extra_metrics(self) -> None:
        registered = set(REGISTRY.keys())
        extra = registered - REQUIRED_METRICS
        assert not extra, f"Unexpected metrics: {extra}"

    def test_counter_increment(self) -> None:
        counter("aep_l1_packets_total", {"type": "sphinx", "lane": "fast"}, value=3)
        val = get_counter("aep_l1_packets_total", {"type": "sphinx", "lane": "fast"})
        assert val == 3

    def test_counter_label_isolation(self) -> None:
        counter("aep_l1_packets_total", {"type": "sphinx", "lane": "fast"}, value=1)
        counter("aep_l1_packets_total", {"type": "cover", "lane": "slow"}, value=5)
        assert get_counter(
            "aep_l1_packets_total", {"type": "sphinx", "lane": "fast"}
        ) != get_counter("aep_l1_packets_total", {"type": "cover", "lane": "slow"})

    def test_gauge_set(self) -> None:
        gauge("aep_l2_dht_records_stored_total", 42.0, {"node_role": "dht-node"})
        val = get_gauge("aep_l2_dht_records_stored_total", {"node_role": "dht-node"})
        assert val == 42.0

    def test_histogram_observe(self) -> None:
        histogram("aep_l3_handshake_duration_seconds", 0.25, {"result": "success"})
        histogram("aep_l3_handshake_duration_seconds", 0.35, {"result": "success"})
        data = snapshot("aep_l3_handshake_duration_seconds")
        assert data is not None

    def test_snapshot_empty_metric(self) -> None:
        data = snapshot("log_redaction_violation_total")
        assert data is not None

    def test_all_metrics_returns_copy(self) -> None:
        m1 = all_metrics()
        m2 = all_metrics()
        assert m1 is not m2
        assert m1 == m2

    def test_nonexistent_metric(self) -> None:
        assert get_counter("nonexistent") == 0
        assert get_gauge("nonexistent") == 0.0
        data = snapshot("nonexistent")
        assert data is None

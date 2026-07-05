"""Shared benchmark assertions for EP-010 M4."""

from __future__ import annotations

import math

from pytest_benchmark.fixture import BenchmarkFixture


def percentile_seconds(samples: list[float], percentile: float) -> float:
    """Return the nearest-rank percentile from per-round durations in seconds."""
    if not samples:
        raise AssertionError("benchmark produced no timing samples")
    if percentile <= 0 or percentile > 1:
        raise ValueError(f"percentile must be in (0, 1], got {percentile}")

    ordered = sorted(samples)
    rank = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[rank]


def assert_p95_under_ms(
    benchmark: BenchmarkFixture,
    *,
    budget_ms: float,
) -> None:
    """Assert that the measured p95 latency is within the millisecond budget."""
    metadata = benchmark.stats
    assert metadata is not None, "benchmark metadata was not recorded"
    observed_ms = percentile_seconds(metadata.stats.data, 0.95) * 1000.0
    benchmark.extra_info["budget_p95_ms"] = budget_ms
    benchmark.extra_info["observed_p95_ms"] = round(observed_ms, 6)
    assert observed_ms <= budget_ms, f"p95 {observed_ms:.6f} ms exceeded {budget_ms:.3f} ms"


def assert_p99_under_us(
    benchmark: BenchmarkFixture,
    *,
    budget_us: float,
) -> None:
    """Assert that the measured p99 latency is within the microsecond budget."""
    metadata = benchmark.stats
    assert metadata is not None, "benchmark metadata was not recorded"
    observed_us = percentile_seconds(metadata.stats.data, 0.99) * 1_000_000.0
    benchmark.extra_info["budget_p99_us"] = budget_us
    benchmark.extra_info["observed_p99_us"] = round(observed_us, 6)
    assert observed_us <= budget_us, f"p99 {observed_us:.6f} us exceeded {budget_us:.3f} us"


def assert_min_ops(
    benchmark: BenchmarkFixture,
    *,
    minimum_ops: float,
) -> None:
    """Assert that operations-per-second meets the documented floor."""
    metadata = benchmark.stats
    assert metadata is not None, "benchmark metadata was not recorded"
    observed_ops = metadata.stats.ops
    benchmark.extra_info["budget_min_ops_per_sec"] = minimum_ops
    benchmark.extra_info["observed_ops_per_sec"] = round(observed_ops, 6)
    assert observed_ops >= minimum_ops, (
        f"throughput {observed_ops:.6f} ops/s below required {minimum_ops:.3f} ops/s"
    )

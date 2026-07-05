"""L4 perf budget checks for EP-010 M4."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from aethermesh.api import PairRatchet
from tests.perf.helpers import assert_min_ops


@pytest.mark.perf
def test_l4_non_dh_step_ops(
    benchmark: BenchmarkFixture,
    l4_non_dh_case: tuple[PairRatchet, bytes, bytes, bytes],
    perf_results_dir: Path,
) -> None:
    """The current non-DH L4 message path stays above the throughput floor."""
    ratchet, intent_header, body, session_id = l4_non_dh_case
    assert perf_results_dir.exists()

    benchmark.extra_info["surface"] = "stub PairRatchet.encrypt(include_dh_pub=False)"
    benchmark.extra_info["signoff_note"] = "rerun against the real ratchet body once EP-006+ lands"
    message = benchmark.pedantic(  # type: ignore[no-untyped-call]
        ratchet.encrypt,
        args=(intent_header, body, session_id),
        kwargs={"include_dh_pub": False},
        rounds=512,
        iterations=1,
    )

    assert message.body == body
    assert_min_ops(benchmark, minimum_ops=200_000.0)

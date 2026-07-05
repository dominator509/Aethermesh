"""L1 perf budget checks for EP-010 M4.

The repository does not yet ship `aethermesh.L1_sphinx`. This benchmark measures
the current placeholder fast-lane contract only: fixed-size 2048-byte packet
validation, matching the existing fuzz target's placeholder surface.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from tests.perf.helpers import assert_p95_under_ms


@pytest.mark.perf
def test_l1_fast_lane_p95(
    benchmark: BenchmarkFixture,
    l1_fast_lane_case: tuple[Callable[[bytes], None], bytes],
    perf_results_dir: Path,
) -> None:
    """Current L1 placeholder contract stays under the documented p95 budget."""
    process_packet, packet = l1_fast_lane_case
    assert perf_results_dir.exists()

    benchmark.extra_info["surface"] = "placeholder fixed-size packet validation"
    benchmark.extra_info["signoff_note"] = "replace with aethermesh.L1_sphinx fast-lane path"
    benchmark.pedantic(  # type: ignore[no-untyped-call]
        process_packet,
        args=(packet,),
        rounds=256,
        iterations=1,
    )

    assert_p95_under_ms(benchmark, budget_ms=300.0)

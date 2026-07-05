"""L3 perf budget checks for EP-010 M4."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from aethermesh.api import SessionState
from tests.perf.helpers import assert_p95_under_ms


@pytest.mark.perf
def test_l3_handshake_p95(
    benchmark: BenchmarkFixture,
    l3_handshake_case: Callable[[], tuple[SessionState, SessionState]],
    perf_results_dir: Path,
) -> None:
    """The current L3 handshake facade stays under the documented p95 budget."""
    assert perf_results_dir.exists()

    benchmark.extra_info["surface"] = "stub HandshakeInitiator/HandshakeResponder facade"
    benchmark.extra_info["signoff_note"] = (
        "rerun against real Noise-PQ handshake on the reference VM"
    )
    alice_session, bob_session = benchmark.pedantic(  # type: ignore[no-untyped-call]
        l3_handshake_case,
        rounds=128,
        iterations=1,
    )

    assert len(alice_session.session_root) == 32
    assert len(bob_session.session_root) == 32
    assert_p95_under_ms(benchmark, budget_ms=550.0)

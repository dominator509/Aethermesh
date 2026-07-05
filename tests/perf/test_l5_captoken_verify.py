"""L5 perf budget checks for EP-010 M4."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from aethermesh.api import CapToken, Discharge
from aethermesh.common.did_resolver import DIDResolver
from aethermesh.common.errors import VerificationDecision
from aethermesh.L5_captokens.verifier import verify_token
from tests.perf.helpers import assert_p99_under_us


@pytest.mark.perf
def test_l5_verify_p99(
    benchmark: BenchmarkFixture,
    l5_verify_case: tuple[CapToken, dict[str, object], DIDResolver, list[Discharge]],
    perf_results_dir: Path,
) -> None:
    """CapToken verification stays within the documented p99 budget."""
    token, request, resolver, discharges = l5_verify_case
    assert perf_results_dir.exists()

    benchmark.extra_info["surface"] = "verify_token caveat and discharge evaluation path"
    benchmark.extra_info["signoff_note"] = (
        "rerun against release-candidate caveat mix on the reference VM"
    )
    decision, reason = benchmark.pedantic(  # type: ignore[no-untyped-call]
        verify_token,
        args=(token, request, resolver, discharges),
        rounds=512,
        iterations=1,
    )

    assert decision == VerificationDecision.ALLOW
    assert reason == "all caveats satisfied"
    assert_p99_under_us(benchmark, budget_us=300.0)

"""Shared test fixtures for AetherMesh."""

from collections.abc import Generator

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "quarantined(reason): mark test as quarantined per FLAKY_POLICY.md",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (interop, perf)",
    )


@pytest.fixture(scope="session")
def aethermesh_session() -> Generator[None, None, None]:
    """No-op session fixture — placeholder for future shared setup."""
    yield

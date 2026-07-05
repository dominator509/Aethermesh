"""Shared test fixtures for AetherMesh."""

from collections.abc import Generator

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register repo-standard test selection flags."""
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="run tests marked slow",
    )


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
    config.addinivalue_line(
        "markers",
        "perf: mark test as performance benchmark",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip slow tests unless the caller explicitly enables them."""
    if config.getoption("--slow"):
        return

    skip_slow = pytest.mark.skip(reason="need --slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def aethermesh_session() -> Generator[None, None, None]:
    """No-op session fixture — placeholder for future shared setup."""
    yield

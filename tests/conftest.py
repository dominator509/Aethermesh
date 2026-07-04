"""Shared test fixtures for AetherMesh."""

from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def aethermesh_session() -> Generator[None, None, None]:
    """No-op session fixture — placeholder for future shared setup."""
    yield

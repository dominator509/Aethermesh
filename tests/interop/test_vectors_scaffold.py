"""Interop scaffold tests for pinned TEST_ONLY vectors.

EP-007 M6. These tests verify vector loading and provide a collectable slow
interop surface until a second implementation is available.
"""

import pytest


@pytest.mark.slow
def test_sha3_vectors_load(sha3_vectors: list[dict[str, object]]) -> None:
    """Pinned vector fixture loads at least one TEST_ONLY case."""
    assert sha3_vectors
    assert {"length", "msg", "md"}.issubset(sha3_vectors[0])

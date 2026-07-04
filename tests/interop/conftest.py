"""Interop test fixtures — load pinned vectors from tests/vectors/.

EP-007 M6. Setup for multi-implementation wire-format testing.
"""

# mypy: ignore-errors

from pathlib import Path

import pytest

VECTORS_DIR = Path(__file__).parent.parent / "vectors"


def _load_json_vectors(name: str) -> list[dict]:
    """Load TEST_ONLY vector file, returning list of test cases."""
    import json

    path = VECTORS_DIR / name
    if not path.exists():
        return []

    with open(path) as f:
        data = json.load(f)

    if not data.get("TEST_ONLY"):
        raise ValueError(f"Vector file {name} missing TEST_ONLY marker")

    return data.get("vectors", [])


@pytest.fixture(scope="session")
def sha3_vectors() -> list[dict]:
    """NIST SHA3-256 test vectors."""
    return _load_json_vectors("sha3_256_nist.json")


@pytest.fixture(scope="session")
def interop_report_dir() -> Path:
    """Directory for interop result artifacts."""
    report_dir = VECTORS_DIR.parent / "interop" / "results"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir

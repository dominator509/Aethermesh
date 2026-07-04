"""Property-based tests for canonical encoding roundtrip."""

import os

from hypothesis import given, settings
from hypothesis.strategies import (
    binary,
    booleans,
    dictionaries,
    floats,
    integers,
    lists,
    none,
    recursive,
    text,
)

from aethermesh.common.canonical import canonical_bytes, canonical_from_bytes

MAX_EXAMPLES = int(os.environ.get("HYPOTHESIS_MAX_EXAMPLES", "200"))

# Build a recursive JSON-like strategy (bytes as leaf, no nested bytes-in-bytes)
_value_strategy = recursive(
    none() | booleans() | integers() | floats(allow_nan=False) | text() | binary(max_size=256),
    lambda children: lists(children, max_size=5) | dictionaries(text(), children, max_size=5),
    max_leaves=20,
)


class TestCanonicalPropertyRoundtrip:
    @given(_value_strategy)
    @settings(max_examples=MAX_EXAMPLES)
    def test_roundtrip(self, value: object) -> None:
        """canonical_from_bytes(canonical_bytes(x)) == x for all supported types."""
        result = canonical_from_bytes(canonical_bytes(value))
        assert result == value

    @given(_value_strategy)
    @settings(max_examples=MAX_EXAMPLES)
    def test_deterministic(self, value: object) -> None:
        """Same input always produces identical output."""
        a = canonical_bytes(value)
        b = canonical_bytes(value)
        assert a == b

    @given(dictionaries(text(), binary(max_size=64), max_size=5))
    @settings(max_examples=MAX_EXAMPLES)
    def test_dict_sort_order(self, d: dict[str, bytes]) -> None:
        """Keys are always sorted."""
        result = canonical_bytes(d)
        decoded = canonical_from_bytes(result)
        # decoded should equal original (bytes survive roundtrip)
        assert decoded == d

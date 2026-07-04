"""Tests for aethermesh.common.canonical — SPEC-001 § Required Behavior item 7."""

import pytest

from aethermesh.common.canonical import canonical_bytes, canonical_from_bytes


class TestCanonicalBytes:
    def test_null(self) -> None:
        assert canonical_bytes(None) == b"null"

    def test_bool(self) -> None:
        assert canonical_bytes(True) == b"true"
        assert canonical_bytes(False) == b"false"

    def test_int(self) -> None:
        assert canonical_bytes(42) == b"42"
        assert canonical_bytes(-1) == b"-1"

    def test_float(self) -> None:
        result = canonical_bytes(3.14)
        assert b"3.14" in result

    def test_str(self) -> None:
        assert canonical_bytes("hello") == b'"hello"'

    def test_hex_like_string_is_escaped(self) -> None:
        assert canonical_from_bytes(canonical_bytes("0xdeadbeef")) == "0xdeadbeef"
        assert canonical_from_bytes(canonical_bytes("0x")) == "0x"
        assert canonical_from_bytes(canonical_bytes("\\0xdeadbeef")) == "\\0xdeadbeef"

    def test_bytes_hex_encoded(self) -> None:
        result = canonical_bytes(b"\x00\xff\xab")
        assert b"0x00ffab" in result

    def test_empty_bytes(self) -> None:
        result = canonical_bytes(b"")
        assert b"0x" in result

    def test_list(self) -> None:
        result = canonical_bytes([1, 2, 3])
        assert result == b"[1,2,3]"

    def test_empty_list(self) -> None:
        assert canonical_bytes([]) == b"[]"

    def test_dict_sorted_keys(self) -> None:
        """Dict keys must be sorted for determinism."""
        result = canonical_bytes({"z": 1, "a": 2, "m": 3})
        # 'a' before 'm' before 'z'
        assert result == b'{"a":2,"m":3,"z":1}'

    def test_nested_dict(self) -> None:
        result = canonical_bytes({"outer": {"inner": 1}})
        assert result == b'{"outer":{"inner":1}}'

    def test_bytes_in_dict(self) -> None:
        result = canonical_bytes({"key": b"\x01\x02"})
        assert b"0x0102" in result

    def test_deterministic(self) -> None:
        """Same object always produces same bytes."""
        obj = {"b": [1, 2], "a": None, "c": {"nested": b"data"}}
        a = canonical_bytes(obj)
        b_result = canonical_bytes(obj)
        assert a == b_result

    def test_unsupported_type_raises(self) -> None:
        with pytest.raises(TypeError, match="unsupported type"):
            canonical_bytes({1 + 2j})  # type: ignore[arg-type, unused-ignore]


class TestCanonicalFromBytes:
    def test_roundtrip_null(self) -> None:
        assert canonical_from_bytes(canonical_bytes(None)) is None

    def test_roundtrip_int(self) -> None:
        assert canonical_from_bytes(canonical_bytes(42)) == 42

    def test_roundtrip_str(self) -> None:
        assert canonical_from_bytes(canonical_bytes("hello")) == "hello"

    def test_roundtrip_bytes(self) -> None:
        original = b"\x00\xff\xab\xcd"
        result = canonical_from_bytes(canonical_bytes(original))
        assert result == original

    def test_roundtrip_list(self) -> None:
        original = [1, "two", None, True]
        result = canonical_from_bytes(canonical_bytes(original))
        assert result == original

    def test_roundtrip_dict(self) -> None:
        original = {"key": b"val", "num": 42}
        result = canonical_from_bytes(canonical_bytes(original))
        assert result == {"key": b"val", "num": 42}

    def test_roundtrip_nested(self) -> None:
        original = {
            "outer": [
                {"inner_bytes": b"\x01\x02"},
                None,
                123,
            ]
        }
        result = canonical_from_bytes(canonical_bytes(original))
        assert result == original

    def test_plain_string_not_hex(self) -> None:
        """A plain string that was not encoded as bytes stays a string."""
        result = canonical_from_bytes(b'"normal_string"')
        assert result == "normal_string"

"""Tests for aethermesh.common.did_resolver — SPEC-001 § Required Behavior item 8."""

import pytest

from aethermesh.common.did_resolver import DIDResolver


class TestDidResolver:
    def test_register_and_resolve(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b'{"key":"value"}')
        assert r.resolve("did:web:example.org") == b'{"key":"value"}'

    def test_known_true(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b"doc")
        assert r.known("did:web:example.org") is True

    def test_known_false(self) -> None:
        r = DIDResolver()
        assert r.known("did:web:peer.example") is False

    def test_resolve_unknown_raises_keyerror(self) -> None:
        r = DIDResolver()
        with pytest.raises(KeyError):
            r.resolve("did:web:peer.example")

    def test_bump_revocation_epoch(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b"doc")
        assert r.revocation_epoch("did:web:example.org") == 0
        epoch = r.bump_revocation_epoch("did:web:example.org")
        assert epoch == 1
        assert r.revocation_epoch("did:web:example.org") == 1

    def test_bump_multiple_times(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b"doc")
        for i in range(1, 6):
            assert r.bump_revocation_epoch("did:web:example.org") == i

    def test_bump_unknown_raises_keyerror(self) -> None:
        r = DIDResolver()
        with pytest.raises(KeyError):
            r.bump_revocation_epoch("did:web:peer.example")

    def test_revocation_epoch_unknown_raises_keyerror(self) -> None:
        r = DIDResolver()
        with pytest.raises(KeyError):
            r.revocation_epoch("did:web:peer.example")

    def test_multiple_dids(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b"example")
        r.register("did:web:peer.example", b"peer")
        assert r.resolve("did:web:example.org") == b"example"
        assert r.resolve("did:web:peer.example") == b"peer"

    def test_register_duplicate_raises(self) -> None:
        r = DIDResolver()
        r.register("did:web:example.org", b"doc")
        with pytest.raises(ValueError, match="already registered"):
            r.register("did:web:example.org", b"other")

    def test_register_empty_did_raises(self) -> None:
        r = DIDResolver()
        with pytest.raises(ValueError, match="must not be empty"):
            r.register("", b"doc")

    def test_register_non_str_did_raises(self) -> None:
        r = DIDResolver()
        with pytest.raises(TypeError):
            r.register(123, b"doc")  # type: ignore[arg-type]

    def test_register_non_bytes_doc_raises(self) -> None:
        r = DIDResolver()
        with pytest.raises(TypeError):
            r.register("did:web:example.org", "not bytes")  # type: ignore[arg-type]

    def test_independent_epochs(self) -> None:
        """Bumping one DID's epoch does not affect another."""
        r = DIDResolver()
        r.register("did:web:example.org", b"example")
        r.register("did:web:peer.example", b"peer")
        r.bump_revocation_epoch("did:web:example.org")
        assert r.revocation_epoch("did:web:example.org") == 1
        assert r.revocation_epoch("did:web:peer.example") == 0

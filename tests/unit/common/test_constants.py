"""Tests for aethermesh.common.constants — value sanity checks."""

from aethermesh.common.constants import (
    ALLOWED_DID_PREFIXES,
    CHA_CHA20_POLY1305_KEY_BYTES,
    CHA_CHA20_POLY1305_NONCE_BYTES,
    COVER_BUDGET_KBIT_S,
    MLDSA65_PK_BYTES,
    MLDSA65_SIG_BYTES,
    MLDSA65_SK_BYTES,
    MLKEM768_CT_BYTES,
    MLKEM768_PK_BYTES,
    MLKEM768_SK_BYTES,
    MLKEM768_SS_BYTES,
    POLY1305_TAG_BYTES,
    REPLAY_CACHE_EPOCHS,
    SHA3_256_OUTPUT_BYTES,
    SPHINX_PACKET_SIZE,
    X25519_KEY_BYTES,
)


class TestConstants:
    def test_sphinx_packet_size(self) -> None:
        assert SPHINX_PACKET_SIZE == 2048

    def test_replay_cache_epochs(self) -> None:
        assert REPLAY_CACHE_EPOCHS == 2

    def test_mlkem768_sizes_match_pq_backend(self) -> None:
        """Constants must match pq_backend module sizes."""
        from aethermesh.common.pq_backend import (
            MLKEM768_CT_SIZE,
            MLKEM768_PK_SIZE,
            MLKEM768_SK_SIZE,
            MLKEM768_SS_SIZE,
        )

        assert MLKEM768_PK_BYTES == MLKEM768_PK_SIZE
        assert MLKEM768_SK_BYTES == MLKEM768_SK_SIZE
        assert MLKEM768_CT_BYTES == MLKEM768_CT_SIZE
        assert MLKEM768_SS_BYTES == MLKEM768_SS_SIZE

    def test_mldsa65_sizes_match_pq_backend(self) -> None:
        from aethermesh.common.pq_backend import (
            MLDSA65_PK_SIZE,
            MLDSA65_SIG_SIZE,
            MLDSA65_SK_SIZE,
        )

        assert MLDSA65_PK_BYTES == MLDSA65_PK_SIZE
        assert MLDSA65_SK_BYTES == MLDSA65_SK_SIZE
        assert MLDSA65_SIG_BYTES == MLDSA65_SIG_SIZE

    def test_sha3_256_output_size(self) -> None:
        assert SHA3_256_OUTPUT_BYTES == 32

    def test_x25519_key_size(self) -> None:
        assert X25519_KEY_BYTES == 32

    def test_chacha20_poly1305_key_size(self) -> None:
        assert CHA_CHA20_POLY1305_KEY_BYTES == 32

    def test_chacha20_poly1305_nonce_size(self) -> None:
        assert CHA_CHA20_POLY1305_NONCE_BYTES == 12

    def test_poly1305_tag_size(self) -> None:
        assert POLY1305_TAG_BYTES == 16

    def test_cover_budget(self) -> None:
        assert COVER_BUDGET_KBIT_S == 80

    def test_allowed_did_prefixes_match_agent_rules(self) -> None:
        assert ALLOWED_DID_PREFIXES == (
            "did:web:example.org",
            "did:web:peer.example",
            "did:web:org.example",
            "did:key:z6Mk-",
        )

    def test_constants_positive(self) -> None:
        """All sizes are positive integers."""
        constants = [
            SPHINX_PACKET_SIZE,
            REPLAY_CACHE_EPOCHS,
            MLKEM768_PK_BYTES,
            MLKEM768_SK_BYTES,
            MLKEM768_CT_BYTES,
            MLKEM768_SS_BYTES,
            MLDSA65_PK_BYTES,
            MLDSA65_SK_BYTES,
            MLDSA65_SIG_BYTES,
            SHA3_256_OUTPUT_BYTES,
            X25519_KEY_BYTES,
            CHA_CHA20_POLY1305_KEY_BYTES,
            CHA_CHA20_POLY1305_NONCE_BYTES,
            POLY1305_TAG_BYTES,
            COVER_BUDGET_KBIT_S,
        ]
        for c in constants:
            assert c > 0

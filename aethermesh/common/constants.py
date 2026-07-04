"""AetherMesh shared constants.

Sources: ARCHITECTURE.md, ENVIRONMENT.md, layer SPECs.
"""

# ---------------------------------------------------------------------------
# Sphinx / L1
# ---------------------------------------------------------------------------
SPHINX_PACKET_SIZE = 2048  # bytes — fixed-wire Sphinx packet

# ---------------------------------------------------------------------------
# Replay protection
# ---------------------------------------------------------------------------
REPLAY_CACHE_EPOCHS = 2  # replay caches keep 2 epochs deep (ARCH § Invariant 6)

# ---------------------------------------------------------------------------
# PQ KEM/SIG sizes (FIPS 203/204)
# ---------------------------------------------------------------------------
MLKEM768_PK_BYTES = 1184
MLKEM768_SK_BYTES = 2400
MLKEM768_CT_BYTES = 1088
MLKEM768_SS_BYTES = 32

MLDSA65_PK_BYTES = 1952
MLDSA65_SK_BYTES = 4032
MLDSA65_SIG_BYTES = 3309

# ---------------------------------------------------------------------------
# Crypto
# ---------------------------------------------------------------------------
SHA3_256_OUTPUT_BYTES = 32
X25519_KEY_BYTES = 32
CHA_CHA20_POLY1305_KEY_BYTES = 32
CHA_CHA20_POLY1305_NONCE_BYTES = 12
POLY1305_TAG_BYTES = 16

# ---------------------------------------------------------------------------
# Cover traffic (ARCH § Invariant 6 + ENVIRONMENT.md)
# ---------------------------------------------------------------------------
COVER_RATE_PPS_ACTIVE_DEFAULT = 5  # packets per second active
COVER_RATE_PPS_IDLE_DEFAULT = 1  # packets per second idle
COVER_BUDGET_KBIT_S = 80  # target constant-rate cover ~80 kbit/s

# ---------------------------------------------------------------------------
# DID prefixes (AGENTS.md § 6)
# ---------------------------------------------------------------------------
ALLOWED_DID_PREFIXES = (
    "did:web:example.org",
    "did:web:peer.example",
    "did:web:org.example",
    "did:key:z6Mk-",
)

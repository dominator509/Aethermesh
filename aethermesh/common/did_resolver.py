"""In-memory DID resolver with revocation-epoch tracking.

SPEC-001 § Required Behavior item 8.
"""


class DIDResolver:
    """In-memory DID → document resolver.

    Each DID has a document (bytes), a current revocation epoch, and optional metadata.
    """

    def __init__(self) -> None:
        self._docs: dict[str, bytes] = {}
        self._revocation_epochs: dict[str, int] = {}

    def register(self, did: str, document: bytes) -> None:
        """Register *did* with its *document*.

        Initial revocation epoch is 0.

        Raises:
            TypeError: If *did* is not a str or *document* is not bytes.
            ValueError: If *did* is empty or already registered.
        """
        if not isinstance(did, str):
            raise TypeError("did must be a str")
        if not isinstance(document, bytes):
            raise TypeError("document must be bytes")
        if not did:
            raise ValueError("did must not be empty")
        if did in self._docs:
            raise ValueError(f"did already registered: {did}")

        self._docs[did] = document
        self._revocation_epochs[did] = 0

    def resolve(self, did: str) -> bytes:
        """Return the document for *did*.

        Raises:
            KeyError: If *did* is not registered.
        """
        if did not in self._docs:
            raise KeyError(did)
        return self._docs[did]

    def known(self, did: str) -> bool:
        """Return True if *did* is registered."""
        return did in self._docs

    def bump_revocation_epoch(self, did: str) -> int:
        """Increment the revocation epoch for *did*.

        Returns the new epoch number.

        Raises:
            KeyError: If *did* is not registered.
        """
        if did not in self._revocation_epochs:
            raise KeyError(did)
        self._revocation_epochs[did] += 1
        return self._revocation_epochs[did]

    def revocation_epoch(self, did: str) -> int:
        """Return the current revocation epoch for *did*.

        Raises:
            KeyError: If *did* is not registered.
        """
        if did not in self._revocation_epochs:
            raise KeyError(did)
        return self._revocation_epochs[did]

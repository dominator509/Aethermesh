"""Hypothesis fuzz target for Sphinx packet parser.

EP-007 M3. Fuzzes binary inputs against Sphinx packet boundaries.
Since no Sphinx packet code exists yet (bundles absent, layers are stubs),
this fuzz target validates the contract that byte arrays are safe to process.

When aethermesh.L1_sphinx is implemented, replace the stub
with real SphinxPacket.from_wire / MixNode.process calls.
"""

from hypothesis import given, settings
from hypothesis.strategies import binary


def _safe_process_sphinx_packet(data: bytes) -> None:
    """Placeholder Sphinx packet processing — body lands with L1 impl.

    Accepts any bytes and either:
    - Decodes successfully (returns None — processed)
    - Raises ValueError (malformed)
    - Raises OverflowError (length exceeds max)

    Never crashes, hangs, or leaks.
    """
    if len(data) == 0:
        raise ValueError("empty packet")

    # Sphinx packets are fixed 2048 bytes on wire
    if len(data) != 2048:
        raise ValueError(f"expected 2048 bytes, got {len(data)}")

    # Placeholder: accept all valid-length inputs
    # Real impl: parse header, decrypt payload, verify MAC


class TestSphinxFuzz:
    @given(data=binary(min_size=0, max_size=2100))
    @settings(max_examples=200)
    def test_sphinx_never_crashes(self, data: bytes) -> None:
        """Any byte sequence either processes or raises typed error — never crashes."""
        try:
            _safe_process_sphinx_packet(data)
        except ValueError:
            pass  # expected: malformed
        except OverflowError:
            pass  # expected: too large
        # Any other exception is a bug

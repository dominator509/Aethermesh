"""Deterministic canonical encoding (JSON stand-in for CBOR).

SPEC-001 § Required Behavior item 7.
Uses sorted-key JSON encoding. Bytes are hex-encoded. Strings that would
collide with the byte marker are escaped before encoding.
"""

import json
from typing import Any


def canonical_bytes(obj: Any) -> bytes:
    """Serialize *obj* to deterministic bytes.

    Rules:
    - dict keys are sorted.
    - bytes values are hex-encoded as "0x<hex>".
    - strings starting with "0x" or "\\" are escaped with a leading "\\".
    - int, float, str, bool, None, list, dict are supported.
    - Output is UTF-8 JSON with no trailing newline.

    Raises:
        TypeError: If *obj* contains an unsupported type.
    """
    serialized = _serialize(obj)
    return json.dumps(serialized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def canonical_from_bytes(data: bytes) -> Any:
    """Deserialize *data* produced by canonical_bytes back to the original object.

    Hex-encoded bytes are decoded back to bytes.
    """
    raw = json.loads(data.decode("utf-8"))
    return _deserialize(raw)


def _serialize(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return obj
    if isinstance(obj, str):
        if obj.startswith((_HEX_PREFIX, _ESCAPE_PREFIX)):
            return _ESCAPE_PREFIX + obj
        return obj
    if isinstance(obj, bytes):
        return _HEX_PREFIX + obj.hex()
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    raise TypeError(f"canonical_bytes: unsupported type {type(obj).__name__}")


_HEX_PREFIX = "0x"
_ESCAPE_PREFIX = "\\"


def _deserialize(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return obj
    if isinstance(obj, list):
        return [_deserialize(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _deserialize(v) for k, v in obj.items()}
    if isinstance(obj, str):
        if obj.startswith(_ESCAPE_PREFIX):
            return obj[1:]
        if obj.startswith(_HEX_PREFIX):
            return bytes.fromhex(obj[2:])
        return obj
    return obj

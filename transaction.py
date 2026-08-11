"""
Transaction serialization and ID.

You MUST use a deterministic JSON-based format exactly as described in
the assignment instructions:

- Recursively sort dict keys (lists keep their order).
- Use json.dumps(..., sort_keys=True, separators=(",", ":")).
- Encode the resulting string as UTF-8 bytes.

Do NOT invent your own format; the autograder expects this one.
"""

import json
import copy
from crypto import hash256


def canonical_serialize(
    tx: dict,
    substitute_input_index: int | None = None,
    substitute_script: list | None = None,
) -> bytes:
    """
    Serialize tx to bytes deterministically using the canonical JSON format.

    If substitute_input_index is not None, you must create a copy of tx where
    that input's script_sig is replaced by substitute_script (for the signing
    message). Then:
      - Recursively sort dict keys (but do NOT reorder lists).
      - Call json.dumps(..., sort_keys=True, separators=(",", ":")).
      - Return the resulting UTF-8 encoded bytes.
    """
    # TODO: implement as specified in the assignment instructions
    tx_copy = copy.deepcopy(tx)

    if substitute_input_index is not None:
        tx_copy["inputs"][substitute_input_index]["script_sig"] = substitute_script

    serialized = json.dumps(
        tx_copy,
        sort_keys=True,
        separators=("," , ":")
    )

    return serialized.encode("utf-8")
    # raise NotImplementedError


def tx_id(tx: dict) -> str:
    """
    Return transaction ID as a hex string:
        tx_id = hash256(canonical_serialize(tx)).hex()
    """
    # TODO: implement using canonical_serialize(tx) and hash256
    return hash256(canonical_serialize(tx)).hex()


def get_signing_message(tx: dict, input_index: int, spent_script_pubkey: list) -> bytes:
    """
    Return the 32-byte message that was signed for input at input_index:
        message = hash256(
            canonical_serialize(
                tx,
                substitute_input_index=input_index,
                substitute_script=spent_script_pubkey,
            )
        )
    """
    # TODO: implement using canonical_serialize as specified above
    serialized = canonical_serialize(
        tx,
        substitute_input_index=input_index,
        substitute_script=spent_script_pubkey
    )
    return hash256(serialized)
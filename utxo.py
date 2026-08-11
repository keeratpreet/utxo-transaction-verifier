"""
UTXO set maintenance.
Keys: (txid: str, vout: int)
Values: {"value": int, "script_pubkey": list}
"""


def get_output(utxo_set: dict, txid: str, vout: int) -> dict | None:
    """
    Return the UTXO entry for (txid, vout), or None if not present.
    """
    # TODO: implement
    return utxo_set.get((txid,vout))

    # raise NotImplementedError


def spend_output(utxo_set: dict, txid: str, vout: int) -> None:
    """
    Remove the output (txid, vout) from utxo_set. Idempotent if missing.
    """
    # TODO: implement
    key = (txid,vout)
    if key in utxo_set:
        utxo_set.pop(key)

    # raise NotImplementedError


def add_output(utxo_set: dict, txid: str, vout: int, value: int, script_pubkey: list) -> None:
    """
    Add a new unspent output to utxo_set.
    """
    # TODO: implement
    key = (txid,vout)
    utxo_set[key] = {
        "value": value,
        "script_pubkey" : script_pubkey
    }

    # raise NotImplementedError

"""
Main entry: verify a transaction and update UTXO set.
"""

from utxo import get_output, spend_output, add_output
from script import execute_script
from transaction import tx_id, get_signing_message


def verify_transaction(tx: dict, utxo_set: dict) -> bool:
    """
    Validate tx against utxo_set.

    Validation logic (see the assignment instructions):
    - Check tx has at least one input and one output.
    - Check all inputs exist and are unspent (no double-spend).
    - Check no duplicate (txid, vout) in inputs.
    - Check fee rule: sum(input values) >= sum(output values).
    - For each input, compute signing message, then run script_sig + script_pubkey;
      script execution must succeed and end with a single true value.

    Atomicity requirement:
    - You MUST NOT mutate utxo_set while validating.
    - Only after all checks pass should you:
        * remove spent outputs from utxo_set, and
        * add new outputs for this tx.
    - If validation fails, utxo_set must remain unchanged.
    """
    # Every check below runs to completion (and can bail out with `return
    # False`) before utxo_set is touched at all — the mutations only start
    # once every input has been validated, which is what keeps a failed
    # verification from ever leaving utxo_set partially updated.

    if "inputs" not in tx or "outputs" not in tx:
        return False

    if len(tx["inputs"]) == 0 or len(tx["outputs"]) == 0:
        return False

    # every output must be a positive integer: a negative output could offset
    # a huge one and slip past the fee rule below (e.g. outputs [150, -60]
    # against 100 of inputs)
    for out in tx["outputs"]:
        if type(out.get("value")) is not int or out["value"] <= 0:
            return False

    # double-spend guard: no input may reference the same (txid, vout) twice
    # within this transaction
    seen = set()

    for inp in tx["inputs"]:
        key = (inp["txid"], inp["vout"])
        if key in seen:
            return False
        seen.add(key)

    input_sum = 0

    for idx, inp in enumerate(tx["inputs"]):

        # the referenced output must exist and still be unspent in utxo_set
        prev = get_output(utxo_set, inp["txid"], inp["vout"])

        if prev is None:
            return False

        value = prev["value"]
        script_pk = prev["script_pubkey"]

        # the signing message binds this specific input to the output it
        # claims to spend — see get_signing_message for the substitution logic
        message = get_signing_message(tx, idx, script_pk)

        if not execute_script(inp["script_sig"], script_pk, message):
            return False

        input_sum += value

    # compute total output value
    output_sum = 0
    for out in tx["outputs"]:
        output_sum += out["value"]

    # fee rule: outputs can't create value out of thin air (input_sum - output_sum
    # is the implicit transaction fee, which is allowed to be >= 0)
    if output_sum > input_sum:
        return False

    # all checks passed — now, and only now, mutate utxo_set
    tid = tx_id(tx)

    for inp in tx["inputs"]:
        spend_output(utxo_set, inp["txid"], inp["vout"])

    for idx, out in enumerate(tx["outputs"]):
        add_output(
            utxo_set,
            tid,
            idx,
            out["value"],
            out["script_pubkey"]
        )

    return True
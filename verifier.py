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
    # TODO: implement according to the rules above and the assignment instructions

    if "inputs" not in tx or "outputs" not in tx:
        return False 
    
    if len(tx["inputs"]) == 0 or len(tx["outputs"]) == 0:
        return False 
    
    seen = set()

    for inp in tx["inputs"]:
        key = (inp["txid"], inp["vout"])
        if key in seen:
            return False
        seen.add(key)

    input_sum = 0 

    for idx, inp in enumerate(tx["inputs"]):

        prev = get_output(utxo_set, inp["txid"], inp["vout"])

        if prev is None:
            return False 
        
        value = prev["value"]
        script_pk = prev["script_pubkey"]

        message = get_signing_message(tx, idx, script_pk)

        if not execute_script(inp["script_sig"], script_pk, message):
            return False 
        
        input_sum += value

    # compute total output value
    output_sum = 0
    for out in tx["outputs"]:
        output_sum += out["value"]

    # fee rule
    if output_sum > input_sum:
        return False 

    # update utxo set
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
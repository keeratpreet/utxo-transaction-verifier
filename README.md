# UTXO Transaction Verifier

A from-scratch implementation of Bitcoin-style transaction validation on the UTXO (Unspent Transaction Output) model: UTXO set management, deterministic transaction serialization, a stack-based script interpreter, and full transaction verification with signature checking.

## Modules

- **`utxo.py`** — UTXO set operations: look up an output by `(txid, vout)`, spend it, add new outputs.
- **`transaction.py`** — deterministic transaction serialization and ID computation (`json.dumps(..., sort_keys=True, separators=(",", ":"))`, recursively sorted keys) so hashing and signing are reproducible.
- **`script.py`** — stack-based script interpreter modeled on Bitcoin Script. Supports `OP_DUP`, `OP_HASH160`, `OP_EQUAL`, `OP_EQUALVERIFY`, `OP_VERIFY`, `OP_CHECKSIG`, and `OP_CHECKMULTISIG`; any stack underflow or invalid opcode fails the script immediately.
- **`crypto.py`** — SHA256/RIPEMD160 hashing and ECDSA (secp256k1) signature verification helpers.
- **`verifier.py`** — `verify_transaction(tx, utxo_set)`, the main entry point tying everything together.

## Verification flow

1. Reject transactions with no inputs or no outputs.
2. Check every referenced input exists in the current UTXO set, and that no `(txid, vout)` pair is spent twice within the same transaction (double-spend guard).
3. For each input, compute the signing message by substituting the referenced output's `script_pubkey` for the input's `script_sig`, then run `script_sig` followed by `script_pubkey` through the interpreter.
4. Require the script to succeed and leave exactly one truthy value on the stack.
5. Require `sum(input values) >= sum(output values)` (implicit fee).
6. Only if every check passes: atomically remove spent outputs and add the transaction's new outputs to the UTXO set. On any failure, the UTXO set is left untouched.

## Usage

```python
from verifier import verify_transaction

utxo_set = { ... }          # {(txid, vout): {"value": int, "script_pubkey": [...]}}
tx = { ... }                # transaction dict with "inputs" and "outputs"

ok = verify_transaction(tx, utxo_set)
```

## Dependencies

```bash
pip install ecdsa
```

See `report.pdf` for the full design writeup, including the challenges around mixed script-element typing (hex vs. int) and multisignature verification.

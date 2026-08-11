"""
Stack-based script interpreter.

Execute script_sig first, then script_pubkey.
`message` is the signing message for OP_CHECKSIG / OP_CHECKMULTISIG.

Supported opcodes (all required):
  OP_DUP
  OP_HASH160
  OP_EQUAL
  OP_EQUALVERIFY
  OP_CHECKSIG
  OP_VERIFY
  OP_CHECKMULTISIG

Data encoding rules (see the assignment instructions):
- Script elements are either:
  * One of the opcodes above, OR
  * Hex-encoded strings representing raw bytes (signatures, pubkeys, hashes), OR
  * Small Python ints (only for m and n in multisig).
- Non-opcode strings MUST be treated as hex; do NOT guess ASCII.
"""

# Import crypto for OP_HASH160, OP_CHECKSIG, OP_CHECKMULTISIG
from crypto import hash160, verify_signature

OPCODES = {
    "OP_DUP",
    "OP_HASH160",
    "OP_EQUAL",
    "OP_EQUALVERIFY",
    "OP_CHECKSIG",
    "OP_VERIFY",
    "OP_CHECKMULTISIG",
}


def execute_script(script_sig: list, script_pubkey: list, message: bytes) -> bool:
    """
    Run script_sig then script_pubkey on a fresh stack.

    Failure semantics:
    - Any stack underflow or unknown opcode must cause immediate failure.
    - OP_VERIFY popping a false value must cause immediate failure.
    - OP_CHECKSIG / OP_CHECKMULTISIG push 1 (true) or 0 (false); they do not
      raise, but incorrect types should be treated as failure.

    Success:
    - After both scripts run, the stack must have exactly one item, and it
      must be true (non-zero int or non-empty bytes). Otherwise the script
      fails.
    """
    # TODO: implement according to the exact opcode semantics in the assignment instructions
    stack=[]
    script = script_sig + script_pubkey

    for i in script :
        if not _is_opcode(i):
          if isinstance(i, str):
              # handle multisig integers like "2" or "3"
              if i.isdigit():
                  stack.append(int(i))
              else:
                  stack.append(_to_bytes(i))
          else:
              stack.append(i)
          continue
        
        if i == "OP_DUP":
            if len(stack)<1:
                return False 
            stack.append(stack[-1])

        elif i == "OP_HASH160":
            if len(stack) < 1 :
                return False
            stack.append(hash160(stack.pop()))

        elif i=="OP_EQUAL":
            if len(stack) < 2:
                return False 
            a=stack.pop()
            b=stack.pop()
            if a== b :
                stack.append(1)
            else:
                stack.append(0)
            
        elif i == "OP_EQUALVERIFY":
            if len(stack) < 2 :
                return False 
            if stack.pop() != stack.pop():
                return False 
            
        elif i == "OP_VERIFY":
            if len(stack) < 1 :
                return False 
            if not stack.pop() :
                return False 

        elif i == "OP_CHECKSIG":
            if len(stack) < 2 :
                return False 
            pubkey = stack.pop()
            sign = stack.pop()
            if(verify_signature(pubkey,message,sign)):
                stack.append(1)
            else :
                stack.append(0)

        elif i == "OP_CHECKMULTISIG":
            if len(stack) < 1:
                return False 
            
            n = stack.pop()
            if not isinstance(n,int):
                return False
            
            if len(stack) < n:
                return False 
            
            pubkeys = []

            for k in range(n):
                pubkeys.append(stack.pop())

            if len(stack) < 1:
                return False 
            
            m=stack.pop()
            if not isinstance(m,int):
                return False 
            
            sigs=[]
            if len(stack) < m :
                return False
            
            for k in range(m):
                sigs.append(stack.pop())

            valid_cnt = 0 
            for sig in sigs:
                for pk in pubkeys:
                    if verify_signature(pk,message,sig):
                        valid_cnt+=1 
                        break 
            stack.append(1 if valid_cnt >=m else 0)

        else :
            return False 
    
    if len(stack) != 1 :
        return False 
    
    top = stack.pop()
    if isinstance(top,int):
        return top != 0
    
    return bool(top)

def _is_opcode(elem) -> bool:
    """True if elem is an opcode string (e.g. OP_DUP)."""
    return isinstance(elem, str) and elem.startswith("OP_")


def _to_bytes(elem: str) -> bytes:
    """
    Convert a non-opcode string element to bytes.
    MUST treat elem as hex; no ASCII guessing.
    """
    return bytes.fromhex(elem)

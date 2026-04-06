import json

# Python Program for implementation of RSA Algorithm
# From: https://www.geeksforgeeks.org/computer-networks/rsa-algorithm-cryptography/

# Function to find modular inverse of e modulo phi(n)
# Here we are calculating phi(n) using Hit and Trial Method
# but we can optimize it using Extended Euclidean Algorithm

# RSA Key Generation
def generate_keys():
  p = 7919 # or 4563413
  q = 1009 # or 3457631
  n = p * q
  phi = (p - 1) * (q - 1)

  # Choose e, where 1 < e < phi(n) and gcd(e, phi(n)) == 1
  # e = 0
  # for e in range(2, phi):
  #   if gcd(e, phi) == 1:
  #     break
  e = 65537               # standard public exponent — always coprime with phi here

  # Compute d such that e * d ≡ 1 (mod phi(n))
  # d = modInverse(e, phi)
  d = pow(e, -1, phi)

  return e, d, n

# # Encrypt message using public key (e, n)
# def encrypt(m, e, n):
#   return pow(m, e, n)

# # Decrypt message using private key (d, n)
# def decrypt(c, d, n):
#   return pow(c, d, n)

# integer encrypt / decrypt
def encrypt(m, e: int, n: int): # encrypt a single integer m. requires 0 <= m < n
  #         m: int             -> int
  if isinstance(m, int):
    if not (0 <= m < n):
      raise ValueError(f"Message {m} out of range [0, {n})")
    return {"type": "int", "data": pow(m, e, n)}

  elif isinstance(m, bytes):
    return {"type": "bytes", "data": encrypt_bytes(m, e, n)}

  elif isinstance(m, str):
    return {"type": "str", "data": encrypt_bytes(m.encode("utf-8"), e, n)}

  elif isinstance(m, dict):
    return {"type": "dict", "data": encrypt_dict(m, e, n)}

  else:
    raise TypeError("Unsupported type")

def decrypt(c, d: int, n: int): # decrypt a single integer m
  #         c: int             -> int
  if not isinstance(c, dict) or "type" not in c or "data" not in c:
    raise ValueError("Invalid ciphertext format")

  ctype = c["type"]
  data = c["data"]

  if ctype == "int":
    return pow(data, d, n)

  elif ctype == "bytes":
    return decrypt_bytes(data, d, n)

  elif ctype == "str":
    return decrypt_bytes(data, d, n).decode("utf-8")

  elif ctype == "dict":
    return decrypt_dict(data, d, n)

  else:
    raise ValueError("Unknown ciphertext type")

def encrypt_bytes(data: bytes, e: int, n: int) -> list[int]:
  """
  Encrypt a bytes object byte-by-byte.
  Each byte value (0-255) is always < n (7,990,271), so no chunking needed.
  Returns a list of ciphertext integers, one per byte.
  """
  return [pow(b, e, n) for b in data]

def decrypt_bytes(ciphertext: list[int], d: int, n: int) -> bytes:
  """Decrypt a list of ciphertext integers back to the original bytes."""
  if not all(isinstance(c, int) for c in ciphertext):
    raise ValueError("Invalid ciphertext format")

  try:
    return bytes(pow(c, d, n) for c in ciphertext)
  except ValueError:
    raise ValueError("Decryption failed: invalid key or corrupted data")

def encrypt_string(s: str, e: int, n: int) -> list[int]:
  """
  Encrypt a UTF-8 string.
  Converts to bytes first, then encrypts each byte.
  Handles any Unicode string — not just ASCII.
  """
  return encrypt_bytes(s.encode("utf-8"), e, n)

def decrypt_string(ciphertext: list[int], d: int, n: int) -> str:
  """Decrypt a list of ciphertext integers back to the original UTF-8 string."""
  return decrypt_bytes(ciphertext, d, n).decode("utf-8")

def encrypt_dict(d_obj: dict, e: int, n: int) -> list[int]:
  """
  Encrypt an entire dict by serializing it to a JSON string first,
  then encrypting the UTF-8 bytes of that string.

  This is the realistic approach — the whole payload is treated as
  one message, not field by field.

  Assumption: all dict values must be JSON-serializable
  (str, int, float, list, dict, bool, None).
  """
  json_str = json.dumps(d_obj, separators=(",", ":"), sort_keys=True)
  return encrypt_string(json_str, e, n)

def decrypt_dict(ciphertext: list[int], d: int, n: int) -> dict:
  """Decrypt a list of ciphertext integers back to the original dict."""
  json_str = decrypt_string(ciphertext, d, n)
  return json.loads(json_str)

# Main execution
# if __name__ == "__main__":
#   # Key Generation
#   e, d, n = generate_keys()

#   print(f"Public Key (e, n): ({e}, {n})")
#   print(f"Private Key (d, n): ({d}, {n})")

#   # Message
#   M = "123"
#   # M = {12, "Lara", 34.5}
#   print(f"Original Message: {M}")

#   # Encrypt the message
#   C = encrypt(M, e, n)
#   print(f"Encrypted Message: {C}")

#   # Decrypt the message
#   decrypted = decrypt(C, d, n)
#   print(f"Decrypted Message: {decrypted}")

if __name__ == "__main__":
  PASS = "✓"
  FAIL = "✗"

  def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    if not condition:
      raise AssertionError(f"FAILED: {label}")

  print("\n" + "=" * 55)
  print("  rsa.py — self-test")
  print("=" * 55)

  e, d, n = generate_keys()

  # ── 1. Key sanity ──────────────────────────────────────────
  print("\n[Test 1] Key generation sanity")
  phi = (7919 - 1) * (1009 - 1)
  check("e > 1",               e > 1)
  check("d > 1",               d > 1)
  check("e*d ≡ 1 (mod phi)",   (e * d) % phi == 1)
  check("n = 7919*1009",       n == 7919 * 1009)

  # ── 2. Integer round-trip ─────────────────────────────────
  print("\n[Test 2] Integer round-trip")
  for m in [0, 1, 42, 255, 1000, 9999]:
    check(f"m={m}", decrypt(encrypt(m, e, n), d, n) == m)

  # ── 3. Integer out of range raises ────────────────────────
  print("\n[Test 3] Integer out of range raises ValueError")
  try:
    encrypt(n, e, n)
    check("Should have raised", False)
  except ValueError:
    check("Raised ValueError for m >= n", True)

  # ── 4. Byte-level round-trip ──────────────────────────────
  print("\n[Test 4] Bytes round-trip")
  raw = b"Hello, EV World!"
  ct  = encrypt_bytes(raw, e, n)
  check("Ciphertext is list of ints",  all(isinstance(x, int) for x in ct))
  check("Length preserved",            len(ct) == len(raw))
  check("Round-trip correct",          decrypt_bytes(ct, d, n) == raw)

  # ── 5. String round-trip — ASCII ──────────────────────────
  print("\n[Test 5] String round-trip — ASCII")
  s = "ABCD1234EFGH5678_9000000001"
  ct = encrypt_string(s, e, n)
  check("Returns list",        isinstance(ct, list))
  check("Round-trip correct",  decrypt_string(ct, d, n) == s)

  # ── 6. String round-trip — Unicode ───────────────────────
  print("\n[Test 6] String round-trip — Unicode")
  s_uni = "नमस्ते EV चार्जिंग"
  ct    = encrypt_string(s_uni, e, n)
  check("Unicode round-trips", decrypt_string(ct, d, n) == s_uni)

  # ── 7. String — empty string ──────────────────────────────
  print("\n[Test 7] Empty string")
  ct = encrypt_string("", e, n)
  check("Empty string → empty list", ct == [])
  check("Round-trip empty",          decrypt_string(ct, d, n) == "")

  # ── 8. Dict round-trip — simple ───────────────────────────
  print("\n[Test 8] Dict round-trip — simple")
  payload = {"VMID": "ABC123_9000000001", "PIN": 1234, "amount": 200}
  ct = encrypt_dict(payload, e, n)
  check("Returns list",       isinstance(ct, list))
  check("Round-trip correct", decrypt_dict(ct, d, n) == payload)

  # ── 9. Dict round-trip — nested ───────────────────────────
  print("\n[Test 9] Dict round-trip — nested / complex")
  nested = {
    "user"    : {"name": "Rakshita", "phone": "9999999991"},
    "amount"  : 350.75,
    "tags"    : ["ev", "charging", "zone1"],
    "success" : True,
    "extra"   : None,
  }
  ct = encrypt_dict(nested, e, n)
  check("Nested dict round-trips", decrypt_dict(ct, d, n) == nested)

  # ── 10. Different plaintexts → different ciphertexts ──────
  print("\n[Test 10] Different inputs produce different ciphertexts")
  ct1 = encrypt_string("hello", e, n)
  ct2 = encrypt_string("world", e, n)
  check("Different strings → different CT", ct1 != ct2)

  # ── 11. Encryption is deterministic ───────────────────────
  print("\n[Test 11] Encryption is deterministic")
  ct_a = encrypt_string("hello", e, n)
  ct_b = encrypt_string("hello", e, n)
  check("Same input → same CT", ct_a == ct_b)

  # ── 12. Wrong private key → garbage output ─────────────────
  print("\n[Test 12] Wrong private key gives wrong result")
  ct   = encrypt_string("secret", e, n)
  try:
    bad  = decrypt_string(ct, d + 1, n)    # wrong d
    check("Wrong key gives wrong result", bad != "secret")
  except Exception:
    check("Wrong key causes failure (acceptable)", True)

  print("\n" + "=" * 55)
  print("  All rsa.py tests passed ✓")
  print("=" * 55 + "\n")

import ascon

def get_key_nonce_pt_ad(self, fid, timestamp):
  try:
    key = b"RaksAditPriyVeda"
    nonce = timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
    # nonce - number used once; ensures same input != same output and prevents replay attacks
    pt = fid.encode("utf-8") # actua data to protect
    ad = timestamp.encode("utf-8")
    # associated data is: data that is NOT encrypted, but is authenticated
    # timestamp is not hidden but cannot be tampered with
    return key, nonce, pt, ad

  except Exception as e:
    print(f"Exception: {e}")
    return None, None, None, None

def ascon_encrypt(key = None, nonce = None, ad = None, plaintext = None, variant="Ascon-128"):
  """
  key: 16 bytes
  nonce: 16 bytes
  ad: bytes (associated data)
  plaintext: bytes
  """
  req_fields = [key, nonce, ad, plaintext]
  if any(x is None for x in req_fields):
    print(req_fields)
    raise ValueError("Something is None in ascon_encrypt")

  ciphertext = ascon.encrypt(key, nonce, ad, plaintext, variant)
  if ciphertext is None:
    raise ValueError("Encryption failed in ascon_encrypt")
  return ciphertext

def ascon_decrypt(key = None, nonce = None, ad = None, ciphertext = None, variant="Ascon-128"):
  req_fields = [key, nonce, ad, ciphertext]
  if any(x is None for x in req_fields):
    print(req_fields)
    raise ValueError("Something is None in ascon_decrypt")

  plaintext = ascon.decrypt(key, nonce, ad, ciphertext, variant)
  if plaintext is None:
    raise ValueError("Decryption failed in ascon_decrypt")
  return plaintext

import ascon

def ascon_encrypt(key, nonce, ad, plaintext, variant="Ascon-128"):
  """
  key: 16 bytes
  nonce: 16 bytes
  ad: bytes (associated data)
  plaintext: bytes
  """
  ciphertext = ascon.encrypt(key, nonce, ad, plaintext, variant)
  if ciphertext is None:
    raise ValueError("Encryption failed in ascon_encrypt")
  return ciphertext

def ascon_decrypt(key, nonce, ad, ciphertext, variant="Ascon-128"):
  plaintext = ascon.decrypt(key, nonce, ad, ciphertext, variant)
  if plaintext is None:
    raise ValueError("Decryption failed in ascon_decrypt")
  return plaintext

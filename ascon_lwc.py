from Crypto.Cipher import AES

def ascon_encrypt(key, nonce, ad, plaintext):
  cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
  cipher.update(ad)
  ciphertext, tag = cipher.encrypt_and_digest(plaintext)
  return ciphertext + tag

def ascon_decrypt(key, nonce, ad, ciphertext):
  cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
  cipher.update(ad)
  ct = ciphertext[:-16]
  tag = ciphertext[-16:]
  return cipher.decrypt_and_verify(ct, tag)

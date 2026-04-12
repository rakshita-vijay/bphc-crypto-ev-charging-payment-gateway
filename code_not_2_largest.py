# --- code_not_2_largest.py ---

# --- requirements.txt ---
pillow
qrcode
ascon
opencv-python
tabulate
streamlit>=1.28.0
# --- ascon_lwc.py ---
import ascon

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

# --- all_code_not_2_largest.py ---
import os, sys

all_files = []

with open("code_not_2_largest.py", "w") as out_file:
  for root, dirs, files in os.walk(os.getcwd()):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'qrcodes', 'pages']]
    files[:] = [f for f in files if f not in ['.gitignore', '_to_do.txt', 'all_code.py', 'app.py', 'code.py', 'README.md', 'v_imp_to_clear_qrcodes.py']]

    for file in files:
      file_path = os.path.join(root, file)
      try:
        size = os.path.getsize(file_path)
        all_files.append({
          "fn": file_path,
          "len": size
        })
      except Exception:
        continue

  if len(all_files) < 2:
    print("Not enough files")
    exit()

  sorted_data = sorted(all_files, key=lambda x: x["len"])
  last2 = [sorted_data[-1]["fn"], sorted_data[-2]["fn"]]
  print(f"Download and attach: {last2[0].split('/')[-1]} and {last2[1].split('/')[-1]}")

  for file_data in sorted_data:
    file_path = file_data["fn"]
    if file_path in last2:
      continue

    try:
      with open(file_path, "r") as fi:
        out_file.write(f"# --- {file_path.split('/')[-1]} ---\n")
        out_file.write(fi.read())
        out_file.write("\n")
    except Exception:
      # Skip binary/unreadable files
      continue

# --- shor_algo.py ---
import math
import random

def period(a, n):
  #Objective: Find r such that a^r = 1 mod n
  #This would normally be done with a quantum computer, but I'm doing it classically for demonstration
  r = 1
  value = a % n
  while value != 1:
    value = (value * a) % n
    r += 1
    #Safety limit
    if r > n:
      return None
  return r

def shor_algorithm(n):
  #If we got an even number, just return 2 and n/2 as the factors
  if n % 2 == 0:
    return 2, n // 2

  #Giving 10 retries to factorize, a retry will fail if we can't find a valid period
  for attempt in range(10):
    a = random.randint(2, n-1)

    gcd = math.gcd(a, n)
    if gcd != 1:
      return gcd, n // gcd

    r = period(a, n)

    if r is None or r % 2 != 0:
      continue

    factor1 = math.gcd(pow(a, r // 2) - 1, n)
    factor2 = math.gcd(pow(a, r // 2) + 1, n)

    #Make sure the factors we got aren't 1, n
    if factor1 != 1 and factor1 != n:
      return factor1, factor2

  return None

def generate_rsa_keypair():
  #Generate the keypair, but with small values of p and q.
  #The keypair is intentionally weak to demonstrate Shor's algo
  p, q = 61, 53 #random small primes for now
  N = p * q
  e = 17
  phi = (p-1) * (q-1)
  d = pow(e, -1, phi)

  public_keypair = (e, N)
  private_keypair = (d, N)
  return public_keypair, private_keypair, p, q

def demonstrate_attack():
  public_key, private_key, original_p, original_q = generate_rsa_keypair()
  e, N = public_key

  print(f"RSA Public Key: e={e}, N={N}")
  print(f"Attacker only knows N={N}. Attempting to factor it...")

  result = shor_algorithm(N)

  if result:
    found_p, found_q = result
    print(f"Shor's algorithm recovered factors: p={found_p}, q={found_q}")
    print(f"Original factors were:              p={original_p}, q={original_q}")

    # Reconstruct private key from broken factors
    phi = (found_p - 1) * (found_q - 1)
    recovered_d = pow(e, -1, phi)
    print(f"Private key recovered: d={recovered_d}")
    print(f"Original private key:  d={private_key[0]}")
    print("RSA encryption is BROKEN for this key.")
  else:
    print("Factoring failed.")

if __name__ == "__main__":
  demonstrate_attack()

# --- main.py ---
import sys

from grid import Grid
from franchise import Franchise
from kiosk import Kiosk
from user import User
from tabulate import tabulate

# def print_users(grid):
#   print("\n--- USERS ---")
#   print(f"{'UID':<20} {'Name':<10} {'Phone':<12} {'Balance':<10}")
#   for u in grid.users.values():
#     print(f"{u.uid:<20} {u.u_name:<10} {u.u_phone:<12} {u.u_balance:<10}")

# def print_franchises(grid):
#   print("\n--- FRANCHISES ---")
#   print(f"{'FID':<20} {'Name':<10} {'Zone':<5} {'Balance':<10}")
#   for f in grid.franchises.values():
#     print(f"{f.fid:<20} {f.f_name:<10} {f.f_zone_code:<5} {f.f_balance:<10}")

# def print_blockchain(grid):
#   print("\n--- BLOCKCHAIN ---")
#   print(f"{'TxnID':<20} {'UID':<20} {'FID':<20} {'Amount':<10}")
#   for b in grid.blockchain:
#     print(f"{b['transaction_id'][:16]:<20} {b['uid']:<20} {b['fid']:<20} {b['amount']:<10}")

def display_users(grid):
  table = []
  for u in grid.users.values():
    table.append([u.uid, u.u_name, u.u_phone, u.u_balance, u.grid])

  print("\n--- USERS ---")
  print(tabulate(table, headers=["UID", "Name", "Phone", "Balance", "Grid"], tablefmt="grid"))

def display_franchises(grid):
  table = []
  for f in grid.franchises.values():
    table.append([f.fid, f.f_name, f.f_zone_code, f.f_balance])

  print("\n--- FRANCHISES ---")
  print(tabulate(table, headers=["FID", "Name", "Zone", "Balance"], tablefmt="grid"))

def display_blockchain(grid):
  table = []
  for b in grid.blockchain:
    table.append([
      b["transaction_id"][:16],
      b["uid"],
      b["fid"],
      b["amount"],
      b["dispute_flag"]
    ])

  print("\n--- BLOCKCHAIN ---")
  print(tabulate(table, headers=["TxnID", "UID", "FID", "Amount", "Refund"], tablefmt="grid"))

if __name__ == "__main__":
  grid = Grid()
  # Create user
  user = User("Rakshita", 9999999999, "1234", "Z1", grid, 1000)
  user2 = User("Rakshitaaaa", 1111, "123456", "Z1", grid, 1000)

  # Create franchise
  fr = Franchise("Station1", "ACC123", "Z1", "pass", 500, grid)

  # Create kiosk
  kiosk = Kiosk(grid, fr)

  # Generate QR
  kiosk.generate_qrcode()

  # Simulate payment (use filename from QR generation)
  payload = user.charge_request(f"qrcode_xxxxxx{fr.vfid[-6:]}.png", 100)
  result = kiosk.process_payment(f"qrcode_xxxxxx{fr.vfid[-6:]}.png", user.uid, fr.fid, payload, 100)
  print(result)

  # Call printers
  # print_users(grid)
  display_users(grid)

  # print_franchises(grid)
  display_franchises(grid)

  # print_blockchain(grid)
  display_blockchain(grid)

# --- franchise.py ---
import os
import datetime
import hashlib
from PIL import Image
# from grid import Grid

class Franchise:
  def __init__(self, f_name, f_acc_num, f_zone_code, f_pwd, f_balance, grid):
    self.f_name = f_name
    self.f_acc_num = f_acc_num
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    self.grid = grid

    self.fid = None # done in grid, if validated - so no dangling fids are there
    self.req_validation_and_reg_w_grid()
    self.vfid = None # done in kiosk
    self.qr_code = None
    self.hardware_failure_rate = 0.0  # 0-1 probability of hardware failure

  def req_validation_and_reg_w_grid(self):
    confirmation = self.grid.req_fran_validation(self)
    if (confirmation == True):
      print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")
    else:
      print("Franchise validation failed")

    # correction at end:
    # confirmation() adds amount to f_balance regardless of whether the cable was successfully unlocked, which is slightly wrong logically (the balance update should be on the grid side, not the franchise side). Per the spec: "Grid Processing: funds are transferred to the Franchise." So balance update belongs in grid.add_block, not in franchise.confirmation. Remove self.f_balance += amount from confirmation().

  def display_qrcode(self, qrcode_file_name):
    try:
      img = Image.open(os.path.join("qrcodes", qrcode_file_name))
      self.qr_code = img
      print(f"QR Code displayed: {qrcode_file_name}")
      # In Streamlit, this will be handled differently
      self.qr_code.show()
    except Exception as e:
      print(f"Error displaying QR code: {e}")

  def confirmation(self, success, amount = 0):
    if success:
      # self.f_balance += amount
      print(f"Transaction for {self.f_name} accepted.")
      print("Attempting to unlock charging cable...")
      status = self.unlock_charging_cable(1)
      if status:
        print(f"Charging cable unlocked successfully for {self.f_name}")
        return True
      else:
        print(f"Charging cable unlock failed for {self.f_name} :(")
        print("Hardware failure detected - refund will be triggered")
        return False
    else:
      print(f"Transaction for {self.f_name} rejected.")
      return None

  def unlock_charging_cable(self, flag):
    # implement this
    # True if unlocked, False if failed to unlock
    try:
      # Log the unlock attempt
      timestamp = datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")
      print(f"Hardware - Unlock attempt at {timestamp}")

      # Simulate network latency
      import time
      time.sleep(0.1)

      # Simulate hardware failure with configurable probability
      # hardware_failure_rate: 0.0 = always succeed, 1.0 = always fail
      failure_random = random.random()

      if failure_random < self.hardware_failure_rate:
        print(f"Hardware - Cable unlock mechanism failed (simulated failure)")
        return False

      # Simulate occasional random failures (1% chance by default if not configured)
      if self.hardware_failure_rate == 0.0 and random.random() < 0.01:
        print(f"Hardware - Unexpected hardware failure (1% random chance)")
        return False

      # Cable unlock succeeds
      print(f"Hardware - Cable unlock mechanism SUCCEEDED")
      print(f"Hardware - Charging session active - User can now charge vehicle")

      return True

    except Exception as e:
      print(f"Hardware - Cable unlock error: {e}")
      return False

if __name__ == "__main__":
  from grid import Grid

  PASS = "✓"
  FAIL = "✗"

  def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    if not condition:
      raise AssertionError(f"FAILED: {label}")

  print("\n" + "=" * 55)
  print("  franchise.py — self-test")
  print("=" * 55)

  grid = Grid()

  # ── 1. Valid registration ─────────────────────────────────
  print("\n[Test 1] Valid franchise (Z1)")
  fr = Franchise("StationAlpha", "ACC001", "Z1", "pwd", 500, grid)
  check("FID set",               fr.fid is not None)
  check("FID length 16",         len(fr.fid) == 16)
  check("In grid registry",      fr.fid in grid.franchises)
  check("Balance unchanged",     fr.f_balance == 500)
  check("vfid starts None",      fr.vfid is None)

  # ── 2. Invalid zone code ──────────────────────────────────
  print("\n[Test 2] Invalid zone code (Z9)")
  fr_bad = Franchise("BadStation", "ACC002", "Z9", "pwd", 100, grid)
  check("FID is None",           fr_bad.fid is None)
  check("Not in registry",       fr_bad.fid not in grid.franchises)

  # ── 3. confirmation() success path ───────────────────────
  print("\n[Test 3] confirmation() — success")
  bal_before = fr.f_balance
  result = fr.confirmation(True, 200)
  check("Returns True", result == True)

  # ── 4. confirmation() failure path ───────────────────────
  print("\n[Test 4] confirmation() — failure")
  result = fr.confirmation(False, 200)
  check("Returns None", result is None)

  # ── 5. unlock_charging_cable directly ────────────────────
  print("\n[Test 5] unlock_charging_cable()")
  # Set high success rate for testing
  fr.hardware_failure_rate = 0.0
  check("Returns True when configured to succeed",  fr.unlock_charging_cable()  == True)

  # Set high failure rate for testing
  fr.hardware_failure_rate = 1.0
  check("Returns False when configured to fail", fr.unlock_charging_cable() == False)

  # ── 6. Two franchises — independent balances ─────────────
  print("\n[Test 6] Two franchises are independent")
  fr2 = Franchise("StationBeta", "ACC003", "Z2", "pwd2", 1000, grid)
  check("Different FIDs",        fr.fid != fr2.fid)
  check("Beta balance correct",  fr2.f_balance == 1000)
  check("Alpha unaffected",      fr.f_balance  == 500)

  print("\n" + "=" * 55)
  print("  All franchise.py tests passed ✓")
  print("=" * 55 + "\n")

# --- kiosk.py ---
import os
import datetime
import hashlib
import qrcode
import cv2
from PIL import Image

from ascon_lwc import ascon_decrypt
# from pyzbar.pyzbar import decode

import shor_algo
import rsa
# from grid import Grid
# from franchise import Franchise

class Kiosk:
  def __init__(self, grid, franchise):
    self.grid = grid
    self.franchise = franchise
    self.timestamp = None

  def generate_qrcode(self):
    # hashed_fid - data to encode in the QR code
    fid = self.franchise.fid

    self.timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    vfid = self.grid.generate_vfid(fid, self.timestamp)
    self.franchise.vfid = vfid

    qr_data = f"{vfid}, {self.timestamp}"

    # Generate the QR code image using the make() shortcut function
    qr = qrcode.make(qr_data)

    # Save Image
    os.makedirs("qrcodes", exist_ok=True)
    qr.save(f"qrcodes/qrcode_xxxxxx{vfid[-6:]}.png")

    print(f"QR code generated and saved as qrcode_xxxxxx{vfid[-6:]}.png in the folder 'qrcodes'")
    self.franchise.display_qrcode(f"qrcode_xxxxxx{vfid[-6:]}.png")

  def decrypt_qrcode(self, decoded_qr_data):
    # and verify hash???

    # 1. load and decode the qr code
    # img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    # decoded_objects = decode(img)

    '''
    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    detector = cv2.QRCodeDetector()
    decoded_qr_data, _, _ = detector.detectAndDecode(img)
    '''

    # print(decoded_qr_data)
    # print(type(decoded_qr_data))

    if not decoded_qr_data:
      print("QR decode failed")
      return None, None

    # 2. extract the data
    # for obj in decoded_objects:
    #   scanned_hash = obj.data.decode('utf-8')
    #   print(f"Scanned Hash: {scanned_hash}")
    # data = decoded_object.decode('utf-8')

    # Step 2: Split VFID and timestamp
    try:
      parts = decoded_qr_data.split(", ")
      if len(parts) != 2:
        print("Invalid QR format, line 68")
        return None, None

      vfid_hex = parts[0].strip()
      ts = parts[1].strip()

      # print("Original vfid (first 10 bytes):", self.franchise.vfid[:20])
      # print("Decoded vfid (first 10 bytes):", vfid_hex[:20])
      # print(self.franchise.vfid == vfid_hex)

      vfid_from_decoded_qr = bytes.fromhex(vfid_hex)

    except:
      print("Invalid QR format")
      return None, None

    try:
      if (ts == self.timestamp):
        # NOTE: To "verify", you must re-hash known data and check if the hashes match.

        key = b"RaksAditPriyVeda"
        nonce = self.timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
        # nonce - number used once; ensures same input != same output and prevents replay attacks
        ad = self.timestamp.encode("utf-8")

        # step: Decrypt
        pt = ascon_decrypt(key, nonce, ad, vfid_from_decoded_qr)
        fid = pt.decode()

        if (fid == self.franchise.fid):
          return True, fid # placeholder
        else:
          raise Exception("FIDs don't match")
          # return False, None # placeholder
      else:
        raise Exception("Timestamps don't match")

    except Exception as e:
      print(f"{e}")
      print("Decryption failed --> tampered QR")
      return None, None

  def process_payment(self, payload):
    # payload is rsa-hashed vmid, pin, so we have to use shor's to decrypt
    """
    TO IMPLEMENT:

    Full payment flow:
      1. Verify QR code authenticity via ASCON decryption.
      2. Decrypt VMID and PIN from the RSA-encrypted payload.
      3. Forward auth request to the Grid.
      4. Attempt to unlock the charging cable.
      5. If cable unlock fails after a successful payment → trigger refund.

    Edge cases handled:
      - Invalid / tampered QR → reject immediately.
      - Grid rejects (bad PIN / balance / VMID) → inform franchise.
      - Payment approved but hardware fails → call add_reverse_block.
    """
    '''
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)

    if (confirmation == False or fid_from_decrypt != fid):
      print("Payment failed due to invalid QR")
      self.franchise.confirmation(False)
      return

    elif (confirmation == True and fid_from_decrypt == fid):
      vmid = rsa.decrypt_string(payload["VMID_enc"], payload["_rsa_d"], payload["rsa_n"])
      pin = rsa.decrypt_string(payload["PIN_enc"], payload["_rsa_d"], payload["rsa_n"])

      success = self.grid.validate_transaction(fid, vmid, pin, payload["amount"])
      status = self.franchise.confirmation(success, payload["amount"])
      if (success and status == False):
        self.grid.add_reverse_block(uid, fid, payload["amount"])
    '''
    if payload is None:
      print("[Kiosk] Payment aborted — no payload (QR scan failed).")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "No payload exists",
        "transaction_id": None
      }

    fid = self.franchise.fid
    amount = payload["amount"]

    # Step 1: Verify QR Code Authenticity
    print("\n[Step 1] Verifying QR Code...")
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)

    if confirmation is None or confirmation == False or fid_from_decrypt != fid:
      print("✗ Payment FAILED: Invalid or tampered QR code")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "Invalid or tampered QR code",
        "transaction_id": None
      }

    print("✓ QR Code verified")

    # Step 2: Decrypt VMID and PIN from RSA payload
    print("\n[Step 2] Decrypting credentials from RSA payload...")
    try:
      vmid = rsa.decrypt_string(payload["VMID_enc"], payload["_rsa_d"], payload["rsa_n"])
      pin = rsa.decrypt_string(payload["PIN_enc"], payload["_rsa_d"], payload["rsa_n"])
      print(f"✓ Credentials decrypted - VMID: {vmid}, PIN: {pin}")
    except Exception as e:
      print(f"✗ Payment FAILED: Could not decrypt credentials: {e}")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": f"RSA decryption failed: {e}",
        "transaction_id": None
      }

    # Step 3: Forward authorization request to Grid
    print("\n[Step 3] Requesting authorization from Grid Authority...")
    success = self.grid.validate_transaction(fid, vmid, pin, payload["amount"])

    if not success:
      print("✗ Grid Authority REJECTED the transaction")
      print("  Reasons could be: Invalid PIN, Insufficient balance, Unknown VMID")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "Grid Authority rejected transaction",
        "transaction_id": None
      }

    print("✓ Grid Authority APPROVED the transaction")

    # Step 4: Attempt to unlock charging cable
    print("\n[Step 4] Attempting to unlock charging cable...")
    status = self.franchise.confirmation(success, payload["amount"])

    if status is False:
      print("✗ Hardware FAILED: Cable unlock failed after successful payment")
      print("  Triggering automatic refund...")

      # Step 5: Handle hardware failure - trigger refund
      uid = None
      for u_id, user in self.grid.users.items():
        if user.vmid == vmid:
          uid = u_id

      if not uid:
        return {
          "success": False,
          "reason": "UID not found",
          "transaction_id": None
        }
      refund_block = self.grid.add_reverse_block(uid, fid, payload["amount"])

      if refund_block is not None:
        print("✓ Refund processed successfully")
        return {
          "success": False,
          "reason": "Hardware failure - automatic refund triggered",
          "transaction_id": None,
          "refund": True
        }
      else:
        print("✗ Refund FAILED")
        return {
          "success": False,
          "reason": "Hardware failure - refund processing failed",
          "transaction_id": None
        }

    # Payment Success
    print("\n" + "="*60)
    print("✓✓✓ PAYMENT SUCCESSFUL ✓✓✓")
    print("="*60)

    # Step 6: Demonstrate Quantum Vulnerability (Educational)
    print("\n[Step 5] Quantum Cryptography Vulnerability Demonstration")
    print("-" * 60)
    print("Showing how Shor's algorithm breaks the RSA key used for this transaction...")
    try:
      shor_algo.demonstrate_attack(payload)
    except Exception as e:
      print(f"Note: Shor's algorithm demo encountered: {e}")

    print("-" * 60)

    return {
      "success": True,
      "reason": "Payment successful - cable unlocked",
      "transaction_id": self.grid.blockchain[-1]["transaction_id"] if self.grid.blockchain else None,
      "amount": payload["amount"]
    }

if __name__ == "__main__":
  # Self-test would go here
  pass

# --- rsa.py ---
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

# --- user.py ---
import os
import hashlib
import cv2

import rsa

class User:
  def __init__(self, u_name:str, u_phone:int, u_pin:str, u_zone_code, grid, u_balance = 0.0):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance
    self.u_zone_code = u_zone_code
    self.grid = grid

    self.uid = None
    self.vmid = None
    self.req_validation_and_generate_uid()

  def req_validation_and_generate_uid(self):
    confirmation = self.grid.req_user_validation(self)
    if (confirmation == True):
      print(f"User '{self.u_name}' registered with UID: {self.uid}")
    else:
      print("User registration failed")

  def scan_qrcode(self, qrcode_file_name: str):
    """
    The EV Owner scans the QR code displayed on the Kiosk screen.

    Responsibility split:
      - User.scan_qrcode()     : reads the QR image and returns the raw
                                  encoded string. This is the "scan" action.
      - Kiosk.decrypt_qrcode() : receives that raw string and does the
                                  ASCON decryption + FID verification.
                                  The ASCON key is shared between Grid and
                                  Kiosk, not the user — so decryption stays
                                  in Kiosk.

    Returns the raw QR string on success, None on failure.
    """
    if not qrcode_file_name:
      print("QR file name is None.")
      return None

    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    if img is None:
      print(f"Could not read QR image: {qrcode_file_name}")
      return None

    detector = cv2.QRCodeDetector()
    decoded_data, _, _ = detector.detectAndDecode(img)

    if not decoded_data:
      print("QR decode failed — blank or unreadable.")
      return None

    print(f"QR scanned successfully.")
    return decoded_data

  def charge_request(self, qrcode_path, charge_amount:float):
    """
    Prepares an RSA-encrypted payment payload to hand to the Kiosk.

    Per spec the VMID and PIN are transmitted over the network and must
    be encrypted. We use RSA here so that shor.py can demonstrate that
    this classical scheme is breakable with a quantum computer.

    The Grid's public key (e, n) is assumed to be known to the user device
    (e.g. obtained from the kiosk at session start).

    Payload returned:
      QR_path   - path to the scanned QR image
      VMID_enc  - list of RSA-encrypted ordinals of each VMID character
      PIN_enc   - RSA-encrypted PIN integer
      amount    - plaintext (not sensitive; used for billing display)
      rsa_e, rsa_n - public key sent alongside so the receiver can verify
    """
    qr_raw_data = self.scan_qrcode(qrcode_path)
    if qr_raw_data is None:
      print("[User] charge_request aborted — QR scan failed.")
      return None

    rsa_e, rsa_d, rsa_n = rsa.generate_keys()

    payload = {"QR_raw_data": qr_raw_data,
              "VMID_enc" : rsa.encrypt_string(self.vmid, rsa_e, rsa_n),
              "PIN_enc": rsa.encrypt_string(self.u_pin, rsa_e, rsa_n),
              "amount": charge_amount,
              "rsa_e": rsa_e,
              "rsa_n": rsa_n,
              "_rsa_d": rsa_d}
    return payload

  '''
  def decrypt_qrcode(self, qrcode_file_name = None):
    # and verify hash???

    # 1. load and decode the qr code
    # img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    # decoded_objects = decode(img)

    if not qrcode_file_name:
      print("QR file name is None - failed")
      return None, None

    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    detector = cv2.QRCodeDetector()
    decoded_qr_data, _, _ = detector.detectAndDecode(img)

    # print(decoded_qr_data)
    # print(type(decoded_qr_data))

    if not decoded_qr_data:
      print("QR data is None - failed")
      return None, None

    # 2. extract the data
    # for obj in decoded_objects:
    #   scanned_hash = obj.data.decode('utf-8')
    #   print(f"Scanned Hash: {scanned_hash}")
    # data = decoded_object.decode('utf-8')

    # Step 2: Split VFID and timestamp
    try:
      parts = decoded_qr_data.split(", ")
      if len(parts) != 2:
        print("Invalid QR format, line 84")
        return None, None

      vfid_hex = parts[0].strip()
      ts = parts[1].strip()

      # print("Original vfid (first 10 bytes):", self.franchise.vfid[:20])
      # print("Decoded vfid (first 10 bytes):", vfid_hex[:20])
      # print(self.franchise.vfid == vfid_hex)

      vfid_from_decoded_qr = bytes.fromhex(vfid_hex)

    except:
      print("Invalid QR format, line 97")
      return None, None

    try:
      if (ts == self.timestamp):
        # NOTE: To "verify", you must re-hash known data and check if the hashes match.

        key = b"RaksAditPriyVeda"
        nonce = self.timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
        # nonce - number used once; ensures same input != same output and prevents replay attacks
        ad = self.timestamp.encode("utf-8")

        # step: Decrypt
        pt = ascon_decrypt(key, nonce, ad, vfid_from_decoded_qr)
        fid = pt.decode()

        if (fid == self.franchise.fid):
          return True, fid # placeholder
        else:
          raise Exception("FIDs don't match")
          # return False, None # placeholder
      else:
        raise Exception("Timestamps don't match")

    except Exception as e:
      print(f"{e}")
      print("Decryption failed --> tampered QR")
      return None, None
  '''

'''
handoff:
user.scan_qrcode(filename)     --> "abc123..., 12-04-26 14:30:00"
kiosk.decrypt_qrcode(that_str) --> (True, "FID_ABC123")
'''

if __name__ == "__main__":
  from grid      import Grid
  from franchise import Franchise
  from rsa       import decrypt_string

  PASS = "✓"
  FAIL = "✗"

  def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    if not condition:
      raise AssertionError(f"FAILED: {label}")

  print("\n" + "=" * 55)
  print("  user.py — self-test")
  print("=" * 55)

  grid = Grid()
  fr   = Franchise("Station1", "ACC001", "Z1", "pass", 1000, grid)

  # 1. Valid registration
  print("\n[Test 1] Valid user registration")
  u = User("Alice", "9000000001", "1234", "Z1", grid, 500)
  check("UID set",          u.uid  is not None)
  check("VMID set",         u.vmid is not None)
  check("VMID format",      u.vmid == f"{u.uid}_{u.u_phone}")
  check("In grid registry", u.uid in grid.users)
  check("Balance correct",  u.u_balance == 500)

  # 2. Second user — different UID/VMID
  print("\n[Test 2] Second user gets different UID/VMID")
  u2 = User("Bob", "9000000002", "5678", "Z2", grid, 300)
  check("Different UID",  u.uid  != u2.uid)
  check("Different VMID", u.vmid != u2.vmid)

  # 3. None name → validation failure
  print("\n[Test 3] User with None name (validation failure)")
  u_bad = User(None, "9000000003", "0000", "Z1", grid, 100)
  check("UID is None",  u_bad.uid  is None)
  check("VMID is None", u_bad.vmid is None)

  # 4. Payload structure
  print("\n[Test 4] charge_request — payload structure")
  payload = u.charge_request("qrcodes/test.png", 200)
  check("Has QR_raw_data", "QR_raw_data"  in payload)
  check("Has VMID_enc",    "VMID_enc" in payload)
  check("Has PIN_enc",     "PIN_enc"  in payload)
  check("Has amount",      "amount"   in payload)
  check("Has rsa_e",       "rsa_e"    in payload)
  check("Has rsa_n",       "rsa_n"    in payload)
  check("Has _rsa_d",      "_rsa_d"   in payload)
  check("Amount correct",  payload["amount"] == 200)

  # 5. Encrypted fields are lists of ints
  print("\n[Test 5] Encrypted fields are lists of ints")
  check("VMID_enc is list",  isinstance(payload["VMID_enc"], list))
  check("PIN_enc  is list",  isinstance(payload["PIN_enc"],  list))
  check("VMID_enc has ints", all(isinstance(x, int) for x in payload["VMID_enc"]))
  check("PIN_enc  has ints", all(isinstance(x, int) for x in payload["PIN_enc"]))

  # 6. Encrypted ≠ raw bytes
  print("\n[Test 6] Ciphertext differs from raw UTF-8 bytes")
  raw_vmid_bytes = list(u.vmid.encode("utf-8"))
  raw_pin_bytes  = list(u.u_pin.encode("utf-8"))
  check("VMID_enc ≠ raw bytes", payload["VMID_enc"] != raw_vmid_bytes)
  check("PIN_enc  ≠ raw bytes", payload["PIN_enc"]  != raw_pin_bytes)

  # 7. RSA round-trip via decrypt_string
  print("\n[Test 7] RSA round-trip — decrypt_string recovers originals")
  rsa_d = payload["_rsa_d"]
  rsa_n = payload["rsa_n"]
  vmid_dec = decrypt_string(payload["VMID_enc"], rsa_d, rsa_n)
  pin_dec  = decrypt_string(payload["PIN_enc"],  rsa_d, rsa_n)
  check("VMID decrypts correctly", vmid_dec == u.vmid)
  check("PIN  decrypts correctly", pin_dec  == u.u_pin)

  # 8. Different charge amounts
  print("\n[Test 8] Different charge amounts produce different payloads")
  p1 = u.charge_request("qrcodes/test.png", 100)
  p2 = u.charge_request("qrcodes/test.png", 200)
  check("Different amounts in payload", p1["amount"] != p2["amount"])

  # 9. VMID length matches encrypted length (one int per UTF-8 byte)
  print("\n[Test 9] VMID_enc length == len(vmid.encode('utf-8'))")
  check("Length matches", len(payload["VMID_enc"]) == len(u.vmid.encode("utf-8")))

  print("\n" + "=" * 55)
  print("  All user.py tests passed ✓")
  print("=" * 55 + "\n")


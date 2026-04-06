# --- user.py ---
import hashlib

import rsa

class User:
  def __init__(self, u_name:str, u_phone:int, u_pin:str, grid, u_balance = 0.0):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance
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

  def charge_request(self, qrcode_path, charge_amount:int):
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
    rsa_e, _rsa_d, rsa_n = rsa.generate_keys()
    payload = {"QR_path": qrcode_path,
            "VMID_enc": [rsa.encrypt(ord(c), rsa_e, rsa_n) for c in self.vmid],
            "PIN_enc": rsa.encrypt(int(self.u_pin), rsa_e, rsa_n),
            "amount": charge_amount,
            "rsa_e": rsa_e,
            "rsa_n": rsa_n,
            "_rsa_d": _rsa_d}
    return payload

if __name__ == "__main__":
  from grid      import Grid
  from franchise import Franchise
  from rsa       import decrypt

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

  # ── 1. Valid registration ─────────────────────────────────
  print("\n[Test 1] Valid user registration")
  u = User("Alice", "9000000001", "1234", grid, 500)
  check("UID set",            u.uid  is not None)
  check("VMID set",           u.vmid is not None)
  check("VMID format",        u.vmid == f"{u.uid}_{u.u_phone}")
  check("In grid registry",   u.uid in grid.users)
  check("Balance correct",    u.u_balance == 500)

  # ── 2. Second user — different UID ───────────────────────
  print("\n[Test 2] Second user gets different UID/VMID")
  u2 = User("Bob", "9000000002", "5678", grid, 300)
  check("Different UID",  u.uid  != u2.uid)
  check("Different VMID", u.vmid != u2.vmid)

  # ── 3. None field → validation failure ───────────────────
  print("\n[Test 3] User with None name (validation failure)")
  u_bad = User(None, "9000000003", "0000", grid, 100)
  check("UID is None",  u_bad.uid  is None)
  check("VMID is None", u_bad.vmid is None)

  # ── 4. charge_request produces encrypted payload ──────────
  print("\n[Test 4] charge_request — payload structure")
  payload = u.charge_request("qrcodes/test.png", 200)
  check("Has QR_path",   "QR_path"  in payload)
  check("Has VMID_enc",  "VMID_enc" in payload)
  check("Has PIN_enc",   "PIN_enc"  in payload)
  check("Has amount",    "amount"   in payload)
  check("Amount correct", payload["amount"] == 200)

  # ── 5. Encrypted values differ from plaintext ─────────────
  print("\n[Test 5] Encrypted VMID chars are not raw ordinals")
  raw_ords = [ord(c) for c in u.vmid]
  check("VMID_enc differs from raw", payload["VMID_enc"] != raw_ords)

  # ── 6. Decryption recovers original VMID and PIN ──────────
  print("\n[Test 6] RSA round-trip — decrypt recovers originals")
  d, e, n = payload["_rsa_d"], payload["rsa_e"], payload["rsa_n"]
  vmid_dec = "".join(chr(decrypt(c, d, n)) for c in payload["VMID_enc"])
  pin_dec  = str(decrypt(payload["PIN_enc"], d, n))
  check("VMID round-trips", vmid_dec == u.vmid)
  check("PIN  round-trips", pin_dec  == u.u_pin)

  # ── 7. Same user, different charge amounts → different payloads ──
  print("\n[Test 7] Different charge amounts produce different payloads")
  p1 = u.charge_request("qrcodes/test.png", 100)
  p2 = u.charge_request("qrcodes/test.png", 200)
  check("Different amounts in payload", p1["amount"] != p2["amount"])

  print("\n" + "=" * 55)
  print("  All user.py tests passed ✓")
  print("=" * 55 + "\n")

# --- requirements.txt ---
pillow
qrcode
ascon
opencv-python
tabulate

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

  def req_validation_and_reg_w_grid(self):
    confirmation = self.grid.req_fran_validation(self)
    if (confirmation == True):
      print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")
    else:
      print("Franchise validation failed")

    # correction at end:
    # confirmation() adds amount to f_balance regardless of whether the cable was successfully unlocked, which is slightly wrong logically (the balance update should be on the grid side, not the franchise side). Per the spec: "Grid Processing: funds are transferred to the Franchise." So balance update belongs in grid.add_block, not in franchise.confirmation. Remove self.f_balance += amount from confirmation().

  def display_qrcode(self, qrcode_file_name):
    img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    self.qr_code = img
    self.qr_code.show()

  def confirmation(self, success, amount = 0):
    if success:
      # self.f_balance += amount
      print(f"Transaction for {self.f_name} accepted.")
      status = self.unlock_charging_cable(1)
      return status
    else:
      print(f"Transaction for {self.f_name} rejected.")
      return None

  def unlock_charging_cable(self, flag):
    # implement this
    return flag # True if unlocked, False if failed to unlock

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
  fr.confirmation(True, 200)
  # Balance must NOT change here — grid handles it
  check("f_balance unchanged by confirmation()", fr.f_balance == bal_before)

  # ── 4. confirmation() failure path ───────────────────────
  print("\n[Test 4] confirmation() — failure")
  fr.confirmation(False, 200)
  check("f_balance still unchanged", fr.f_balance == bal_before)

  # ── 5. unlock_charging_cable directly ────────────────────
  print("\n[Test 5] unlock_charging_cable()")
  check("Returns True  when flag=True",  fr.unlock_charging_cable(True)  == True)
  check("Returns False when flag=False", fr.unlock_charging_cable(False) == False)

  # ── 6. Two franchises — independent balances ─────────────
  print("\n[Test 6] Two franchises are independent")
  fr2 = Franchise("StationBeta", "ACC003", "Z2", "pwd2", 1000, grid)
  check("Different FIDs",        fr.fid != fr2.fid)
  check("Beta balance correct",  fr2.f_balance == 1000)
  check("Alpha unaffected",      fr.f_balance  == 500)

  print("\n" + "=" * 55)
  print("  All franchise.py tests passed ✓")
  print("=" * 55 + "\n")

# --- code.py ---
# --- user.py ---
import hashlib

import rsa

class User:
  def __init__(self, u_name:str, u_phone:int, u_pin:str, grid, u_balance = 0.0):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance
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

  def charge_request(self, qrcode_path, charge_amount:int):
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
    rsa_e, _rsa_d, rsa_n = rsa.generate_keys()
    payload = {"QR_path": qrcode_path,
            "VMID_enc": [rsa.encrypt(ord(c), rsa_e, rsa_n) for c in self.vmid],
            "PIN_enc": rsa.encrypt(int(self.u_pin), rsa_e, rsa_n),
            "amount": charge_amount,
            "rsa_e": rsa_e,
            "rsa_n": rsa_n,
            "_rsa_d": _rsa_d}
    return payload

if __name__ == "__main__":
  from grid      import Grid
  from franchise import Franchise
  from rsa       import decrypt

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

  # ── 1. Valid registration ─────────────────────────────────
  print("\n[Test 1] Valid user registration")
  u = User("Alice", "9000000001", "1234", grid, 500)
  check("UID set",            u.uid  is not None)
  check("VMID set",           u.vmid is not None)
  check("VMID format",        u.vmid == f"{u.uid}_{u.u_phone}")
  check("In grid registry",   u.uid in grid.users)
  check("Balance correct",    u.u_balance == 500)

  # ── 2. Second user — different UID ───────────────────────
  print("\n[Test 2] Second user gets different UID/VMID")
  u2 = User("Bob", "9000000002", "5678", grid, 300)
  check("Different UID",  u.uid  != u2.uid)
  check("Different VMID", u.vmid != u2.vmid)

  # ── 3. None field → validation failure ───────────────────
  print("\n[Test 3] User with None name (validation failure)")
  u_bad = User(None, "9000000003", "0000", grid, 100)
  check("UID is None",  u_bad.uid  is None)
  check("VMID is None", u_bad.vmid is None)

  # ── 4. charge_request produces encrypted payload ──────────
  print("\n[Test 4] charge_request — payload structure")
  payload = u.charge_request("qrcodes/test.png", 200)
  check("Has QR_path",   "QR_path"  in payload)
  check("Has VMID_enc",  "VMID_enc" in payload)
  check("Has PIN_enc",   "PIN_enc"  in payload)
  check("Has amount",    "amount"   in payload)
  check("Amount correct", payload["amount"] == 200)

  # ── 5. Encrypted values differ from plaintext ─────────────
  print("\n[Test 5] Encrypted VMID chars are not raw ordinals")
  raw_ords = [ord(c) for c in u.vmid]
  check("VMID_enc differs from raw", payload["VMID_enc"] != raw_ords)

  # ── 6. Decryption recovers original VMID and PIN ──────────
  print("\n[Test 6] RSA round-trip — decrypt recovers originals")
  d, e, n = payload["_rsa_d"], payload["rsa_e"], payload["rsa_n"]
  vmid_dec = "".join(chr(decrypt(c, d, n)) for c in payload["VMID_enc"])
  pin_dec  = str(decrypt(payload["PIN_enc"], d, n))
  check("VMID round-trips", vmid_dec == u.vmid)
  check("PIN  round-trips", pin_dec  == u.u_pin)

  # ── 7. Same user, different charge amounts → different payloads ──
  print("\n[Test 7] Different charge amounts produce different payloads")
  p1 = u.charge_request("qrcodes/test.png", 100)
  p2 = u.charge_request("qrcodes/test.png", 200)
  check("Different amounts in payload", p1["amount"] != p2["amount"])

  print("\n" + "=" * 55)
  print("  All user.py tests passed ✓")
  print("=" * 55 + "\n")

# --- requirements.txt ---
pillow
qrcode
ascon
opencv-python
tabulate

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

  def req_validation_and_reg_w_grid(self):
    confirmation = self.grid.req_fran_validation(self)
    if (confirmation == True):
      print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")
    else:
      print("Franchise validation failed")

    # correction at end:
    # confirmation() adds amount to f_balance regardless of whether the cable was successfully unlocked, which is slightly wrong logically (the balance update should be on the grid side, not the franchise side). Per the spec: "Grid Processing: funds are transferred to the Franchise." So balance update belongs in grid.add_block, not in franchise.confirmation. Remove self.f_balance += amount from confirmation().

  def display_qrcode(self, qrcode_file_name):
    img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    self.qr_code = img
    self.qr_code.show()

  def confirmation(self, success, amount = 0):
    if success:
      # self.f_balance += amount
      print(f"Transaction for {self.f_name} accepted.")
      status = self.unlock_charging_cable(1)
      return status
    else:
      print(f"Transaction for {self.f_name} rejected.")
      return None

  def unlock_charging_cable(self, flag):
    # implement this
    return flag # True if unlocked, False if failed to unlock

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
  fr.confirmation(True, 200)
  # Balance must NOT change here — grid handles it
  check("f_balance unchanged by confirmation()", fr.f_balance == bal_before)

  # ── 4. confirmation() failure path ───────────────────────
  print("\n[Test 4] confirmation() — failure")
  fr.confirmation(False, 200)
  check("f_balance still unchanged", fr.f_balance == bal_before)

  # ── 5. unlock_charging_cable directly ────────────────────
  print("\n[Test 5] unlock_charging_cable()")
  check("Returns True  when flag=True",  fr.unlock_charging_cable(True)  == True)
  check("Returns False when flag=False", fr.unlock_charging_cable(False) == False)

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

  def decrypt_qrcode(self, qrcode_file_name):
    # and verify hash???

    # 1. load and decode the qr code
    # img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    # decoded_objects = decode(img)

    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    detector = cv2.QRCodeDetector()
    decoded_qr_data, _, _ = detector.detectAndDecode(img)

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

  def process_payment(self, qrcode_file_name, uid, fid, payload, amount):
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
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)

    if (confirmation == False):
      print("Payment failed due to invalid QR")

    elif (confirmation == True and fid_from_decrypt == fid):
      vmid = "".join(chr(rsa.decrypt(n, payload["_rsa_d"], payload["rsa_n"])) for n in payload["VMID_enc"])
      pin = str(rsa.decrypt(payload["PIN_enc"], payload["_rsa_d"], payload["rsa_n"]))
      success = self.grid.validate_transaction(fid, vmid, pin, amount)
      status = self.franchise.confirmation(success, amount)
      if (success and status == False):
        self.grid.add_reverse_block(uid, fid, amount)

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
    table.append([u.uid, u.u_name, u.u_phone, u.u_balance])

  print("\n--- USERS ---")
  print(tabulate(table, headers=["UID", "Name", "Phone", "Balance"], tablefmt="grid"))

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
  user = User("Rakshita", 9999999999, "1234", grid, 1000)

  # Create franchise
  fr = Franchise("Station1", "ACC123", "Z1", "pass", 500, grid)

  # Create kiosk
  kiosk = Kiosk(grid, fr)

  # Generate QR
  kiosk.generate_qrcode()

  # Simulate payment (use filename from QR generation)
  payload = user.charge_request(f"qrcode_xxxxxx{fr.vfid[-6:]}.png", 100)
  kiosk.process_payment(f"qrcode_xxxxxx{fr.vfid[-6:]}.png", user.uid, fr.fid, payload, 100)

  # Call printers
  # print_users(grid)
  display_users(grid)

  # print_franchises(grid)
  display_franchises(grid)

  # print_blockchain(grid)
  display_blockchain(grid)


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

        key, nonce, pt, ad = get_key_nonce_pt_ad(fid, timestamp)

        req_fields = [key, nonce, pt, ad]
        if all(x is not None for x in req_fields):
          # step: Decrypt
          pt = ascon_decrypt(key, nonce, ad, vfid_from_decoded_qr)
          fid = pt.decode()

          if (fid == self.franchise.fid):
            return True, fid # placeholder
          else:
            raise Exception("FIDs don't match")
            # return False, None # placeholder
        else:
          return Exception("Decryption failed - something in req_fields is None")
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
  u = User("Alice", 9000000001, "1234", "Z1", grid, 500)
  check("UID set",          u.uid  is not None)
  check("VMID set",         u.vmid is not None)
  check("VMID format",      u.vmid == f"{u.uid}_{u.u_phone}")
  check("In grid registry", u.uid in grid.users)
  check("Balance correct",  u.u_balance == 500)

  # 2. Second user — different UID/VMID
  print("\n[Test 2] Second user gets different UID/VMID")
  u2 = User("Bob", 9000000002, "5678", "Z2", grid, 300)
  check("Different UID",  u.uid  != u2.uid)
  check("Different VMID", u.vmid != u2.vmid)

  # 3. None name --> validation failure
  print("\n[Test 3] User with None name (validation failure)")
  u_bad = User(None, 9000000003, "0000", "Z1", grid, 100)
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

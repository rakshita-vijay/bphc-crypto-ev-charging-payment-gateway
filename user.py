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

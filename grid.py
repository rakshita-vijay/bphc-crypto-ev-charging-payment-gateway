import os
import datetime
import hashlib
from ascon_lwc import ascon_encrypt
import json

class Grid:
  def __init__(self):
    self.providers = ["Tata", "Adani", "ChargePoint"]
    self.zones = {"Z1": "Tata", "Z2": "Tata", "Z3": "Tata", # f_zone_code, provider_name
                  "Z4": "Adani", "Z5": "Adani", "Z6": "Adani",
                  "Z7": "ChargePoint", "Z8": "ChargePoint", "Z9": "ChargePoint"}
    self.users = {} # uid, user_obj
    self.franchises = {} # fid, fran_obj
    self.blockchain = [] # block dicts

  def sha3_algo(self, message):
    # can we just import it? or should we code it out? - importing. DONE
    try:
      return hashlib.sha3_256(message.encode("utf-8")).hexdigest()
    except:
      return "Could not hash"
    # this returns hex code

  def generate_fid(self, f_name, f_time_acc_create, f_pwd):
    message = f"{f_name}, {f_time_acc_create}, {f_pwd}"
    return self.sha3_algo(message)[:16]
    # fid - unique to every station and shouldn’t be shared

  def generate_vfid(self, fid, timestamp):
    # implement using lwc algo, below is placeholder
    key = b"RaksAditPriyVeda"
    nonce = timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
    # nonce - number used once; ensures same input != same output and prevents replay attacks
    pt = fid.encode("utf-8") # actua data to protect
    ad = timestamp.encode("utf-8")
    # associated data is: data that is NOT encrypted, but is authenticated
    # timestamp is not hidden but cannot be tampered with
    vfid = ascon_encrypt(key, nonce, ad, pt)

    return vfid.hex()

  def req_fran_validation(self, f_obj = None):
    req_fields = [f_obj.f_name, f_obj.f_pwd, f_obj.f_balance, f_obj.f_time_acc_create]

    if f_obj.f_zone_code in self.zones and all(x is not None for x in req_fields):
      return self.register_franchise(f_obj)
    else:
      return False

  def req_user_validation(self, u_obj = None):
    req_fields = [u_obj.u_name, u_obj.u_phone, u_obj.u_pin, u_obj.u_balance]

    if u_obj.u_zone_code in self.zones and all(x is not None for x in req_fields):
      return self.register_user(u_obj)
    else:
      return False

  def register_franchise(self, franchise):
    fid = self.generate_fid(franchise.f_name, franchise.f_time_acc_create, franchise.f_pwd)
    franchise.fid = fid
    # franchise.grid = self
    self.franchises[franchise.fid] = franchise
    return True

  def register_user(self, user):
    message = f"{user.u_name}, {user.u_phone}, {user.u_pin}"
    uid = self.sha3_algo(message)[:16] # unique to every station and shouldn’t be shared
    user.uid = uid
    user.vmid = f"{uid}_{user.u_phone}"
    # user.grid = self
    self.users[user.uid] = user
    return True

  def validate_transaction(self, fid, vmid, pin, amount):
    if fid not in self.franchises:
      print("FID not found in franchises")
      return False

    for user in self.users.values():
      if user.vmid == vmid and user.u_pin == pin:
        if user.u_balance >= amount:
          user.u_balance -= amount
          self.franchises[fid].f_balance += amount

          ts = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
          bl = self.add_block(user.uid, fid, ts, amount)
          if (bl == None):
            print(f"Block of FID {fid} representing a successful transaction could not be added to blockchain")
            return False
          return True
    return False

  # Add to grid.py
  def save_blockchain(self):
      import json
      with open("blockchain_ledger.json", "w") as f:
          json.dump(self.blockchain, f, indent=2)

  def load_blockchain(self):
      import json
      try:
          with open("blockchain_ledger.json", "r") as f:
              self.blockchain = json.load(f)
      except FileNotFoundError:
          self.blockchain = []

  def add_block(self, uid, fid, timestamp, amount, dispute = False): # disp_flag : T for a refund block
    try:
      t_id_msg = f"{uid}, {fid}, {timestamp}, {amount}"
      prev_hash = self.blockchain[-1]["transaction_id"] if len(self.blockchain) > 0 else ("0" * 64)
      block = {
                "transaction_id" : self.sha3_algo(t_id_msg),
                "prev_block_hash" : prev_hash,
                "timestamp" : timestamp,
                "uid" : uid,
                "fid" : fid,
                "amount" : amount,
                "dispute_flag" : dispute
              }
      self.blockchain.append(block)
      self.save_blockchain() # save after every new block
      x = "successful transaction" if dispute == False else "refund"
      print(f"Block of FID {fid} representing a {x} added to blockchain")
      return block
    except:
      return None

  def process_refund(self, uid, fid, amount):
    if fid not in self.franchises:
      print("FID not found in franchises")
      return None

    for user in self.users.values():
      if user.uid == uid:
        user.u_balance += amount
        self.franchises[fid].f_balance -= amount
        ts = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
        return ts

    return None

  def add_reverse_block(self, uid, fid, amount, dispute = True):
    # called when payment succeeds but hardware fails to dispense power. reverses the balance and records a dispute block.
    ts = self.process_refund(uid, fid, amount)
    if ts is None:
      print("Refund failed - either FID or user not found")
      return None

    return self.add_block(uid, fid, ts, amount, True)

  def verify_chain(self):
    """
    Walks every block and checks:
      1. txn_id matches a fresh SHA3 of its own data fields.
      2. prev_hash matches the txn_id of the preceding block.
    Returns True if chain is intact, False if tampered.
    """
    for i, block in enumerate(self.blockchain):
      expected_txid = self.sha3_algo(
        f"{block['uid']}, {block['fid']}, {block['timestamp']}, {block['amount']}"
      )
      if block["transaction_id"] != expected_txid:
        print(f"[Chain] TAMPERED at block {i} — txn_id mismatch!")
        return False

      expected_prev = self.blockchain[i - 1]["transaction_id"] if i > 0 else "0" * 64
      if block["prev_block_hash"] != expected_prev:
        print(f"[Chain] BROKEN LINK at block {i} — prev_hash mismatch!")
        return False

    print(f"[Chain] Chain intact — {len(self.blockchain)} block(s) verified.")
    return True

if __name__ == "__main__":
  # Import here to avoid circular imports at module level
  from user import User
  from franchise import Franchise

  PASS = "✓ "
  FAIL = "✗"

  def check(label, condition):
    status = PASS if condition else FAIL
    print(f"  [{status}] {label}")
    if not condition:
      raise AssertionError(f"FAILED: {label}")

  print("\n" + "=" * 55)
  print("  grid.py — self-test")
  print("=" * 55)

  grid = Grid()

  # ── 1. Valid franchise registration ──────────────────────
  print("\n[Test 1] Valid franchise registration")
  fr1 = Franchise("StationAlpha", "ACC001", "Z1", "secret", 1000, grid)
  check("FID is set",           fr1.fid is not None)
  check("FID is 16 chars",      len(fr1.fid) == 16)
  check("Franchise in registry", fr1.fid in grid.franchises)

  # ── 2. Invalid zone code ──────────────────────────────────
  print("\n[Test 2] Franchise with invalid zone code (Z9)")
  fr_bad = Franchise("BadStation", "ACC002", "Z9", "secret", 500, grid)
  check("FID is None for bad zone", fr_bad.fid is None)
  check("Not in registry",          fr_bad.fid not in grid.franchises)

  # ── 3. Valid user registration ────────────────────────────
  print("\n[Test 3] Valid user registration")
  u1 = User("Alice", "9000000001", "4321", grid, 800)
  check("UID is set",   u1.uid  is not None)
  check("VMID is set",  u1.vmid is not None)
  check("VMID format",  u1.vmid == f"{u1.uid}_{u1.u_phone}")
  check("User in registry", u1.uid in grid.users)

  # ── 4. User missing required field ───────────────────────
  print("\n[Test 4] User with None name (should fail validation)")
  u_bad = User(None, "9000000002", "0000", grid, 100)
  check("UID is None",  u_bad.uid  is None)
  check("VMID is None", u_bad.vmid is None)

  # ── 5. Valid transaction ──────────────────────────────────
  print("\n[Test 5] Valid transaction (₹200)")
  bal_u_before  = u1.u_balance
  bal_fr_before = fr1.f_balance
  ok = grid.validate_transaction(fr1.fid, u1.vmid, u1.u_pin, 200)
  check("Returns True",                 ok)
  check("User balance deducted",        u1.u_balance  == bal_u_before  - 200)
  check("Franchise balance credited",   fr1.f_balance == bal_fr_before + 200)
  check("Block added to chain",         len(grid.blockchain) == 1)
  check("Block has correct amount",     grid.blockchain[-1]["amount"] == 200)
  check("Block not a refund",           grid.blockchain[-1]["dispute_flag"] == False)

  # ── 6. Insufficient balance ───────────────────────────────
  print("\n[Test 6] Insufficient balance (₹99999)")
  ok = grid.validate_transaction(fr1.fid, u1.vmid, u1.u_pin, 99999)
  check("Returns False",                not ok)
  check("No new block added",           len(grid.blockchain) == 1)

  # ── 7. Wrong PIN ──────────────────────────────────────────
  print("\n[Test 7] Wrong PIN")
  ok = grid.validate_transaction(fr1.fid, u1.vmid, "WRONG", 50)
  check("Returns False", not ok)

  # ── 8. Unknown FID ────────────────────────────────────────
  print("\n[Test 8] Unknown FID")
  ok = grid.validate_transaction("FAKEFID000000000", u1.vmid, u1.u_pin, 50)
  check("Returns False", not ok)

  # ── 9. Second franchise and cross-payment ────────────────
  print("\n[Test 9] Second franchise (Z2), second user, cross-payment")
  fr2 = Franchise("StationBeta", "ACC003", "Z2", "pwd2", 0, grid)
  u2  = User("Bob", "9000000003", "9999", grid, 300)
  ok  = grid.validate_transaction(fr2.fid, u2.vmid, u2.u_pin, 150)
  check("Returns True",               ok)
  check("Bob's balance is 150",       u2.u_balance  == 150)
  check("Beta franchise credited",    fr2.f_balance == 150)
  check("Second block added",         len(grid.blockchain) == 2)

  # ── 10. Reverse block (refund) ────────────────────────────
  print("\n[Test 10] Reverse block — hardware failure after payment")
  # First make a payment to refund
  grid.validate_transaction(fr1.fid, u1.vmid, u1.u_pin, 100)
  bal_u  = u1.u_balance
  bal_fr = fr1.f_balance
  grid.add_reverse_block(u1.uid, fr1.fid, 100)
  check("User refunded",              u1.u_balance  == bal_u  + 100)
  check("Franchise debited",          fr1.f_balance == bal_fr - 100)
  check("Refund block has flag=True", grid.blockchain[-1]["dispute_flag"] == True)

  # ── 11. Reverse block with bad UID ────────────────────────
  print("\n[Test 11] Reverse block with unknown UID")
  result = grid.add_reverse_block("BADUID000000000", fr1.fid, 50)
  check("Returns None", result is None)

  # ── 12. Reverse block with bad FID ────────────────────────
  print("\n[Test 12] Reverse block with unknown FID")
  result = grid.add_reverse_block(u1.uid, "BADFID000000000", 50)
  check("Returns None", result is None)

  # ── 13. Chain integrity ───────────────────────────────────
  print("\n[Test 13] Chain integrity — unmodified")
  check("Chain valid", grid.verify_chain())

  # ── 14. Tamper detection ──────────────────────────────────
  print("\n[Test 14] Tamper detection — modify block amount")
  original_amount = grid.blockchain[0]["amount"]
  grid.blockchain[0]["amount"] = 999999
  check("Chain detects tampering", not grid.verify_chain())
  grid.blockchain[0]["amount"] = original_amount  # restore

  # ── 15. VFID generation ───────────────────────────────────
  print("\n[Test 15] VFID generation via ASCON")
  ts   = "01-04-26 12:00:00"
  vfid = grid.generate_vfid(fr1.fid, ts)
  check("VFID is a hex string",      isinstance(vfid, str))
  check("Different fid → diff vfid", grid.generate_vfid(fr2.fid, ts) != vfid)
  check("Different ts → diff vfid",  grid.generate_vfid(fr1.fid, "02-04-26 12:00:00") != vfid)

  print("\n" + "=" * 55)
  print("  All grid.py tests passed ✓")
  print("=" * 55 + "\n")


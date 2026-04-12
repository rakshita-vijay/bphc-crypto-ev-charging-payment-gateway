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
  print("\n" + "~"*65)
  print("  Centralized EV Charging Payment Gateway — Full Demo")
  print("~"*65)

  # ────────────────────────────────────────────────────────────
  print("1. Grid Initialization — 3 providers, 9 zones")
  # ────────────────────────────────────────────────────────────
  grid = Grid()
  print(f"[Grid] Zones: {list(grid.zones.keys())}")

  # ────────────────────────────────────────────────────────────
  print("2. Franchise Registrations (one per zone)")
  # ────────────────────────────────────────────────────────────
  fr_z1 = Franchise("PowerStop_Hyd",     "ACC001", "Z1", "pwd1", 5000, grid)
  fr_z4 = Franchise("ChargeHub_Del",     "ACC004", "Z4", "pwd4", 3000, grid)
  fr_z7 = Franchise("VoltPoint_Mum",     "ACC007", "Z7", "pwd7", 8000, grid)

  print("\n[Scenario] Invalid zone code (Z99):")
  fr_bad = Franchise("GhostStation", "ACC999", "Z99", "badpwd", 100, grid)
  assert fr_bad.fid is None
  print("  → Correctly rejected.")
  display_franchises(grid)

  # ────────────────────────────────────────────────────────────
  print("3. User Registrations (no zone restriction)")
  # ────────────────────────────────────────────────────────────
  u1 = User("Rakshita", 9999999991, "1234", "Z1", grid, 1000)
  u2 = User("Aditya",   9999999992, "5678", "Z2", grid, 500)
  u3 = User("Priya",    9999999993, "4321", "Z3", grid, 250)
  u4 = User("Vedant",   9999999994, "9999", "Z4", grid, 0)     # zero balance

  print("\n[Scenario] None name → rejected:")
  u_bad = User(None, 0000000000, "0000", "Z0", grid, 100)
  assert u_bad.uid is None
  print("  → Correctly rejected.")
  display_users(grid)

  # ────────────────────────────────────────────────────────────
  print("4. Kiosk Setup & QR Generation")
  # ────────────────────────────────────────────────────────────
  kiosk_z1 = Kiosk(grid, fr_z1)
  kiosk_z4 = Kiosk(grid, fr_z4)
  kiosk_z7 = Kiosk(grid, fr_z7)

  kiosk_z1.generate_qrcode()
  kiosk_z4.generate_qrcode()
  kiosk_z7.generate_qrcode()

  qr_z1 = f"qrcode_xxxxxx{fr_z1.vfid[-6:]}.png"
  qr_z4 = f"qrcode_xxxxxx{fr_z4.vfid[-6:]}.png"
  qr_z7 = f"qrcode_xxxxxx{fr_z7.vfid[-6:]}.png"

  # ────────────────────────────────────────────────────────────
  print("5. Successful Payments (cross-zone allowed)")
  # ────────────────────────────────────────────────────────────
  print("\n[A] Rakshita → Z1/Tata (₹200)")
  r = kiosk_z1.process_payment(u1.charge_request(qr_z1, 200))
  assert r["success"] and u1.u_balance == 800 and fr_z1.f_balance == 5200

  print("\n[B] Aditya → Z4/Adani (₹150)")
  r = kiosk_z4.process_payment(u2.charge_request(qr_z4, 150))
  assert r["success"] and u2.u_balance == 350 and fr_z4.f_balance == 3150

  print("\n[C] Priya → Z7/ChargePoint (₹100)")
  r = kiosk_z7.process_payment(u3.charge_request(qr_z7, 100))
  assert r["success"] and u3.u_balance == 150 and fr_z7.f_balance == 8100

  print("\n[D] Rakshita charges again at Z1 (₹300)")
  r = kiosk_z1.process_payment(u1.charge_request(qr_z1, 300))
  assert r["success"] and u1.u_balance == 500

  print("\n[E] Aditya charges at Z1 (cross-provider, still valid)")
  r = kiosk_z1.process_payment(u2.charge_request(qr_z1, 100))
  assert r["success"] and u2.u_balance == 250

  # ────────────────────────────────────────────────────────────
  print("6. Edge Cases — Failed Payments")
  # ────────────────────────────────────────────────────────────
  print("\n[Edge 1] Vedant (₹0 balance) tries ₹100:")
  r = kiosk_z1.process_payment(u4.charge_request(qr_z1, 100))
  assert not r["success"] and u4.u_balance == 0
  print("  → Correctly rejected.")

  print("\n[Edge 2] Wrong PIN:")
  from rsa import generate_keys, encrypt_string
  e2, d2, n2  = generate_keys()
  raw_z1      = u2.scan_qrcode(qr_z1)
  bad_payload = {
    "QR_raw_data" : raw_z1,
    "VMID_enc"    : encrypt_string(u2.vmid, e2, n2),
    "PIN_enc"     : encrypt_string("0000", e2, n2),
    "amount"      : 50,
    "rsa_e": e2, "rsa_n": n2, "_rsa_d": d2,
  }
  r = kiosk_z1.process_payment(bad_payload)
  assert not r["success"]
  print("  → Correctly rejected.")

  print("\n[Edge 3] Priya overspend (has ₹150, requests ₹200):")
  r = kiosk_z7.process_payment(u3.charge_request(qr_z7, 200))
  assert not r["success"] and u3.u_balance == 150
  print("  → Correctly rejected.")

  print("\n[Edge 4] None payload (scan failed):")
  r = kiosk_z1.process_payment(None)
  assert not r["success"]
  print("  → Cleanly aborted.")

  print("\n[Edge 5] Tampered QR string in payload:")
  t_payload = u1.charge_request(qr_z1, 50)
  t_payload["QR_raw_data"] = f"deadbeef0000000000000000, {kiosk_z1.timestamp}"
  r = kiosk_z1.process_payment(t_payload)
  assert not r["success"]
  print("  → Correctly rejected.")

  print("\n[Edge 6] Replay attack — stale timestamp:")
  old_ts   = "01-01-20 00:00:00"
  old_vfid = grid.generate_vfid(fr_z1.fid, old_ts)
  r_payload = u1.charge_request(qr_z1, 50)
  r_payload["QR_raw_data"] = f"{old_vfid}, {old_ts}"
  r = kiosk_z1.process_payment(r_payload)
  assert not r["success"]
  print("  → Correctly rejected.")

  # ────────────────────────────────────────────────────────────
  print("7. Hardware Failure → Refund (Reverse Block)")
  # ────────────────────────────────────────────────────────────
  print("\n[Edge 7] Rakshita pays ₹100 but cable fails:")
  bal_u_pre  = u1.u_balance
  bal_fr_pre = fr_z1.f_balance
  fr_z1.hardware_failure_rate = 1.0   # force failure
  r = kiosk_z1.process_payment(u1.charge_request(qr_z1, 100))
  fr_z1.hardware_failure_rate = 0.0   # restore
  assert r.get("refund") == True
  assert u1.u_balance  == bal_u_pre,  "User should be fully refunded"
  assert fr_z1.f_balance == bal_fr_pre, "Franchise should be debited back"
  assert grid.blockchain[-1]["dispute_flag"] == True
  print("  → Refund processed. Dispute block recorded.")

  # ────────────────────────────────────────────────────────────
  print("8. Shor's Algorithm Demo")
  # ────────────────────────────────────────────────────────────
  print("\n[Standalone demo] Weak key (p=61, q=53):")
  demonstrate_attack()

  print("\n[Real payload attack] Intercepting Aditya's next payment:")
  demonstrate_attack(u2.charge_request(qr_z4, 50))

  # ────────────────────────────────────────────────────────────
  print("9. Blockchain Ledger & Chain Verification")
  # ────────────────────────────────────────────────────────────
  display_blockchain(grid)
  valid = grid.verify_chain()
  print(f"\n[Chain] Integrity: {'PASS ✓' if valid else 'FAIL ✗'}")
  assert valid

  # ────────────────────────────────────────────────────────────
  print("10. Final Balances")
  # ────────────────────────────────────────────────────────────
  display_users(grid)
  display_franchises(grid)

  print("\n" + "~"*65)
  print("  Demo complete.")
  print("~"*65 + "\n")

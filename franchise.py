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

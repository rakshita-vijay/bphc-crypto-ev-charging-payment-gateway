import os
import datetime
import hashlib
import random
from PIL import Image

class Franchise:
  def __init__(self, f_name, f_acc_num, f_zone_code, f_pwd, f_balance, grid):
    self.f_name = f_name
    self.f_acc_num = f_acc_num
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    self.grid = grid
    self.fid = None
    self.req_validation_and_reg_w_grid()
    self.vfid = None
    self.qr_code = None
    self.hardware_failure_rate = 0.0  # 0-1 probability of hardware failure

  def req_validation_and_reg_w_grid(self):
    """Register franchise with Grid Authority"""
    confirmation = self.grid.req_fran_validation(self)
    if confirmation == True:
      print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")
    else:
      print("Franchise validation failed")

  def display_qrcode(self, qrcode_file_name):
    """Display the generated QR code"""
    try:
      img = Image.open(os.path.join("qrcodes", qrcode_file_name))
      self.qr_code = img
      print(f"QR Code displayed: {qrcode_file_name}")
      # In Streamlit, this will be handled differently
      # self.qr_code.show()
    except Exception as e:
      print(f"Error displaying QR code: {e}")

  def confirmation(self, success, amount=0):
    """
    Process transaction confirmation from Grid Authority.
    If successful, attempt to unlock the charging cable.
    
    Args:
        success: Boolean indicating if Grid approved the transaction
        amount: Transaction amount
    
    Returns:
        True if cable unlocked successfully
        False if cable unlock failed (hardware failure)
        None if transaction was rejected by Grid
    """
    if success:
      print(f"\n✓ Transaction for {self.f_name} ACCEPTED (Amount: {amount})")
      print("  Attempting to unlock charging cable...")
      
      # Simulate cable unlock
      status = self.unlock_charging_cable()
      
      if status:
        print(f"✓ Charging cable UNLOCKED successfully for {self.f_name}")
        return True
      else:
        print(f"✗ Charging cable UNLOCK FAILED for {self.f_name}")
        print("  Hardware failure detected - refund will be triggered")
        return False
    else:
      print(f"\n✗ Transaction for {self.f_name} REJECTED")
      return None

  def unlock_charging_cable(self):
    """
    Simulate charging cable unlock mechanism.
    
    This function simulates the hardware operation of unlocking the
    charging cable at the EV charging station. In a real system, this
    would communicate with physical hardware.
    
    Success/Failure scenarios:
    - Normal operation: Cable unlocks successfully (configurable success rate)
    - Hardware failure: Cable mechanism jams or fails to unlock
    - Connection timeout: Unable to reach hardware controller
    
    Returns:
        True if cable unlocked successfully
        False if hardware fails to unlock (triggers automatic refund)
    """
    try:
      # Log the unlock attempt
      timestamp = datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")
      print(f"  [Hardware] Unlock attempt at {timestamp}")
      
      # Simulate network latency
      import time
      time.sleep(0.1)
      
      # Simulate hardware failure with configurable probability
      # hardware_failure_rate: 0.0 = always succeed, 1.0 = always fail
      failure_random = random.random()
      
      if failure_random < self.hardware_failure_rate:
        print(f"  [Hardware] ✗ Cable unlock mechanism FAILED (simulated failure)")
        return False
      
      # Simulate occasional random failures (1% chance by default if not configured)
      if self.hardware_failure_rate == 0.0 and random.random() < 0.01:
        print(f"  [Hardware] ✗ Unexpected hardware failure (1% random chance)")
        return False
      
      # Cable unlock succeeds
      print(f"  [Hardware] ✓ Cable unlock mechanism SUCCEEDED")
      print(f"  [Hardware] Charging session active - User can now charge vehicle")
      
      return True
      
    except Exception as e:
      print(f"  [Hardware] ✗ Cable unlock error: {e}")
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
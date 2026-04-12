"""
Integration tests for the EV Charging Payment Gateway.
Tests the complete payment flow from user registration to blockchain verification.
"""

import sys
from grid import Grid
from user import User
from franchise import Franchise
from kiosk import Kiosk
import datetime

PASS = "✓"
FAIL = "✗"

def check(label, condition):
  status = PASS if condition else FAIL
  print(f"  [{status}] {label}")
  if not condition:
    raise AssertionError(f"FAILED: {label}")

def test_complete_payment_flow():
  """Test: User registers --> Franchise registers --> Generate QR --> Process payment"""
  print("\n" + "=" * 70)
  print("  INTEGRATION TEST: Complete Payment Flow")
  print("=" * 70)

  # Setup
  print("\n[Setup] Initializing Grid Authority...")
  grid = Grid()
  check("Grid initialized", grid is not None)

  # Step 1: User Registration
  print("\n[Step 1] User Registration")
  user = User("Alice", 9000000001, "1234", "Z1", grid, 1000)
  check("User UID generated", user.uid is not None)
  check("User VMID generated", user.vmid is not None)
  check("User registered in grid", user.uid in grid.users)
  check("User balance correct", user.u_balance == 1000)

  # Step 2: Franchise Registration
  print("\n[Step 2] Franchise Registration")
  franchise = Franchise("ChargingStation_Zone1", "ACC001", "Z1", "pass123", 500, grid)
  check("Franchise FID generated", franchise.fid is not None)
  check("Franchise registered in grid", franchise.fid in grid.franchises)
  check("Franchise balance correct", franchise.f_balance == 500)

  # Step 3: Kiosk Creation & QR Generation
  print("\n[Step 3] QR Code Generation")
  kiosk = Kiosk(grid, franchise)
  kiosk.generate_qrcode()
  check("QR code generated", franchise.vfid is not None)
  check("Kiosk timestamp set", kiosk.timestamp is not None)

  # Step 4: User Charge Request
  print("\n[Step 4] User Payment Request (RSA Encryption)")
  qr_filename = f"qrcode_xxxxxx{franchise.vfid[-6:]}.png"
  payload = user.charge_request(qr_filename, 200)
  check("Payload has VMID_enc", "VMID_enc" in payload)
  check("Payload has PIN_enc", "PIN_enc" in payload)
  check("Payload has amount", payload["amount"] == 200)

  # Step 5: Process Payment
  print("\n[Step 5] Process Payment")
  result = kiosk.process_payment(payload) # single arg
  check("Result returned", result is not None)
  check("Payment successful", result["success"] == True)

  # Step 6: Verify Balances Updated
  print("\n[Step 6] Balance Verification")
  check("User balance deducted", user.u_balance == 800) # 1000 - 200
  check("Franchise balance credited", franchise.f_balance == 700) # 500 + 200

  # Step 7: Verify Blockchain
  print("\n[Step 7] Blockchain Verification")
  check("Transaction recorded in blockchain", len(grid.blockchain) == 1)
  check("Block has correct amount", grid.blockchain[0]["amount"] == 200)
  check("Block marked as not dispute", grid.blockchain[0]["dispute_flag"] == False)

  # Step 8: Verify Chain Integrity
  print("\n[Step 8] Chain Integrity Check")
  chain_valid = grid.verify_chain()
  check("Blockchain chain is intact", chain_valid == True)

  print("\n" + "=" * 70)
  print("  ✓ INTEGRATION TEST PASSED")
  print("=" * 70 + "\n")

def test_insufficient_balance():
  """Test: Payment rejected due to insufficient balance"""
  print("\n" + "=" * 70)
  print("  TEST: Insufficient Balance")
  print("=" * 70)

  grid = Grid()
  user = User("Bob", 9000000002, "5678", "Z2", grid, 100)  # Only 100 balance
  franchise = Franchise("ChargingStation_Zone2", "ACC002", "Z2", "pass456", 500, grid)

  kiosk = Kiosk(grid, franchise)
  kiosk.generate_qrcode()

  qr_filename = f"qrcode_xxxxxx{franchise.vfid[-6:]}.png"
  payload = user.charge_request(qr_filename, 500)  # Trying to charge 500 but only has 100

  result = kiosk.process_payment(payload)
  check("Payment rejected", result["success"] == False)
  check("Reason is insufficient balance", "Grid Authority rejected" in result["reason"])
  check("User balance unchanged", user.u_balance == 100)
  check("No blockchain entry created", len(grid.blockchain) == 0)

  print("\n" + "=" * 70)
  print("  ✓ INSUFFICIENT BALANCE TEST PASSED")
  print("=" * 70 + "\n")

def test_wrong_pin():
  """Test: Payment rejected due to wrong PIN"""
  print("\n" + "=" * 70)
  print("  TEST: Wrong PIN")
  print("=" * 70)

  grid = Grid()
  user = User("Charlie", 9000000003, "1111", "Z3", grid, 500)
  franchise = Franchise("ChargingStation_Zone3", "ACC003", "Z3", "pass789", 500, grid)

  kiosk = Kiosk(grid, franchise)
  kiosk.generate_qrcode()

  qr_filename = f"qrcode_xxxxxx{franchise.vfid[-6:]}.png"
  payload = user.charge_request(qr_filename, 200)

  # Manually corrupt the PIN in payload (simulate wrong PIN)
  import rsa as rsa_module
  payload["PIN_enc"] = rsa_module.encrypt_string("9999", payload["rsa_e"], payload["rsa_n"])

  result = kiosk.process_payment(payload)
  check("Payment rejected", result["success"] == False)
  check("User balance unchanged", user.u_balance == 500)

  print("\n" + "=" * 70)
  print("  ✓ WRONG PIN TEST PASSED")
  print("=" * 70 + "\n")

def test_hardware_failure_refund():
  """Test: Hardware failure after payment --> automatic refund"""
  print("\n" + "=" * 70)
  print("  TEST: Hardware Failure with Auto-Refund")
  print("=" * 70)

  grid = Grid()
  user = User("Diana", 9000000004, "2222", "Z4", grid, 1000)
  franchise = Franchise("ChargingStation_Zone1", "ACC004", "Z1", "pass111", 500, grid)

  # Configure franchise to fail hardware unlock
  franchise.hardware_failure_rate = 1.0

  kiosk = Kiosk(grid, franchise)
  kiosk.generate_qrcode()

  qr_filename = f"qrcode_xxxxxx{franchise.vfid[-6:]}.png"
  payload = user.charge_request(qr_filename, 300)

  result = kiosk.process_payment(payload)

  check("Payment indicates hardware failure", "Hardware failure" in result["reason"])
  check("Refund was triggered", result.get("refund") == True)
  check("User refunded", user.u_balance == 1000)  # Back to original
  check("Franchise debited", franchise.f_balance == 500)  # Back to original
  check("Two blockchain entries (transaction + refund)", len(grid.blockchain) == 2)
  check("Refund block marked as dispute", grid.blockchain[-1]["dispute_flag"] == True)

  print("\n" + "=" * 70)
  print("  ✓ HARDWARE FAILURE REFUND TEST PASSED")
  print("=" * 70 + "\n")


def test_multiple_transactions():
  """Test: Multiple transactions in sequence with SEPARATE kiosks"""
  print("\n" + "=" * 70)
  print("  TEST: Multiple Transactions")
  print("=" * 70)

  grid = Grid()

  # Create 2 users and 2 franchises
  user1 = User("Eve", 9000000005, "3333", "Z5", grid, 1000)
  user2 = User("Frank", 9000000006, "4444", "Z6", grid, 800)

  franchise1 = Franchise("Station_A", "ACC005", "Z1", "pass222", 100, grid)
  franchise2 = Franchise("Station_B", "ACC006", "Z2", "pass333", 200, grid)

  # Transaction 1: User1 --> Franchise1
  print("\n  Transaction 1: User1 charges 150 at Franchise1")
  kiosk1 = Kiosk(grid, franchise1)
  kiosk1.generate_qrcode()
  qr1 = f"qrcode_xxxxxx{franchise1.vfid[-6:]}.png"
  payload1 = user1.charge_request(qr1, 150)
  result1 = kiosk1.process_payment(payload1)
  check("Transaction 1 successful", result1["success"] == True)

  # Transaction 2: User2 --> Franchise2
  # IMPORTANT: Create a NEW kiosk with fresh timestamp!
  print("\n  Transaction 2: User2 charges 200 at Franchise2")
  kiosk2 = Kiosk(grid, franchise2)  # NEW kiosk instance
  kiosk2.generate_qrcode()  # Generates fresh QR with new timestamp
  qr2 = f"qrcode_xxxxxx{franchise2.vfid[-6:]}.png"
  payload2 = user2.charge_request(qr2, 200)
  result2 = kiosk2.process_payment(payload2)
  check("Transaction 2 successful", result2["success"] == True)

  # Transaction 3: User1 --> Franchise2
  # Create ANOTHER NEW kiosk with fresh timestamp
  print("\n  Transaction 3: User1 charges 100 at Franchise2")
  kiosk3 = Kiosk(grid, franchise2)  # NEW kiosk instance
  kiosk3.generate_qrcode()  # Generates fresh QR with new timestamp
  qr3 = f"qrcode_xxxxxx{franchise2.vfid[-6:]}.png"
  payload3 = user1.charge_request(qr3, 100)
  result3 = kiosk3.process_payment(payload3)
  check("Transaction 3 successful", result3["success"] == True)

  # Verify final balances
  print("\n  Final Balances:")
  check("User1 balance (1000-150-100)", user1.u_balance == 750)
  check("User2 balance (800-200)", user2.u_balance == 600)
  check("Franchise1 balance (100+150)", franchise1.f_balance == 250)
  check("Franchise2 balance (200+200+100)", franchise2.f_balance == 500)

  # Verify blockchain
  check("3 transaction blocks created", len(grid.blockchain) == 3)
  chain_valid = grid.verify_chain()
  check("Blockchain integrity intact", chain_valid == True)

  print("\n" + "=" * 70)
  print("  ✓ MULTIPLE TRANSACTIONS TEST PASSED")
  print("=" * 70 + "\n")

if __name__ == "__main__":
  try:
    test_complete_payment_flow()
    test_insufficient_balance()
    test_wrong_pin()
    test_hardware_failure_refund()
    test_multiple_transactions()

    print("\n" + "=" * 70)
    print("  ✓✓✓ ALL INTEGRATION TESTS PASSED ✓✓✓")
    print("=" * 70 + "\n")
  except AssertionError as e:
    print(f"\n✗ TEST FAILED: {e}\n")
    sys.exit(1)

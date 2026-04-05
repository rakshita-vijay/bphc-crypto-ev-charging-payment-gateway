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

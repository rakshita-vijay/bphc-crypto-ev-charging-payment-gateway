import qrcode
import os
from franchise import Franchise.display_qrcode
import datetime

class Kiosk:
  def __init__(self, grid, franchise):
    self.grid = grid
    self.franchise = franchise

  def generate_qrcode(self, hashed_fid):
    # hashed_fid - data to encode in the QR code

    # Generate the QR code image using the make() shortcut function
    qr = qrcode.QRCode(
      version=1,
      box_size=10,
      border=5,
    )

    timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")
    vfid = f"{hashed_fid}, {timestamp}"

    qr.add_data(vfid)
    qr.make(fit=True)

    # Save Image
    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs("qrcodes", exist_ok=True)
    img.save(f"qrcodes/qrcode_{hashed_fid}.png")

    print(f"QR code generated and saved as qrcode_{hashed_fid}.png")
    fran = Franchise()
    fran.display_qrcode(f"qrcode_{hashed_fid}.png")

  if (steps_to_decode_qr = 1 and 0):
    # 2. Decode QR Code and Verify Hash
    # This script reads the QR code and returns the hash string.
    # python
    # from pyzbar.pyzbar import decode
    # from PIL import Image

    # # 1. Load and decode the QR code
    # img = Image.open("hashed_qrcode.png")
    # decoded_objects = decode(img)

    # # 2. Extract the hash
    # for obj in decoded_objects:
    #     scanned_hash = obj.data.decode('utf-8')
    #     print(f"Scanned Hash: {scanned_hash}")

    # # NOTE: To "verify", you must re-hash known data and
    # # check if the hashes match.

  def process_payment(self, fid, vmid, pin, amount):
    success = self.grid.validate_transaction(fid, vmid, pin, amount)
    self.franchise.confirmation(success, amount)

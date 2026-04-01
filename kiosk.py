
import os
import datetime
import hashlib
import qrcode
from ascon_lwc import ascon_encrypt
from pyzbar.pyzbar import decode
from PIL import Image

# from grid import Grid
# from franchise import Franchise

class Kiosk:
  def __init__(self, grid, franchise):
    self.grid = grid
    self.franchise = franchise

  def generate_qrcode(self):
    # hashed_fid - data to encode in the QR code
    fid = self.franchise.fid

    timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    vfid = self.grid.generate_vfid(fid, timestamp)
    self.franchise.vfid = vfid

    # hashed_vfid = self.grid.sha3_algo(vfid).upper()[:16]
    qr_data = f"{vfid}, {timestamp}"

    # Generate the QR code image using the make() shortcut function
    # qr = qrcode.QRCode(
    #   version=1,
    #   box_size=10,
    #   border=5,
    # )

    # qr.add_data(hashed_vfid)
    # qr.make(fit=True)
    qr = qrcode.make(qr_data)

    # Save Image
    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs("qrcodes", exist_ok=True)
    img.save(f"qrcodes/qrcode_{hashed_vfid}.png")

    print(f"QR code generated and saved as qrcode_{hashed_vfid}.png in the folder 'qrcodes'")
    self.franchise.display_qrcode(f"qrcode_{hashed_vfid}.png")

  def decrypt_qrcode(self, qrcode_file_name):
    # and verify hash???

    # 1. load and decode the qr code
    img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    decoded_objects = decode(img)
    print(type(decoded_objects))

    if not decoded_objects:
      print("QR decode failed")
      return None, None

    # 2. extract the data
    # for obj in decoded_objects:
    #   scanned_hash = obj.data.decode('utf-8')
    #   print(f"Scanned Hash: {scanned_hash}")
    data = decoded_objects[0].data.decode('utf-8')

    # Step 2: Split VFID and timestamp
    try:
      vfid, timestamp = data.split(", ")
    except:
      print("Invalid QR format")
      return None, None
    key = b"RaksAditPriyVeda"
    nonce = timestamp.encode("utf-8").upper()[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
    # nonce - number used once; ensures same input != same output and prevents replay attacks
    ad = timestamp.encode("utf-8").upper()

    try:
      # Step 4: Decrypt
      pt = ascon_decrypt(key, nonce, ad, bytes.fromhex(vfid), variant="Ascon-128")
      fid = pt.decode()
    except Exception as e:
        print("Decryption failed --> tampered QR")
        return None, None

    # NOTE: To "verify", you must re-hash known data and
    # check if the hashes match.
    if (fid == self.franchise.fid):
      return True, fid # placeholder
    else:
      return False, None # placeholder

  def process_payment(self, qrcode_file_name, fid, vmid, pin, amount):
    confirmation, fid = self.decrypt_qrcode(qrcode_file_name)
    if (confirmation == True):
      success = self.grid.validate_transaction(fid, vmid, pin, amount)
      self.franchise.confirmation(success, amount)
    else:
      print("Payment failed due to invalid QR")

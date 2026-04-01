
import os
import datetime
import hashlib
import qrcode
from ascon_lwc import ascon_encrypt, ascon_decrypt
# from pyzbar.pyzbar import decode
import cv2
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

    self.timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    vfid, payload = self.grid.generate_vfid(fid, self.timestamp)
    self.franchise.vfid = vfid

    # hashed_vfid = self.grid.sha3_algo(vfid).upper()[:16]
    # qr_data = f"{vfid}, {timestamp}"
    qr_data = payload

    # Generate the QR code image using the make() shortcut function
    # qr = qrcode.QRCode(
    #   version=1,
    #   box_size=10,
    #   border=5,
    # )

    # qr.add_data(hashed_vfid)
    # qr.make(fit=True)
    # img = qr.make_image(fill_color="black", back_color="white")
    qr = qrcode.make(qr_data)

    # Save Image
    os.makedirs("qrcodes", exist_ok=True)
    qr.save(f"qrcodes/qrcode_xxxxxx{vfid[-6:]}.png")

    print(f"QR code generated and saved as qrcode_xxxxxx{vfid[-6:]}.png in the folder 'qrcodes'")
    self.franchise.display_qrcode(f"qrcode_xxxxxx{vfid[-6:]}.png")

  def decrypt_qrcode(self, qrcode_file_name):
    # and verify hash???

    # 1. load and decode the qr code
    # img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    # decoded_objects = decode(img)

    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    detector = cv2.QRCodeDetector()
    decoded_object, _, _ = detector.detectAndDecode(img)

    print(decoded_object)
    print(type(decoded_object))

    if not decoded_object:
      print("QR decode failed")
      return None, None

    payload = decoded_object

    # 2. extract the data
    # for obj in decoded_objects:
    #   scanned_hash = obj.data.decode('utf-8')
    #   print(f"Scanned Hash: {scanned_hash}")
    # data = decoded_object.decode('utf-8')

    # Step 2: Split VFID and timestamp
    try:
      vfid_hex, nonce_hex = decoded_object.split(", ")
      nonce = bytes.fromhex(nonce_hex)
      vfid = bytes.fromhex(vfid_hex)
    except:
      print("Invalid QR format")
      return None, None

    try:
      # NOTE: To "verify", you must re-hash known data and check if the hashes match.

      key = b"RaksAditPriyVeda"
      # nonce = timestamp.encode("utf-8").upper()[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
      # nonce - number used once; ensures same input != same output and prevents replay attacks
      ad = self.timestamp.encode("utf-8").upper()

      # step: Decrypt
      # print(vfid)
      # print(type(vfid))
      pt = ascon_decrypt(key, nonce, ad, vfid)
      # print("92")
      fid = pt.decode()
      # print("94")

      if (fid == self.franchise.fid):
        return True, fid # placeholder
      else:
        return False, None # placeholder

    except Exception as e:
      print(f"{e}")
      print("Decryption failed --> tampered QR")
      return None, None

  def process_payment(self, qrcode_file_name, fid, vmid, pin, amount):
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)
    if (confirmation == True and fid_from_decrypt == fid):
      success = self.grid.validate_transaction(fid, vmid, pin, amount)
      self.franchise.confirmation(success, amount)
    else:
      print("Payment failed due to invalid QR")

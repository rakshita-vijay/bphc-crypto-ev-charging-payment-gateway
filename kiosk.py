import os
import datetime
import hashlib
import qrcode
import cv2
from PIL import Image

from ascon_lwc import ascon_decrypt
# from pyzbar.pyzbar import decode

import shor_algo
import rsa
# from grid import Grid
# from franchise import Franchise

class Kiosk:
  def __init__(self, grid, franchise):
    self.grid = grid
    self.franchise = franchise
    self.timestamp = None

  def generate_qrcode(self):
    # hashed_fid - data to encode in the QR code
    fid = self.franchise.fid

    self.timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    vfid = self.grid.generate_vfid(fid, self.timestamp)
    self.franchise.vfid = vfid

    qr_data = f"{vfid}, {self.timestamp}"

    # Generate the QR code image using the make() shortcut function
    qr = qrcode.make(qr_data)

    # Save Image
    os.makedirs("qrcodes", exist_ok=True)
    qr.save(f"qrcodes/qrcode_xxxxxx{vfid[-6:]}.png")

    print(f"QR code generated and saved as qrcode_xxxxxx{vfid[-6:]}.png in the folder 'qrcodes'")
    self.franchise.display_qrcode(f"qrcode_xxxxxx{vfid[-6:]}.png")

  def decrypt_qrcode(self, decoded_qr_data):
    # and verify hash???

    # 1. load and decode the qr code
    # img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    # decoded_objects = decode(img)

    '''
    img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
    detector = cv2.QRCodeDetector()
    decoded_qr_data, _, _ = detector.detectAndDecode(img)
    '''

    # print(decoded_qr_data)
    # print(type(decoded_qr_data))

    if not decoded_qr_data:
      print("QR decode failed")
      return None, None

    # 2. extract the data
    # for obj in decoded_objects:
    #   scanned_hash = obj.data.decode('utf-8')
    #   print(f"Scanned Hash: {scanned_hash}")
    # data = decoded_object.decode('utf-8')

    # Step 2: Split VFID and timestamp
    try:
      parts = decoded_qr_data.split(", ")
      if len(parts) != 2:
        print("Invalid QR format, line 68")
        return None, None

      vfid_hex = parts[0].strip()
      ts = parts[1].strip()

      # print("Original vfid (first 10 bytes):", self.franchise.vfid[:20])
      # print("Decoded vfid (first 10 bytes):", vfid_hex[:20])
      # print(self.franchise.vfid == vfid_hex)

      vfid_from_decoded_qr = bytes.fromhex(vfid_hex)

    except:
      print("Invalid QR format")
      return None, None

    try:
      if (ts == self.timestamp):
        # NOTE: To "verify", you must re-hash known data and check if the hashes match.

        key = b"RaksAditPriyVeda"
        nonce = self.timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
        # nonce - number used once; ensures same input != same output and prevents replay attacks
        ad = self.timestamp.encode("utf-8")

        # step: Decrypt
        pt = ascon_decrypt(key, nonce, ad, vfid_from_decoded_qr)
        fid = pt.decode()

        if (fid == self.franchise.fid):
          return True, fid # placeholder
        else:
          raise Exception("FIDs don't match")
          # return False, None # placeholder
      else:
        raise Exception("Timestamps don't match")

    except Exception as e:
      print(f"{e}")
      print("Decryption failed --> tampered QR")
      return None, None

  def process_payment(self, payload):
    # payload is rsa-hashed vmid, pin, so we have to use shor's to decrypt
    """
    TO IMPLEMENT:

    Full payment flow:
      1. Verify QR code authenticity via ASCON decryption.
      2. Decrypt VMID and PIN from the RSA-encrypted payload.
      3. Forward auth request to the Grid.
      4. Attempt to unlock the charging cable.
      5. If cable unlock fails after a successful payment → trigger refund.

    Edge cases handled:
      - Invalid / tampered QR → reject immediately.
      - Grid rejects (bad PIN / balance / VMID) → inform franchise.
      - Payment approved but hardware fails → call add_reverse_block.
    """
    '''
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)

    if (confirmation == False or fid_from_decrypt != fid):
      print("Payment failed due to invalid QR")
      self.franchise.confirmation(False)
      return

    elif (confirmation == True and fid_from_decrypt == fid):
      vmid = rsa.decrypt_string(payload["VMID_enc"], payload["_rsa_d"], payload["rsa_n"])
      pin = rsa.decrypt_string(payload["PIN_enc"], payload["_rsa_d"], payload["rsa_n"])

      success = self.grid.validate_transaction(fid, vmid, pin, payload["amount"])
      status = self.franchise.confirmation(success, payload["amount"])
      if (success and status == False):
        self.grid.add_reverse_block(uid, fid, payload["amount"])
    '''
    if payload is None:
      print("[Kiosk] Payment aborted — no payload (QR scan failed).")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "No payload exists",
        "transaction_id": None
      }

    fid = self.franchise.fid
    amount = payload["amount"]

    # Step 1: Verify QR Code Authenticity
    print("\n[Step 1] Verifying QR Code...")
    confirmation, fid_from_decrypt = self.decrypt_qrcode(payload["QR_raw_data"])

    if confirmation is None or confirmation == False or fid_from_decrypt != fid:
      print("✗ Payment FAILED: Invalid or tampered QR code")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "Invalid or tampered QR code",
        "transaction_id": None
      }

    print("✓ QR Code verified")

    # Step 2: Decrypt VMID and PIN from RSA payload
    print("\n[Step 2] Decrypting credentials from RSA payload...")
    try:
      vmid = rsa.decrypt_string(payload["VMID_enc"], payload["_rsa_d"], payload["rsa_n"])
      pin = rsa.decrypt_string(payload["PIN_enc"], payload["_rsa_d"], payload["rsa_n"])
      print(f"✓ Credentials decrypted - VMID: {vmid}, PIN: {pin}")
    except Exception as e:
      print(f"✗ Payment FAILED: Could not decrypt credentials: {e}")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": f"RSA decryption failed: {e}",
        "transaction_id": None
      }

    # Step 3: Forward authorization request to Grid
    print("\n[Step 3] Requesting authorization from Grid Authority...")
    success = self.grid.validate_transaction(fid, vmid, pin, payload["amount"])

    if not success:
      print("✗ Grid Authority REJECTED the transaction")
      print("  Reasons could be: Invalid PIN, Insufficient balance, Unknown VMID")
      self.franchise.confirmation(False, 0)
      return {
        "success": False,
        "reason": "Grid Authority rejected transaction",
        "transaction_id": None
      }

    print("✓ Grid Authority APPROVED the transaction")

    # Step 4: Attempt to unlock charging cable
    print("\n[Step 4] Attempting to unlock charging cable...")
    status = self.franchise.confirmation(success, payload["amount"])

    if status is False:
      print("✗ Hardware FAILED: Cable unlock failed after successful payment")
      print("  Triggering automatic refund...")

      # Step 5: Handle hardware failure - trigger refund
      uid = None
      for u_id, user in self.grid.users.items():
        if user.vmid == vmid:
          uid = u_id

      if not uid:
        return {
          "success": False,
          "reason": "UID not found",
          "transaction_id": None
        }
      refund_block = self.grid.add_reverse_block(uid, fid, payload["amount"])

      if refund_block is not None:
        print("✓ Refund processed successfully")
        return {
          "success": False,
          "reason": "Hardware failure - automatic refund triggered",
          "transaction_id": None,
          "refund": True
        }
      else:
        print("✗ Refund FAILED")
        return {
          "success": False,
          "reason": "Hardware failure - refund processing failed",
          "transaction_id": None
        }

    # Payment Success
    print("\n" + "="*60)
    print("✓✓✓ PAYMENT SUCCESSFUL ✓✓✓")
    print("="*60)

    # Step 6: Demonstrate Quantum Vulnerability (Educational)
    print("\n[Step 5] Quantum Cryptography Vulnerability Demonstration")
    print("-" * 60)
    print("Showing how Shor's algorithm breaks the RSA key used for this transaction...")
    try:
      shor_algo.demonstrate_attack(payload)
    except Exception as e:
      print(f"Note: Shor's algorithm demo encountered: {e}")

    print("-" * 60)

    return {
      "success": True,
      "reason": "Payment successful - cable unlocked",
      "transaction_id": self.grid.blockchain[-1]["transaction_id"] if self.grid.blockchain else None,
      "amount": payload["amount"]
    }

if __name__ == "__main__":
  # Self-test would go here
  pass

import os
import datetime
import hashlib
import qrcode
import cv2
from PIL import Image

from ascon_lwc import ascon_decrypt
import shor_algo
import rsa

class Kiosk:
  def __init__(self, grid, franchise):
    self.grid = grid
    self.franchise = franchise
    self.timestamp = None

  def generate_qrcode(self):
    fid = self.franchise.fid
    self.timestamp = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
    vfid = self.grid.generate_vfid(fid, self.timestamp)
    self.franchise.vfid = vfid

    qr_data = f"{vfid}, {self.timestamp}"
    qr = qrcode.make(qr_data)

    os.makedirs("qrcodes", exist_ok=True)
    qr.save(f"qrcodes/qrcode_xxxxxx{vfid[-6:]}.png")

    print(f"QR code generated and saved as qrcode_xxxxxx{vfid[-6:]}.png in the folder 'qrcodes'")
    self.franchise.display_qrcode(f"qrcode_xxxxxx{vfid[-6:]}.png")

  def decrypt_qrcode(self, qrcode_file_name):
    """
    Decrypts and verifies QR code authenticity using ASCON.
    Prevents replay attacks by checking timestamp.
    Detects tampering by comparing decrypted FID with franchise FID.
    
    Returns:
        (True, fid) if QR is valid and authentic
        (False/None, None) if QR is invalid or tampered
    """
    try:
      img = cv2.imread(os.path.join("qrcodes", qrcode_file_name))
      if img is None:
        print("QR image file not found")
        return None, None
        
      detector = cv2.QRCodeDetector()
      decoded_qr_data, _, _ = detector.detectAndDecode(img)

      if not decoded_qr_data:
        print("QR decode failed")
        return None, None

      # Step 1: Split VFID and timestamp
      try:
        parts = decoded_qr_data.split(", ")
        if len(parts) != 2:
          print("Invalid QR format")
          return None, None

        vfid_hex = parts[0].strip()
        ts = parts[1].strip()
        vfid_from_decoded_qr = bytes.fromhex(vfid_hex)

      except Exception as e:
        print(f"Invalid QR format: {e}")
        return None, None

      # Step 2: Verify timestamp (prevent replay attacks)
      if ts != self.timestamp:
        print(f"Timestamp mismatch - Possible replay attack. Expected: {self.timestamp}, Got: {ts}")
        return None, None

      # Step 3: Decrypt VFID using ASCON
      try:
        key = b"RaksAditPriyVeda"
        nonce = self.timestamp.encode("utf-8")[:16].ljust(16, b"\x00")
        ad = self.timestamp.encode("utf-8")
        
        pt = ascon_decrypt(key, nonce, ad, vfid_from_decoded_qr)
        fid = pt.decode()

        # Step 4: Verify FID (detect tampering)
        if fid == self.franchise.fid:
          print(f"✓ QR Code verified - FID matches: {fid}")
          return True, fid
        else:
          print(f"✗ FID mismatch - QR code tampered. Expected: {self.franchise.fid}, Got: {fid}")
          return False, None

      except Exception as e:
        print(f"Decryption failed - QR code is tampered or corrupted: {e}")
        return None, None

    except Exception as e:
      print(f"Error in decrypt_qrcode: {e}")
      return None, None

  def process_payment(self, qrcode_file_name, uid, fid, payload, amount):
    """
    Complete payment flow:
    1. Verify QR code authenticity via ASCON decryption
    2. Decrypt VMID and PIN from RSA-encrypted payload
    3. Forward auth request to the Grid
    4. Attempt to unlock the charging cable
    5. If cable unlock fails after successful payment → trigger refund
    
    Edge cases handled:
    - Invalid/tampered QR → reject immediately
    - Grid rejects (bad PIN/balance/VMID) → inform franchise
    - Payment approved but hardware fails → call add_reverse_block
    
    Args:
        qrcode_file_name: Path to QR code image
        uid: User ID
        fid: Franchise ID
        payload: RSA-encrypted payment data
        amount: Charging amount
    """
    print("\n" + "="*60)
    print("PAYMENT PROCESSING INITIATED")
    print("="*60)

    # Step 1: Verify QR Code Authenticity
    print("\n[Step 1] Verifying QR Code...")
    confirmation, fid_from_decrypt = self.decrypt_qrcode(qrcode_file_name)

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
      shor_algo.demonstrate_attack()
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
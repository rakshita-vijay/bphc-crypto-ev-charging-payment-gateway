import qrcode
import os

class Kiosk:
  def __init__(self):
    self.x = x

  def generate_qrcode(self, hashed_fid):
    # hashed_fid - data to encode in the QR code

    # Generate the QR code image using the make() shortcut function
    qr = qrcode.QRCode(
      version=1,
      box_size=10,
      border=5,
    )
    qr.add_data(hashed_fid)
    qr.make(fit=True)

    # Save Image
    img = qr.make_image(fill_color="black", back_color="white")

    os.makedirs("qrcodes", exist_ok=True)
    img.save(f"qrcodes/qrcode_{hashed_fid}.png")

    print(f"QR code generated and saved as my_qrcode_{hashed_fid}.png")

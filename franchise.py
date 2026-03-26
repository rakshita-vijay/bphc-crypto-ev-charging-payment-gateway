import datetime
import hashlib
from PIL import Image
import os

class Franchise:
  def __init__(self, f_name, f_acc_num, f_zone_code, f_pwd, f_balance, fid):
    self.f_name = f_name
    self.f_acc_num = f_acc_num
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")
    self.vfid = None
    self.qr_code = None

    # FID generation - can be done here instead of in grid cuz it's just one line
    raw = f_name + self.f_time_acc_create + f_pwd
    self.fid = hashlib.sha3_256(raw.encode()).hexdigest()[:16]

  def registration_with_grid(self, grid):
    grid.register_franchise(self) # Implement register_franchise in grid
    print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")

  def qr_display(self, qr_code, vfid):
    self.qr_code = qr_code
    self.vfid = vfid

    if self.qr_code:
      print(f"QR code received for franchise {self.f_name}")
      qrcode_file_name = f"{self.f_name}_qr.png"
      qrcode_file_name = os.path.join("qrcodes", qrcode_file_name)
      self.qr_code.save(qrcode_file_name)

      self.qr_code.show()

  def confirmation(self, success, amount=0):
    if success:
      self.f_balance += amount
      self.unlock_charging_cable(self, 1)
    else:
      print(f"Transaction for {self.f_name} rejected.")

  def unlock_charging_cable(self, flag):
    return True if (flag == 1) else False

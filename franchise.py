import datetime
import hashlib
from PIL import Image

class Franchise:
  def __init__(self, f_name, f_acc_num, f_zone_code, f_pwd, f_balance):
    self.f_name = f_name
    self.f_acc_num = f_acc_num
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")

    self.fid = self.generate_fid()

  def sha3_algo(self, message):
    # can we just import it? or should we code it out?
    try:
      return hashlib.sha3_256(message.encode()).hexdigest()
    except:
      return "Could not hash"
    # this returns hex code

  def generate_fid(self):
    message = f"{self.f_name}, {self.f_time_acc_create}, {self.f_pwd}"
    ct = ((sha3_algo(message)).upper())[:16]
    # unique to every station and shouldn’t be shared
    return ct

  def display_qrcode(self, qrcode_file_name):
    img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    img.show()

  def unlock_charging_cable(self, flag):
    return True if (flag == 1) else False

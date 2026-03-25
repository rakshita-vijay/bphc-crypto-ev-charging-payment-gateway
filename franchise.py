import datetime
import hashlib

class Franchise:
  def __init__(self, f_name, f_zone_code, f_pwd, f_balance):
    self.f_name = f_name
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")

    self.generate_fid()

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

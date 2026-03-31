import hashlib
import time
from datetime import datetime
import qrcode

class User:
  def __init__(self, u_name:str, u_phone:str, u_pin:int, u_balance:int = 0, grid):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance
    self.grid = grid

    self.uid = None
    conf = self.req_validation_and_generate_uid(self)
    if (conf):
      self.vmid = self.generate_vmid()

  def req_validation_and_generate_uid(self):
    confirmation = self.grid.req_user_validation(self)
    if (confirmation == True):
      print(f"User '{self.u_name}' registered with UID: {self.uid}")
    else:
      print("User registration failed")
    return confirmation

  def generate_vmid(self):
    return f"{self.uid}_{self.u_phone}"

  def charge_request(self, qrcode_path, charge_amount:int):
    send = {"QR_path": qrcode_path, "VMID": self.vmid, "PIN": self.u_pin, "amount": charge_amount}
    # encrypt this info. how?
    return send

if __name__ == "__main__":
  user = User("Tester", "8124086501", 1234, 9999)
  print(user.uid)
  print(len(user.uid))
  print(user.vmid)

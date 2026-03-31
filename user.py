import hashlib
import time
from datetime import datetime
import qrcode

class User:
  def __init__(self, name:str, phone:str, pin:int, balance:int):
    self.name = name
    self.phone = phone
    self.pin = pin
    self.balance = balance

    self.uid = self.generate_uid()
    self.vmid = self.generate_vmid()

  def generate_uid(self):
    curr_time = time.time()
    # formatted_time = ((datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")
    # curr_time = "|".join(formatted_time)
    message = f"{self.name}{curr_time}{self.pin}"
    ct = hashlib.sha3_256(message.encode("utf-8"))
    # unique to every station and shouldn’t be shared
    return ct.hexdigest()[:16]

  def generate_vmid(self):
    return f"{self.uid}_{self.phone}"
  
  def charge_request(self, qrcode_path, charge_amount:int):
    send = {"QR_path": qrcode_path, "VMID": self.vmid, "PIN": self.pin, "amount": charge_amount}
    # encrypt this info. how?
    return send


if __name__ == "__main__":
  user = User("Tester", "8124086501", 1234, 9999)
  print(user.uid)
  print(len(user.uid))
  print(user.vmid)  
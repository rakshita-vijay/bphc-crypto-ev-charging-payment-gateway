import hashlib
from grid import Grid.sha3_algo

class User:
  def __init__(self, u_name, u_phone, u_pin, u_balance):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance

    self.uid = self.generate_uid()
    self.vmid = self.generate_vmid()

  def generate_uid(self):
    grid = Grid()
    message = f"{self.u_name}, {self.u_phone}, {self.u_pin}"
    ct = ((self.grid.sha3_algo(message)).upper())[:16]
    # unique to every station and shouldn’t be shared
    return ct

  def generate_vmid(self):
    return f"{self.uid}_{self.u_phone}"

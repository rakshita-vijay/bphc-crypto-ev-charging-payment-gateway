import hashlib

class User:
  def __init__(self, u_name, u_phone, u_pin, u_balance):
    self.u_name = u_name
    self.u_phone = u_phone
    self.u_pin = u_pin
    self.u_balance = u_balance

    self.uid = self.generate_uid()
    self.vmid = self.generate_vmid()

  def sha3_algo(self, message):
    # can we just import it? or should we code it out?
    try:
      return hashlib.sha3_256(message.encode()).hexdigest()
    except:
      return "Could not hash"
    # this returns hex code

  def generate_uid(self):
    message = f"{self.u_name}, {self.u_phone}, {self.u_pin}"
    ct = ((sha3_algo(message)).upper())[:16]
    # unique to every station and shouldn’t be shared
    return ct

  def generate_vmid(self):
    return f"{self.uid}_{self.phone}"

class Grid:
  def __init__(self):
    self.users = {}
    self.franchises = {}

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

  def register_user(self, user):
    self.users[user.uid] = user

  def register_franchise(self, franchise):
    self.franchises[franchise.fid] = franchise

  def generate_vfid(self, fid):
    # using lwc algo

  def validate_transaction(self, vmid, pin, amount):
    for user in self.users.values():
      if user.vmid == vmid and user.pin == pin:
        if user.balance >= amount:
          user.balance -= amount
          return True
    return False

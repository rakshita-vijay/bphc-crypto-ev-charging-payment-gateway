class Grid:
  def __init__(self):
    self.users = {}
    self.franchises = {}

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

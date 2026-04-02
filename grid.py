import os
import datetime
import hashlib
from ascon_lwc import ascon_encrypt

class Grid:
  def __init__(self):
    self.providers = ["Tata", "Adani", "ChargePoint"]
    self.zones = {"Z1": "Tata", "Z2": "Adani", "Z3": "ChargePoint"} # f_zone_code, provder_name
    self.users = {} # uid, user_obj
    self.franchises = {} # fid, fran_obj
    self.blockchain = [] # block dicts

  def sha3_algo(self, message):
    # can we just import it? or should we code it out?
    try:
      return hashlib.sha3_256(message.encode("utf-8")).hexdigest()
    except:
      return "Could not hash"
    # this returns hex code

  def generate_fid(self, f_name, f_time_acc_create, f_pwd):
    message = f"{f_name}, {f_time_acc_create}, {f_pwd}"
    return self.sha3_algo(message)[:16]
    # fid - unique to every station and shouldn’t be shared

  def generate_vfid(self, fid, timestamp):
    # implement using lwc algo, below is placeholder
    key = b"RaksAditPriyVeda"
    nonce = timestamp.encode("utf-8")[:16].ljust(16, b"\x00") # .ljust(16, b"\x00") pads with zeros if shorter
    # nonce - number used once; ensures same input != same output and prevents replay attacks
    pt = fid.encode("utf-8") # actua data to protect
    ad = timestamp.encode("utf-8")
    # associated data is: data that is NOT encrypted, but is authenticated
    # timestamp is not hidden but cannot be tampered with
    vfid = ascon_encrypt(key, nonce, ad, pt)

    return vfid.hex()

  def req_fran_validation(self, f_obj = None):
    # if f_obj.f_zone_code in self.zones and (f_obj.f_name != None and f_obj.f_pwd != None and f_obj.f_balance != None and f_obj.f_time_acc_create != None):

    req_fields = [f_obj.f_name, f_obj.f_pwd, f_obj.f_balance, f_obj.f_time_acc_create]

    if f_obj.f_zone_code in self.zones and all(x is not None for x in req_fields):
      return self.register_franchise(f_obj)
    else:
      return False

  def req_user_validation(self, u_obj = None):
    req_fields = [u_obj.u_name, u_obj.u_phone, u_obj.u_pin, u_obj.u_balance]

    if all(x is not None for x in req_fields):
      return self.register_user(u_obj)
    else:
      return False

  def register_franchise(self, franchise):
    fid = self.generate_fid(franchise.f_name, franchise.f_time_acc_create, franchise.f_pwd)
    franchise.fid = fid
    franchise.grid = self
    self.franchises[franchise.fid] = franchise
    return True

  def register_user(self, user):
    message = f"{user.u_name}, {user.u_phone}, {user.u_pin}"
    uid = self.sha3_algo(message)[:16] # unique to every station and shouldn’t be shared
    user.uid = uid
    user.vmid = f"{uid}_{user.u_phone}"
    user.grid = self
    self.users[user.uid] = user
    return True

  def validate_transaction(self, fid, vmid, pin, amount):
    if fid not in self.franchises:
      print("FID not found in franchises")
      return False

    for user in self.users.values():
      if user.vmid == vmid and user.u_pin == pin:
        if user.u_balance >= amount:
          user.u_balance -= amount
          # self.franchises[fid].f_balance += amount

          ts = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
          bl = self.add_block(user.uid, fid, ts, amount)
          if (bl == None):
            printf(f"Block of FID {fid} representing a successful transaction could not be added to blockchain")
            return False
          return True
    return False

  def add_block(self, uid, fid, timestamp, amount, dispute = False): # disp_flag : T for a refund block
    try:
      t_id_msg = f"{uid}, {fid}, {timestamp}, {amount}"
      prev_hash = self.blockchain[-1]["transaction_id"] if len(self.blockchain) > 0 else ("0" * 64)
      block = {
                "transaction_id" : self.sha3_algo(t_id_msg),
                "prev_bl_hash" : prev_hash,
                "timestamp" : timestamp,
                "uid" : uid,
                "fid" : fid,
                "amount" : amount,
                "dispute_flag" : dispute
              }
      self.blockchain.append(block)
      x = "successful transaction" if dispute == False else "refund"
      print(f"Block of FID {fid} representing a {x} added to blockchain")
      return block
    except:
      return None

  def process_refund(self, uid, fid, amount):
    if fid not in self.franchises:
      print("FID not found in franchises")
      return None

    for user in self.users.values():
      if user.uid == uid:
        user.u_balance += amount
        self.franchises[fid].f_balance -= amount
        ts = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S"))
        return ts

    return None

  def add_reverse_block(self, uid, fid, amount, dispute = True):
    # called when payment succeeds but hardware fails to dispense power. reverses the balance and records a dispute block.
    ts = self.process_refund(uid, fid, amount)
    if ts is None:
      print("Refund failed - either FID or user not found")
      return None

    return self.add_block(uid, fid, ts, amount, True)

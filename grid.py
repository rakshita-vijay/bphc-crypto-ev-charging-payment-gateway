import hashlib

class Grid:
  def __init__(self, energy_provider, reg_zone):
    self.energy_provider = energy_provider
    self.reg_zone = reg_zone
    self.zone_code = 0 # based on a dict

  # def conv_to_hex(self):
    # 16 digit hex number

  def sha3_algo(self, message, length):
    # can we just import it? or should we code it out?
    if length == 224:
      return hashlib.sha3_224(message.encode()).hexdigest()
    elif length == 256:
      return hashlib.sha3_256(message.encode()).hexdigest()
    elif length == 384:
      return hashlib.sha3_384(message.encode()).hexdigest()
    elif length == 512:
      return hashlib.sha3_512(message.encode()).hexdigest()
    else:
      return "Invalid length"
    # this return hex code only

  def gen_fid(self):
    # self.f_name
    # self.f_time_acc_create
    # self.f_pwd
    # hashed using the SHA3 (Keccak-256) algorithm and converted into a 16-digit hexadecimal number
    message = ', '.join([self.f_name, self.f_time_acc_create, self.f_pwd])
    m_len = 224 if (len(message) <= 224)
            else (256 if (len(message) <= 256)
            else (384 if (len(message) <= 384))
            else 512)

    ct = (sha3_algo(message, m_len)).upper()
    # unique to every station and shouldn’t be shared

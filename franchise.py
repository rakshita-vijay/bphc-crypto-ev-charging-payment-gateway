import os
import datetime
import hashlib
from PIL import Image
from grid import Grid

class Franchise:
  def __init__(self, f_name, f_acc_num, f_zone_code, f_pwd, f_balance, grid):
    self.f_name = f_name
    self.f_acc_num = f_acc_num
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_balance = f_balance
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")
    self.grid = grid # have to figure out which grid to assign bcz of f_zone_code (done in grid) - right??? NO.
    self.fid = None # done in grid, if validated, so no dangling fids are there
    self.req_validation_and_reg_w_grid()
    self.vfid = None # what to do with these @renake
    self.qr_code = None

  def req_validation_and_reg_w_grid(self):
    confirmation = self.grid.req_validation(self)
    if (confirmation == True):
      print(f"Franchise '{self.f_name}' registered with FID: {self.fid}")
    else:
      print("Franchise validation failed")

  def display_qrcode(self, qrcode_file_name):
    img = Image.open(os.path.join("qrcodes", qrcode_file_name))
    self.qr_code = img
    self.qr_code.show()

  def confirmation(self, success, amount = 0):
    if success:
      self.f_balance += amount
      self.unlock_charging_cable(1)
    else:
      print(f"Transaction for {self.f_name} rejected.")

  def unlock_charging_cable(self, flag):
    return flag == 1

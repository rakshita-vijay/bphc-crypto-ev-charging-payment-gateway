import datetime
from grid import Grid

class Franchise(Grid):
  def __init__(self, f_name, f_zone_code, f_pwd, f_init_acc_bal):
    super.__init__()
    registration(f_name, f_zone_code, f_pwd, f_init_acc_bal)
    self.f_time_acc_create = ((datetime.datetime.now()).strftime("%d-%m-%y %H:%M:%S")).split(" ")

  def registration(self, f_name, f_zone_code, f_pwd, f_init_acc_bal):
    self.f_name = f_name
    self.f_zone_code = f_zone_code
    self.f_pwd = f_pwd
    self.f_init_acc_bal = f_init_acc_bal

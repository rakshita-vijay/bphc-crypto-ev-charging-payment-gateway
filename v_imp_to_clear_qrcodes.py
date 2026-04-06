import os, shutil, re
# import os, sys, re, datetime, csv, zipfile, shutil

def delete_pychache():
  for root, dirs, files in os.walk(os.getcwd()):
    for dir_name in dirs:
      if dir_name == "__pycache__":
        pycache_path = os.path.join(root, dir_name)
        try:
          shutil.rmtree(pycache_path)
        except Exception as e:
          print(f"Error deleting {pycache_path}: {e}")
  print("Pycache files deleted from repo.")

def delete_qrcodes():
  curr_dir = os.getcwd()
  for folders, _, files in os.walk(curr_dir):
    for file in files:
      if re.search(r'^qrcode_xxxxxx', file):
        os.remove(os.path.join(folders, file))
  print("QR codes deleted from repo.")

if __name__ == "__main__":
  delete_pychache()
  delete_qrcodes()

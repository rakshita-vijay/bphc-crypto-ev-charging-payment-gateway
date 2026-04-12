import os, sys

all_files = []

with open("code_not_2_largest.py", "w") as out_file:
  for root, dirs, files in os.walk(os.getcwd()):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'qrcodes', 'pages']]
    files[:] = [f for f in files if f not in ['.gitignore', '_to_do.txt', 'all_code.py', 'app.py', 'code.py', 'README.md', 'v_imp_to_clear_qrcodes.py']]

    for file in files:
      file_path = os.path.join(root, file)
      try:
        size = os.path.getsize(file_path)
        all_files.append({
          "fn": file_path,
          "len": size
        })
      except Exception:
        continue

  if len(all_files) < 2:
    print("Not enough files")
    exit()

  sorted_data = sorted(all_files, key=lambda x: x["len"])
  last2 = [sorted_data[-1]["fn"], sorted_data[-2]["fn"]]
  print(f"Download and attach: {last2[0].split('/')[-1]} and {last2[1].split('/')[-1]}")

  for file_data in sorted_data:
    file_path = file_data["fn"]
    if file_path in last2:
      continue

    try:
      with open(file_path, "r") as fi:
        out_file.write(f"# --- {file_path.split('/')[-1]} ---\n")
        out_file.write(fi.read())
        out_file.write("\n")
    except Exception:
      # Skip binary/unreadable files
      continue

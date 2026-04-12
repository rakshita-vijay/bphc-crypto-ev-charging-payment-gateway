import os, sys

all_files = []

with open("code.py", "w") as out_file:
  for root, dirs, files in os.walk(os.getcwd()):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'qrcodes', 'pages']]
    files[:] = [f for f in files if f not in ['.gitignore', 'all_code_not_2_largest.py', 'all_code.py', 'app.py', 'code_not_2_largest.py', 'code.py', 'README.md', 'v_imp_to_clear_qrcodes.py']]

    for file in files:
      file_path = os.path.join(root, file)
      try:
        size = os.path.getsize(file_path)
        all_files.append(file_path)
      except Exception:
        continue

  if len(all_files) == 0:
    print("No files found")
    exit()

  sorted_data = sorted(all_files)

  for file_path in sorted_data:
    try:
      with open(file_path, "r") as fi:
        out_file.write(f"# --- {file_path.split('/')[-1]} ---\n")
        out_file.write(fi.read())
        out_file.write("\n")
    except Exception:
      # Skip binary/unreadable files
      continue

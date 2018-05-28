import os

files = os.listdir("/Users/neil/workplace/raw_files/")
total_files = len(files)
files = [file.split(".")[0] for file in files]
files = set(files)
unique_files = len(set(files))

if total_files == unique_files:
    print("FILE CHECK IS GOOD")
else:
    raise NameError("FILE CHECK FAILED. NOT ALL FILES ARE UNIQUE")

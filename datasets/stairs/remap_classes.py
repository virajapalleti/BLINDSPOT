import os

STAIRS_LABEL_DIR = "C:/Users/palle/Downloads/all projects/SEREN-1/datasets/stairs/stairs/labels"
NEW_CLASS_ID = 7

for filename in os.listdir(STAIRS_LABEL_DIR):
    if filename.endswith(".txt"):
        filepath = os.path.join(STAIRS_LABEL_DIR, filename)
        with open(filepath, "r") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            parts[0] = str(NEW_CLASS_ID)
            new_lines.append(" ".join(parts) + "\n")
        with open(filepath, "w") as f:
            f.writelines(new_lines)

print("Remapping done — stairs is now class 7")
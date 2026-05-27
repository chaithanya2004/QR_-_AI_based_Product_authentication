import os
import shutil

SOURCE_DIR = "dataset/archive"
DEST_DIR = "dataset"

GENUINE_DIR = os.path.join(DEST_DIR, "genuine")
FAKE_DIR = os.path.join(DEST_DIR, "fake")

os.makedirs(GENUINE_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

def classify_image(filename):
    fname = filename.lower()
    if fname.endswith("-v1.jpg") or fname.endswith("-v1.png") or \
       fname.endswith("-v2.jpg") or fname.endswith("-v2.png"):
        return "fake"
    if fname.endswith("-v3.jpg") or fname.endswith("-v3.png") or \
       fname.endswith("-v4.jpg") or fname.endswith("-v4.png"):
        return "genuine"
    return None

for file in os.listdir(SOURCE_DIR):
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    label = classify_image(file)
    src = os.path.join(SOURCE_DIR, file)

    if label == "genuine":
        shutil.copy(src, os.path.join(GENUINE_DIR, file))
        print(f"[GENUINE] {file}")
    elif label == "fake":
        shutil.copy(src, os.path.join(FAKE_DIR, file))
        print(f"[FAKE] {file}")
    else:
        print(f"[SKIPPED] {file}")

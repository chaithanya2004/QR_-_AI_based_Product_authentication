import json
import shutil
import zipfile
import os

# ---------------------------
# STEP 1: Extract ZIP
# ---------------------------
zip_path = "Dataset.v1i.coco.zip"
extract_dir = "dataset_raw"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

print("[✓] ZIP extracted successfully!")

# ---------------------------
# STEP 2: Load COCO annotation file
# ---------------------------
annotation_file = os.path.join(extract_dir, "annotations.json")  # change name if diff

with open(annotation_file, 'r') as f:
    data = json.load(f)

print("[✓] COCO annotations loaded")

# ---------------------------
# STEP 3: Prepare binary output folders
# ---------------------------
output_dir = "dataset_binary"

real_dir = os.path.join(output_dir, "real")
fake_dir = os.path.join(output_dir, "fake")

os.makedirs(real_dir, exist_ok=True)
os.makedirs(fake_dir, exist_ok=True)

# ---------------------------
# STEP 4: Map COCO image IDs to filenames
# ---------------------------
image_id_to_file = {img["id"]: img["file_name"] for img in data["images"]}

# ---------------------------
# STEP 5: Read categories and annotations
# ---------------------------
# Detect category IDs
cat_map = {cat["id"]: cat["name"].lower() for cat in data["categories"]}
print("Detected Categories:", cat_map)

# Must have 2 categories: real & fake
real_ids = [cid for cid, name in cat_map.items() if "real" in name]
fake_ids = [cid for cid, name in cat_map.items() if "fake" in name]

if not real_ids or not fake_ids:
    print("ERROR: No Real/Fake labels found!")
    exit()

# ---------------------------
# STEP 6: Move images to respective folders
# ---------------------------
images_src_path = os.path.join(extract_dir, "images")

count_real = 0
count_fake = 0

for ann in data["annotations"]:
    img_id = ann["image_id"]
    cat_id = ann["category_id"]
    file_name = image_id_to_file[img_id]

    src = os.path.join(images_src_path, file_name)

    if cat_id in real_ids:
        shutil.copy(src, os.path.join(real_dir, file_name))
        count_real += 1
    elif cat_id in fake_ids:
        shutil.copy(src, os.path.join(fake_dir, file_name))
        count_fake += 1

print(f"[✓] Conversion completed!")
print("Real images:", count_real)
print("Fake images:", count_fake)
print("Output folder:", output_dir)

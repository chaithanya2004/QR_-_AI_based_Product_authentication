import os
import requests
from bs4 import BeautifulSoup
import cv2
import random

# ===========================
# FUNCTION 1: DOWNLOAD IMAGES
# ===========================
def download_pixabay_images(query, folder, num_images=30):
    print(f"\nDownloading images for: {query}")
    os.makedirs(folder, exist_ok=True)
    url = f"https://pixabay.com/images/search/{query.replace(' ', '%20')}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    imgs = soup.find_all("img")

    count = 0
    for img in imgs:
        src = img.get("src")
        if src and "cdn.pixabay.com" in src:
            try:
                img_data = requests.get(src).content
                with open(f"{folder}/{query}_{count}.jpg", "wb") as f:
                    f.write(img_data)
                count += 1
                print(f"Downloaded image {count}")
                if count >= num_images:
                    break
            except:
                pass

    print(f"Finished: {count} images saved in {folder}")


# ======================================
# FUNCTION 2: CREATE FAKE/TAMPERED IMAGES
# ======================================
def simulate_fake_images(input_folder, output_folder):
    print(f"\nCreating FAKE images from: {input_folder}")
    os.makedirs(output_folder, exist_ok=True)
    
    for file in os.listdir(input_folder):
        if not file.endswith(".jpg"):
            continue

        img_path = os.path.join(input_folder, file)
        img = cv2.imread(img_path)
        if img is None:
            continue

        # Rotate slightly
        h, w = img.shape[:2]
        angle = random.randint(-6, 6)
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1)
        rotated = cv2.warpAffine(img, M, (w, h))

        # Color distortion
        alpha = random.uniform(0.8, 1.2)
        beta = random.randint(-25, 25)
        fake_img = cv2.convertScaleAbs(rotated, alpha=alpha, beta=beta)

        cv2.imwrite(os.path.join(output_folder, "fake_" + file), fake_img)

    print(f"Fake images created at: {output_folder}")


# ===========================
# MAIN SCRIPT — RUN EVERYTHING
# ===========================
if __name__ == "__main__":
    # Download genuine images
    download_pixabay_images("Nivea cream", "dataset/genuine/cream", 30)
    download_pixabay_images("Nivea lotion", "dataset/genuine/lotion", 30)
    download_pixabay_images("Nivea facewash", "dataset/genuine/facewash", 30)

    # Create fake images
    simulate_fake_images("dataset/genuine/cream", "dataset/fake/cream")
    simulate_fake_images("dataset/genuine/lotion", "dataset/fake/lotion")
    simulate_fake_images("dataset/genuine/facewash", "dataset/fake/facewash")

    print("\n🎉 Dataset creation completed!")

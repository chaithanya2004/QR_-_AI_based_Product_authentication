import os
import cv2
import numpy as np

# Paths
genuine_dir = "dataset/genuine_img"
fake_dir = "dataset/fake_augmented"
os.makedirs(fake_dir, exist_ok=True)

# --- Helper functions ---

def random_brightness_contrast(img):
    alpha = 0.5 + np.random.rand()  # contrast (0.5 to 1.5)
    beta = np.random.randint(-50, 50)  # brightness (-50 to 50)
    return cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

def add_gaussian_blur(img):
    k = np.random.choice([3,5,7])
    return cv2.GaussianBlur(img, (k,k), 0)

def add_noise(img):
    noise = np.random.normal(0, 25, img.shape).astype(np.uint8)
    return cv2.add(img, noise)

def random_resize(img):
    h, w = img.shape[:2]
    scale = np.random.uniform(0.3, 0.7)
    new_w, new_h = int(w*scale), int(h*scale)
    img_small = cv2.resize(img, (new_w, new_h))
    return cv2.resize(img_small, (w, h))  # upscale back

def elastic_distort(img, alpha=50, sigma=5):
    # Simple approximation using random affine + warp
    h, w = img.shape[:2]
    pts1 = np.float32([[0,0],[w,0],[0,h]])
    dx = np.random.randint(-alpha, alpha, size=(3,2))
    pts2 = pts1 + dx
    M = cv2.getAffineTransform(pts1, pts2.astype(np.float32))
    return cv2.warpAffine(img, M, (w,h), borderMode=cv2.BORDER_REFLECT)

# --- Apply augmentations ---
for img_name in os.listdir(genuine_dir):
    img_path = os.path.join(genuine_dir, img_name)
    img = cv2.imread(img_path)

    if img is None:
        continue

    img_aug = img.copy()
    img_aug = random_brightness_contrast(img_aug)
    if np.random.rand() > 0.5:
        img_aug = add_gaussian_blur(img_aug)
    if np.random.rand() > 0.5:
        img_aug = add_noise(img_aug)
    if np.random.rand() > 0.5:
        img_aug = random_resize(img_aug)
    if np.random.rand() > 0.5:
        img_aug = elastic_distort(img_aug)

    save_path = os.path.join(fake_dir, f"fake_{img_name}")
    cv2.imwrite(save_path, img_aug)

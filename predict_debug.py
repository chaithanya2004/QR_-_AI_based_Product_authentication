import sys
import os
import cv2
import numpy as np
import tensorflow as tf

# Debug script to inspect per-class probabilities for a single image.
# Usage (PowerShell):
# python .\predict_debug.py "d:\path\to\screenshot.jpg"

MODEL_CANDIDATES = [
    os.path.join('model', 'qr_authenticator_model.h5'),
    'qr_authenticator_model.h5'
]

IMG_SIZE = 128
# Default label order used in training scripts. Change if your training used a different order.
LABELS = ['fake', 'genuine', 'non_qr']


def load_model():
    for p in MODEL_CANDIDATES:
        if os.path.exists(p):
            print(f"Loading model: {p}")
            return tf.keras.models.load_model(p)
    raise FileNotFoundError(f"No model found. Tried: {MODEL_CANDIDATES}")


def preprocess_cv2(path, as_rgb=False):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found or unreadable: {path}")
    if as_rgb:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    x = img.astype('float32') / 255.0
    return np.expand_dims(x, 0)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python predict_debug.py <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print("Image path does not exist:", img_path)
        sys.exit(1)

    model = load_model()

    # Try prediction with cv2 BGR (the same preprocessing you trained with)
    x_bgr = preprocess_cv2(img_path, as_rgb=False)
    preds_bgr = model.predict(x_bgr)[0]

    # Also try with RGB (in case of mismatch)
    x_rgb = preprocess_cv2(img_path, as_rgb=True)
    preds_rgb = model.predict(x_rgb)[0]

    def print_preds(preds, mode):
        print('\n--- Predictions (' + mode + ') ---')
        for i, p in enumerate(preds):
            label = LABELS[i] if i < len(LABELS) else f'class_{i}'
            print(f"{i}: {label:10s} -> {p:.4f}")
        top = int(np.argmax(preds))
        print(f"Top: {LABELS[top]} (index {top}) with confidence {preds[top]:.4f}")

        # simple heuristics
        non_qr_conf = preds[2] if len(preds) > 2 else 0.0
        max_conf = float(preds.max())
        diff_fg = abs(preds[0] - preds[1]) if len(preds) > 1 else 1.0
        print('Heuristics:')
        print(f" - non_qr_conf = {non_qr_conf:.4f}")
        print(f" - max_conf = {max_conf:.4f}")
        print(f" - fake vs genuine diff = {diff_fg:.4f}")
        if non_qr_conf > 0.3:
            print(' -> Recommend: Non-QR (non_qr_conf > 0.3)')
        elif max_conf < 0.5:
            print(' -> Recommend: Non-QR (low overall confidence)')
        elif len(preds) > 1 and diff_fg < 0.15:
            print(' -> Recommend: Non-QR (fake vs genuine uncertain)')
        else:
            print(' -> Recommend: Accept top prediction')

    print_preds(preds_bgr, 'BGR (cv2)')
    print_preds(preds_rgb, 'RGB (cv2->RGB)')

    print('\nNote: If BGR vs RGB produces large differences, ensure your app preprocesses images the same way as training (cv2.imread + resize + /255).')
    print('If the model still confidently predicts "genuine" for screenshots, add representative screenshots to dataset/non_qr and retrain using train_improved.py (it uses augmentation and class weights).')

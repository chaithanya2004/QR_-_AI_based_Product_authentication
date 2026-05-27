import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.optimizers import Adam

# ✅ Path to your dataset folder
DATASET_DIR = "dataset/archive"  # <-- change if needed

# ✅ Image size
IMG_SIZE = 128

# ✅ Labeling logic: 
# v1, v2 → Genuine | v3, v4 → Fake
def get_label(filename):
    filename = filename.lower()
    if "v1" in filename or "v2" in filename:
        return 0  # Genuine
    elif "v3" in filename or "v4" in filename:
        return 1  # Fake
    else:
        return None  # Skip unrecognized

# ✅ Load dataset
images = []
labels = []

for file in os.listdir(DATASET_DIR):
    path = os.path.join(DATASET_DIR, file)
    if not (file.endswith(".jpg") or file.endswith(".png")):
        continue
    label = get_label(file)
    if label is not None:
        img = cv2.imread(path)
        if img is None:
            continue
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = img_to_array(img) / 255.0
        images.append(img)
        labels.append(label)

images = np.array(images)
labels = np.array(labels)
labels = to_categorical(labels, num_classes=2)

print(f"✅ Total images loaded: {len(images)}")

# ✅ Split into train/test
X_train, X_test, y_train, y_test = train_test_split(
    images, labels, test_size=0.2, random_state=42
)

# ✅ Build CNN Model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(2, activation='softmax')
])

# ✅ Compile
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# ✅ Train
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=16,
    validation_split=0.1
)

# ✅ Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"🎯 Test Accuracy: {acc * 100:.2f}%")

# ✅ Save Model
model.save("qr_authenticator_model.h5")
print("💾 Model saved as qr_authenticator_model.h5") 















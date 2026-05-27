import os
import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# --- CONFIG ---
DATASET_DIR = "dataset"
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)
IMG_SIZE = 128
BATCH_SIZE = 32
EPOCHS = 25
SEED = 42

# --- DATA AUGMENTATION & GENERATORS ---
datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    validation_split=0.20,
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True,
    fill_mode='nearest'
)

train_gen = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    seed=SEED
)

val_gen = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    seed=SEED
)

# --- Class weights to mitigate imbalance ---
train_classes = train_gen.classes
classes_unique = np.unique(train_classes)
class_weights = compute_class_weight('balanced', classes=classes_unique, y=train_classes)
class_weight_dict = {int(i): w for i, w in enumerate(class_weights)}
print("Class indices (label -> folder):", train_gen.class_indices)
print("Class weights:", class_weight_dict)

# --- MODEL ---
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),

    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(len(train_gen.class_indices), activation='softmax')
])

model.compile(
    optimizer=Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# --- TRAIN ---
steps_per_epoch = max(1, train_gen.samples // BATCH_SIZE)
validation_steps = max(1, val_gen.samples // BATCH_SIZE)

history = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    validation_data=val_gen,
    validation_steps=validation_steps,
    epochs=EPOCHS,
    class_weight=class_weight_dict
)

# --- EVALUATE on validation set ---
val_steps_full = int(np.ceil(val_gen.samples / BATCH_SIZE))
val_gen.reset()
probs = model.predict(val_gen, steps=val_steps_full)

y_pred = np.argmax(probs, axis=1)
y_true = val_gen.classes[:len(y_pred)]

print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=list(train_gen.class_indices.keys())))
print("Confusion Matrix:")
print(confusion_matrix(y_true, y_pred))

# --- Save model ---
model_path = os.path.join(MODEL_DIR, 'qr_authenticator_model.h5')
model.save(model_path)
print(f"Model saved to {model_path}")

# --- Plot training curves ---
plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='train_loss')
plt.plot(history.history['val_loss'], label='val_loss')
plt.legend(); plt.title('Loss')

plt.subplot(1,2,2)
plt.plot(history.history['accuracy'], label='train_acc')
plt.plot(history.history['val_accuracy'], label='val_acc')
plt.legend(); plt.title('Accuracy')

plt.tight_layout()
plt.savefig('training_history.png')
print('Saved training_history.png')

# --- Quick inference helper (example) ---
if __name__ == '__main__':
    # Example: run inference on a single image (change path as needed)
    import cv2
    example_path = None  # set path to a sample image to test
    if example_path and os.path.exists(example_path):
        img = cv2.imread(example_path)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        x = img.astype('float32') / 255.0
        x = np.expand_dims(x, axis=0)
        preds = model.predict(x)[0]
        idx = np.argmax(preds)
        label_map = {v:k for k,v in train_gen.class_indices.items()}
        print('Pred:', list(train_gen.class_indices.keys())[idx], 'confidence:', preds[idx])
    else:
        print('To test a single image, set example_path variable in this file and re-run.')

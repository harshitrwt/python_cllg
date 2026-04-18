"""
Fashion Product Classifier — MobileNetV2 Transfer Learning
===========================================================
Trains a CNN on the Kaggle fashion dataset to classify product images
into subcategories (Shoes, Topwear, Bottomwear, Sandals, etc.)

Usage:
    python -m ml_model.train_model
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Suppress TF info logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# ─── Configuration ───────────────────────────────────────────────
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 0.001
FINE_TUNE_EPOCHS = 5
FINE_TUNE_LR = 0.0001

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "ml_data" / "data"
CSV_PATH = DATA_DIR / "fashion.csv"
MODEL_SAVE_PATH = Path(__file__).resolve().parent / "fashion_classifier.h5"
LABELS_SAVE_PATH = Path(__file__).resolve().parent / "class_labels.json"
HISTORY_SAVE_PATH = Path(__file__).resolve().parent / "training_history.json"

# Image subdirectories inside the dataset
IMAGE_DIRS = {
    ("Apparel", "Boys"):    DATA_DIR / "Apparel" / "Boys" / "Images" / "images_with_product_ids",
    ("Apparel", "Girls"):   DATA_DIR / "Apparel" / "Girls" / "Images" / "images_with_product_ids",
    ("Footwear", "Men"):    DATA_DIR / "Footwear" / "Men" / "Images" / "images_with_product_ids",
    ("Footwear", "Women"):  DATA_DIR / "Footwear" / "Women" / "Images" / "images_with_product_ids",
}


def find_image_path(row):
    """Locate the actual image file for a given CSV row."""
    filename = str(row["Image"])
    category = row["Category"]
    gender = row["Gender"]
    
    # Map gender to folder names
    gender_map = {
        "Boys": "Boys", "Girls": "Girls",
        "Men": "Men", "Women": "Women"
    }
    
    folder_gender = gender_map.get(gender)
    if not folder_gender:
        return None
    
    key = (category, folder_gender)
    img_dir = IMAGE_DIRS.get(key)
    
    if img_dir and img_dir.exists():
        img_path = img_dir / filename
        if img_path.exists():
            return str(img_path)
    
    return None


def load_and_preprocess_image(path, label):
    """Load an image from disk, resize, and normalize for MobileNetV2."""
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    return img, label


def build_model(num_classes):
    """Build MobileNetV2 with a custom classification head."""
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze the base model layers initially
    base_model.trainable = False
    
    # Custom classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation="relu")(x)
    x = Dropout(0.4)(x)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.3)(x)
    output = Dense(num_classes, activation="softmax")(x)
    
    model = Model(inputs=base_model.input, outputs=output)
    return model, base_model


def train():
    """Main training pipeline."""
    print("=" * 60)
    print("  Fashion Classifier - MobileNetV2 Transfer Learning")
    print("=" * 60)
    
    # ─── Step 1: Load CSV & map image paths ──────────────────────
    print("\n[LOAD] Loading dataset...")
    df = pd.read_csv(CSV_PATH)
    print(f"   CSV loaded: {len(df)} entries")
    
    df["image_path"] = df.apply(find_image_path, axis=1)
    df = df.dropna(subset=["image_path"])
    print(f"   Images found: {len(df)} (matched to disk)")
    
    # ─── Step 2: Encode labels ───────────────────────────────────
    labels_sorted = sorted(df["SubCategory"].unique())
    label_to_idx = {label: idx for idx, label in enumerate(labels_sorted)}
    idx_to_label = {idx: label for label, idx in label_to_idx.items()}
    
    df["label_idx"] = df["SubCategory"].map(label_to_idx)
    num_classes = len(labels_sorted)
    
    print(f"\n[CLASSES] Classes ({num_classes}):")
    for label, idx in label_to_idx.items():
        count = len(df[df["SubCategory"] == label])
        print(f"   [{idx}] {label}: {count} images")
    
    # Save class labels for inference
    with open(LABELS_SAVE_PATH, "w") as f:
        json.dump(idx_to_label, f, indent=2)
    print(f"\n[SAVE] Class labels saved to: {LABELS_SAVE_PATH}")
    
    # ─── Step 3: Train/Val Split ─────────────────────────────────
    train_df, val_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label_idx"]
    )
    print(f"\n[SPLIT] Split: {len(train_df)} train / {len(val_df)} val")
    
    # ─── Step 4: Build tf.data pipelines ─────────────────────────
    print("\n[DATA] Building data pipelines...")
    
    train_ds = tf.data.Dataset.from_tensor_slices(
        (train_df["image_path"].values, train_df["label_idx"].values)
    )
    val_ds = tf.data.Dataset.from_tensor_slices(
        (val_df["image_path"].values, val_df["label_idx"].values)
    )
    
    AUTOTUNE = tf.data.AUTOTUNE
    
    train_ds = (train_ds
        .shuffle(1000)
        .map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
        .batch(BATCH_SIZE)
        .prefetch(AUTOTUNE)
    )
    
    val_ds = (val_ds
        .map(load_and_preprocess_image, num_parallel_calls=AUTOTUNE)
        .batch(BATCH_SIZE)
        .prefetch(AUTOTUNE)
    )
    
    # ─── Step 5: Build & compile model ───────────────────────────
    print("\n[MODEL] Building MobileNetV2 model...")
    model, base_model = build_model(num_classes)
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    total_params = model.count_params()
    trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    print(f"   Total params: {total_params:,}")
    print(f"   Trainable params: {trainable_params:,}")
    print(f"   Frozen base layers: {len(base_model.layers)}")
    
    # ─── Step 6: Callbacks ───────────────────────────────────────
    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=4,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1
        ),
        ModelCheckpoint(
            str(MODEL_SAVE_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        )
    ]
    
    # ─── Step 7: Train (Phase 1 — frozen base) ──────────────────
    print(f"\n[PHASE 1] Training classification head ({EPOCHS} epochs)...")
    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # ─── Step 8: Fine-tune (Phase 2 — unfreeze top layers) ──────
    print(f"\n[PHASE 2] Fine-tuning top layers ({FINE_TUNE_EPOCHS} epochs)...")
    
    # Unfreeze the last 30 layers of the base model
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False
    
    model.compile(
        optimizer=Adam(learning_rate=FINE_TUNE_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=FINE_TUNE_EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # ─── Step 9: Save final model & history ──────────────────────
    model.save(str(MODEL_SAVE_PATH))
    
    # Merge and save training history
    full_history = {}
    for key in history1.history:
        full_history[key] = history1.history[key] + history2.history[key]
    
    # Convert numpy values to Python floats for JSON serialization
    serializable_history = {}
    for key, values in full_history.items():
        serializable_history[key] = [float(v) for v in values]
    
    with open(HISTORY_SAVE_PATH, "w") as f:
        json.dump(serializable_history, f, indent=2)
    
    # ─── Step 10: Final evaluation ───────────────────────────────
    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    
    print("\n" + "=" * 60)
    print("  [OK] TRAINING COMPLETE")
    print("=" * 60)
    print(f"   Final Val Accuracy : {val_acc * 100:.2f}%")
    print(f"   Final Val Loss     : {val_loss:.4f}")
    print(f"   Model saved to     : {MODEL_SAVE_PATH}")
    print(f"   Labels saved to    : {LABELS_SAVE_PATH}")
    print(f"   History saved to   : {HISTORY_SAVE_PATH}")
    print("=" * 60)
    
    return model, full_history


if __name__ == "__main__":
    train()

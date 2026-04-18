"""
Fashion Product Predictor — Inference Module
=============================================
Loads the trained MobileNetV2 model and provides predictions
for product images (from file upload or URL).
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from io import BytesIO

# Suppress TF info logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from PIL import Image
import requests

logger = logging.getLogger(__name__)

IMG_SIZE = 224
MODEL_PATH = Path(__file__).resolve().parent / "fashion_classifier.h5"
LABELS_PATH = Path(__file__).resolve().parent / "class_labels.json"
HISTORY_PATH = Path(__file__).resolve().parent / "training_history.json"


class FashionPredictor:
    """
    Loads the trained CNN model and classifies fashion product images.
    
    Usage:
        predictor = FashionPredictor()
        if predictor.is_ready():
            result = predictor.predict_from_file(uploaded_file)
            # result = {"predictions": [...], "top_class": "Shoes", "confidence": 0.95}
    """
    
    def __init__(self):
        self.model = None
        self.class_labels = None
        self.history = None
        self._load()
    
    def _load(self):
        """Load model and class labels from disk."""
        try:
            if MODEL_PATH.exists() and LABELS_PATH.exists():
                self.model = tf.keras.models.load_model(str(MODEL_PATH))
                with open(LABELS_PATH, "r") as f:
                    self.class_labels = json.load(f)
                logger.info(f"CNN model loaded: {len(self.class_labels)} classes")
            else:
                logger.warning("CNN model not found. Please train first: python -m ml_model.train_model")
        except Exception as e:
            logger.error(f"Error loading CNN model: {e}")
            self.model = None
    
    def is_ready(self):
        """Check if the model is loaded and ready for predictions."""
        return self.model is not None and self.class_labels is not None
    
    def get_training_history(self):
        """Load and return training history for visualization."""
        try:
            if HISTORY_PATH.exists():
                with open(HISTORY_PATH, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading training history: {e}")
        return None
    
    def get_model_summary(self):
        """Return model metadata."""
        if not self.is_ready():
            return None
        return {
            "num_classes": len(self.class_labels),
            "classes": list(self.class_labels.values()),
            "input_shape": f"{IMG_SIZE}x{IMG_SIZE}x3",
            "total_params": self.model.count_params(),
            "model_file": str(MODEL_PATH),
            "model_size_mb": round(MODEL_PATH.stat().st_size / (1024 * 1024), 2) if MODEL_PATH.exists() else 0
        }
    
    def _preprocess_image(self, img: Image.Image) -> np.ndarray:
        """Convert a PIL Image to a preprocessed numpy array for MobileNetV2."""
        img = img.convert("RGB")
        img = img.resize((IMG_SIZE, IMG_SIZE))
        img_array = np.array(img, dtype=np.float32)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array
    
    def predict_from_pil(self, pil_image: Image.Image, top_k: int = 3) -> dict:
        """
        Predict the fashion category from a PIL Image.
        
        Returns:
            {
                "success": True,
                "top_class": "Shoes",
                "confidence": 0.95,
                "predictions": [
                    {"class": "Shoes", "confidence": 0.95},
                    {"class": "Sandal", "confidence": 0.03},
                    {"class": "Flip Flops", "confidence": 0.01},
                ]
            }
        """
        if not self.is_ready():
            return {"success": False, "error": "Model not loaded. Train first."}
        
        try:
            img_array = self._preprocess_image(pil_image)
            predictions = self.model.predict(img_array, verbose=0)[0]
            
            # Get top-k predictions
            top_indices = predictions.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                class_name = self.class_labels.get(str(idx), f"Unknown-{idx}")
                confidence = float(predictions[idx])
                results.append({
                    "class": class_name,
                    "confidence": confidence
                })
            
            return {
                "success": True,
                "top_class": results[0]["class"],
                "confidence": results[0]["confidence"],
                "predictions": results
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"success": False, "error": str(e)}
    
    def predict_from_file(self, file_bytes) -> dict:
        """Predict from uploaded file bytes (e.g., Streamlit UploadedFile)."""
        try:
            img = Image.open(BytesIO(file_bytes) if isinstance(file_bytes, bytes) else file_bytes)
            return self.predict_from_pil(img)
        except Exception as e:
            return {"success": False, "error": f"Could not read image: {e}"}
    
    def predict_from_url(self, image_url: str) -> dict:
        """Download an image from URL and predict."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            return self.predict_from_pil(img)
        except Exception as e:
            return {"success": False, "error": f"Could not download image: {e}"}

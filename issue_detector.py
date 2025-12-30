import tensorflow as tf
import numpy as np
from PIL import Image
import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

model = None

try:
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
except Exception:
    model = None

def detect_issue_with_ai(image_path):
    global model
    try:
        if model is None:
            return "Civic Issue", "Verified (AI System Offline)"

        img = Image.open(image_path).convert('RGB').resize((224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

        predictions = model.predict(img_array)
        results = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=30)[0]

        issue_map = {
            'pothole': 'Damaged Road / Pothole',
            'ashcan': 'Garbage Pile',
            'trash': 'Garbage Pile',
            'garbage': 'Garbage Pile',
            'street_light': 'Broken Streetlight',
            'lamppost': 'Broken Streetlight',
            'drain': 'Clogged Drain',
            'manhole': 'Open Manhole'
        }
        
        for (id, label, prob) in results:
            label_lower = label.lower()
            for key, display_name in issue_map.items():
                if key in label_lower and prob > 0.02: 
                    return display_name, f"Verified by AI ({prob*100:.1f}%)"

        return "Invalid", "AI was unsure, please use manual submission."
        
    except Exception:
        return "Invalid", "AI Processing Error"
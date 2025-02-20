import re
import pandas as pd
import numpy as np
import joblib
import json
import os
from azureml.core.model import Model
from azureml.core import Workspace
from azureml.core import Run
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,auc

# Same feature extraction used in training
def extract_features(texts):
    return pd.DataFrame({
        'length': [len(text) for text in texts],
        'word_count': [len(text.split()) for text in texts],
        'has_urgency': [1 if re.search(r'\b(urgent|immediately|now|quick|action required|expire)\b', text.lower()) else 0 for text in texts],
        'has_money': [1 if re.search(r'\b(win|prize|cash|free|bonus|reward|\$|money|dollar|million|billion)\b', text.lower()) else 0 for text in texts],
        'has_link': [1 if re.search(r'http|www|\.com|\.net|\.org|click|\.link|bit\.ly|goo\.gl', text.lower()) else 0 for text in texts],
        'special_char_count': [len(re.findall(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]', text)) for text in texts],
        'has_greeting': [1 if re.search(r'^dear|hello|hi |greetings|valued customer', text.lower()) else 0 for text in texts],
        'has_threat': [1 if re.search(r'\b(suspend|close|terminate|verify|confirm|account|security|alert)\b', text.lower()) else 0 for text in texts]
    })

def init():
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'phishingmodel.pkl')
    model = joblib.load(model_path)

def run(raw_data):
    try:
        data = json.loads(raw_data)
        messages = data['data']

        # Extract features
        features = extract_features(messages)

        # Predict
        probabilities = model.predict_proba(features)[:, 1] * 100
        predictions = model.predict(features)

        # Format result
        results = []
        for msg, pred, prob in zip(messages, predictions, probabilities):
            if prob > 15:
                risk = {"level": "high", "color": "red"}
            elif prob > 10:
                risk = {"level": "medium", "color": "yellow"}
            else:
                risk = {"level": "low", "color": "green"}

            results.append({
                "message": msg,
                "prediction": "phishing" if pred == 1 else "safe",
                "probability": float(prob),
                "risk": risk
            })

        return json.dumps({"results": results})
    
    except Exception as e:
        return json.dumps({"error": str(e), "success": False})
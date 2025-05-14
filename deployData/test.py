import numpy as np
import pandas as pd
import re
import joblib

def extract_features(texts):
    features = pd.DataFrame({
        'length': [len(text) for text in texts],
        'word_count': [len(text.split()) for text in texts],
        'has_urgency': [1 if re.search(r'\b(urgent|immediately|now|quick|action required|expire)\b', text.lower()) else 0 for text in texts],
        'has_money': [1 if re.search(r'\b(win|prize|cash|free|bonus|reward|\$|money|dollar|million|billion)\b', text.lower()) else 0 for text in texts],
        'has_link': [1 if re.search(r'http|www|\.com|\.net|\.org|click|\.link|bit\.ly|goo\.gl', text.lower()) else 0 for text in texts],
        'special_char_count': [len(re.findall(r'[!@#$%^&*()_+\-=\[\]{};:\'"\\|,.<>\/?]', text)) for text in texts],
        'has_greeting': [1 if re.search(r'^dear|hello|hi |greetings|valued customer', text.lower()) else 0 for text in texts],
        'has_threat': [1 if re.search(r'\b(suspend|close|terminate|verify|confirm|account|security|alert)\b', text.lower()) else 0 for text in texts]
    })
    return features


rf = joblib.load("phishingmodel.pkl")

test_messages = [
    "Congratulations! You've won a free iPhone. Click here to claim.",
    "URGENT: Your bank account will be suspended. Verify immediately!",
    "Hey, are we still meeting for coffee later?",
    "Limited time offer! Free gift for you. Act now!",
    "Your account needs verification. Click www.suspicious-link.com"
]

print("\nTest Predictions with Probabilities:")

# Extract features
features = extract_features(test_messages)

# Predict
for i, message in enumerate(test_messages):
    msg_features = features.iloc[[i]]
    proba = rf.predict_proba(msg_features)[0][1] * 100
    prediction = rf.predict(msg_features)[0]
    result = "Phishing" if prediction == 1 else "Safe"

    print(f"\nMessage: {message}")
    print(f"Prediction: {result}")
    print(f"Phishing Probability: {proba:.2f}%")
    
    if proba > 15:
        print("Risk:High Red")
    elif proba > 10:
        print("Risk:Medium Yellow")
    else:
        print("Risk:Low Green")
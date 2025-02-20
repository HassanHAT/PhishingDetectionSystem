import numpy as np
import pandas as pd
import re
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Feature extraction
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

# Load and prepare data
sms = pd.read_csv('./PhishingData.csv', encoding='latin-1')

sms = sms.rename(columns={"v1":"label", "v2":"text"})

sms = sms.dropna(subset=['text','label'])

sms['label'] = sms['label'].map({'ham': 0,'spam': 1})

# Drop rows not mapping
sms = sms.dropna(subset=['label'])

# Convert label to integer
sms['label'] = sms['label'].astype(int)

# Feature extraction
X = extract_features(sms['text'])
y = sms['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Train RandomForest
rf = RandomForestClassifier(n_estimators=300, max_depth=25, min_samples_split=5, class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Evaluate
y_pred = rf.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(rf, "phishingmodel.pkl")



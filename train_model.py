import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

SYMPTOMS = [
    "cough", "fever", "fatigue", "headache", "nausea",
    "chest pain", "shortness of breath", "sore throat",
    "runny nose", "body ache"
]

data = [
    (["cough", "fever", "shortness of breath"], "Pneumonia"),
    (["cough", "fever", "fatigue"],              "Pneumonia"),
    (["cough", "chest pain"],                    "Pneumonia"),
    (["headache", "fatigue", "nausea"],          "Migraine"),
    (["headache", "nausea"],                     "Migraine"),
    (["runny nose", "sore throat", "fatigue"],   "Common Cold"),
    (["runny nose", "sore throat"],              "Common Cold"),
    (["fever", "body ache", "fatigue"],          "Influenza"),
    (["fever", "body ache", "headache"],         "Influenza"),
    (["nausea", "fatigue"],                      "General Checkup"),
    (["headache"],                               "General Checkup"),
]

X_raw = [d[0] for d in data]
y     = [d[1] for d in data]

mlb = MultiLabelBinarizer(classes=SYMPTOMS)
X   = mlb.fit_transform(X_raw)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "model.pkl")
joblib.dump(mlb,   "mlb.pkl")

print("Model trained and saved as model.pkl and mlb.pkl")
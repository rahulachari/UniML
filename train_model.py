import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

np.random.seed(42)

rows = 800
data = []

for _ in range(rows):
    hb = round(np.random.uniform(8, 17), 1)
    wbc = np.random.randint(4000, 15000)
    sugar = np.random.randint(70, 200)
    bp = np.random.randint(90, 160)
    pulse = np.random.randint(60, 110)

    # Condition logic (realistic hierarchy)
    if sugar > 160:
        condition = "Diabetes"
    elif hb < 11:
        condition = "Anemia"
    elif wbc > 11000:
        condition = "Infection"
    elif bp > 140:
        condition = "Hypertension"
    elif pulse > 100:
        condition = "Cardiac Stress"
    else:
        condition = "Healthy"

    data.append([hb, wbc, sugar, bp, pulse, condition])

df = pd.DataFrame(data, columns=[
    "hemoglobin", "wbc", "sugar", "bp", "pulse", "condition"
])

X = df.drop("condition", axis=1)
y = df["condition"]

model = RandomForestClassifier(n_estimators=150)
model.fit(X, y)

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/healthcare_model.pkl")

print("✅ Model trained and saved")
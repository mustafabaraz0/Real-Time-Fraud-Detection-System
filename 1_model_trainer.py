import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import time
import os

print("[MLOps] Initiating AI Model Training and Serialization Process...")
start_time = time.time()

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'bank_transactions.db')

# Extract historical data for training
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM Transactions", conn)
conn.close()

# Feature Engineering: Extracting chronological context (Hour)
df['TransactionTime'] = pd.to_datetime(df['TransactionTime'])
df['Hour'] = df['TransactionTime'].dt.hour

# One-Hot Encoding for categorical features
features = pd.get_dummies(df[['Amount', 'LocationCode', 'Hour', 'Device', 'Merchant']])

# Persist the column structure to ensure consistent dimensions during live inference
model_columns = list(features.columns)
joblib.dump(model_columns, os.path.join(current_dir, 'model_columns.pkl'))

print("[TRAINING] Fitting Isolation Forest model with 300 estimators...")
# contamination=0.02 matches the 2% fraud injection rate in the dataset
model = IsolationForest(n_estimators=300, max_samples='auto', contamination=0.02, random_state=42, n_jobs=-1)
model.fit(features)

# Serialize and save the trained model
model_path = os.path.join(current_dir, 'fraud_model.pkl')
joblib.dump(model, model_path)

# Performance Evaluation
df['AI_Prediction'] = model.predict(features)
df['AI_Prediction'] = df['AI_Prediction'].map({1: 0, -1: 1})

true_frauds = len(df[df['IsFraud'] == 1])
caught_frauds = len(df[(df['IsFraud'] == 1) & (df['AI_Prediction'] == 1)])
accuracy_rate = (caught_frauds / true_frauds) * 100 if true_frauds > 0 else 0

end_time = time.time()
print("-" * 50)
print(f"[SUCCESS] Model training completed in {round(end_time - start_time, 2)} seconds.")
print(f"[ARTIFACT] Model serialized to: fraud_model.pkl")
print(f"[PERFORMANCE] Fraud Detection Accuracy Rate: {round(accuracy_rate, 2)}%")
print("-" * 50)
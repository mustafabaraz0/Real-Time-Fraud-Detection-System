import sqlite3
import pandas as pd
import joblib
import time
import os
from datetime import datetime
import random
import warnings

warnings.filterwarnings("ignore")

print("[SYSTEM] HYBRID SECURITY ARCHITECTURE: MULTI-VECTOR ATTACK SIMULATION ACTIVE...")

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'bank_transactions.db')
model_path = os.path.join(current_dir, 'fraud_model.pkl')
columns_path = os.path.join(current_dir, 'model_columns.pkl')

# Load the serialized model and its expected feature dimensions
model = joblib.load(model_path)
model_columns = joblib.load(columns_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Live_Fraud_Alerts (
        AlertID INTEGER PRIMARY KEY AUTOINCREMENT,
        AccountID INTEGER,
        Amount REAL,
        LocationCode INTEGER,
        Device TEXT,
        Merchant TEXT,
        TransactionTime TEXT,
        RiskScore REAL
    )
''')
conn.commit()

# In-memory store for velocity (frequency) rule enforcement
account_history = {} 

print("[MLOps] AI Engine Online. Advanced Scenarios & Velocity Enforcer Active.")
print("-" * 90)

burst_mode_active = False
burst_account_id = 0
burst_count = 0

def get_logical_transaction(is_attack, burst_acc=None):
    """Generates logically consistent transaction data based on the provided state."""
    account_id = burst_acc if burst_acc else random.randint(1000, 5000)
    
    if is_attack:
        attack_type = random.choice(['Account_Takeover', 'ATM_Skimming', 'POS_Cloned_Card'])
        
        if attack_type == 'Account_Takeover':
            amount = round(random.uniform(25000.0, 75000.0), 2)
            location = random.randint(90, 101) 
            device = 'Web_Browser'
            merchant = random.choice(['Crypto_Exchange', 'International_Transfer'])
            
        elif attack_type == 'ATM_Skimming':
            amount = round(random.uniform(8000.0, 15000.0), 2) 
            location = random.randint(70, 85)
            device = 'ATM'
            merchant = 'Cash_Withdrawal'
            
        else: # POS_Cloned_Card
            amount = round(random.uniform(30000.0, 60000.0), 2) 
            location = random.randint(1, 51)
            device = 'POS_Device'
            merchant = 'Electronics'
    else:
        # Legitimate customer behavior logic
        amount = round(abs(random.gauss(150.0, 80.0)), 2)
        location = random.randint(1, 51)
        device = random.choices(['Mobile_App', 'POS_Device', 'ATM', 'Web_Browser'], weights=[0.4, 0.4, 0.1, 0.1])[0]
        
        if device == 'ATM':
            merchant = random.choice(['Cash_Withdrawal', 'Cash_Deposit'])
        elif device == 'POS_Device':
            merchant = random.choice(['Grocery', 'Restaurant', 'Clothing', 'Electronics'])
        elif device == 'Mobile_App':
            merchant = random.choice(['Utility_Bill', 'Bank_Transfer', 'Credit_Card_Payment'])
        else:
            merchant = random.choice(['Electronics', 'Clothing', 'Flight_Ticket'])
            
    return account_id, amount, location, device, merchant

try:
    while True:
        # Velocity attack simulation logic
        if burst_mode_active:
            time.sleep(0.1) 
            is_attack = True
            account_id, amount, location, device, merchant = get_logical_transaction(is_attack, burst_account_id)
            burst_count -= 1
            if burst_count <= 0:
                burst_mode_active = False 
        else:
            time.sleep(random.uniform(0.5, 1.5))
            if random.random() < 0.02:
                burst_mode_active = True
                burst_account_id = random.randint(1000, 5000)
                burst_count = 5 
                print(f"\n⚠️ [SIMULATION TRIGGERED] Bot-Net Velocity Attack initiated on Account {burst_account_id}!")
                continue
            else:
                is_attack = random.random() < 0.04 
                account_id, amount, location, device, merchant = get_logical_transaction(is_attack)

        now = datetime.now()
        time_only = now.strftime('%H:%M:%S') 
        full_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

        # LAYER 1: RULE-BASED ENGINE (VELOCITY CHECK)
        if account_id not in account_history:
            account_history[account_id] = []
        account_history[account_id].append(now)
        # Retain only transactions from the last 30 seconds
        account_history[account_id] = [t for t in account_history[account_id] if (now - t).total_seconds() < 30]

        if len(account_history[account_id]) >= 3:
            print(f"🛑 [BLOCKED] Time: {time_only} | Account: {account_id} locked! Reason: Velocity Rule Violation.", flush=True)
            cursor.execute('''INSERT INTO Live_Fraud_Alerts (AccountID, Amount, LocationCode, Device, Merchant, TransactionTime, RiskScore) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                        (account_id, amount, location, device, merchant, full_time_str, 99.9))
            conn.commit()
            continue

        # LAYER 2: AI INFERENCE (ISOLATION FOREST)
        live_data = pd.DataFrame([{'Amount': amount, 'LocationCode': location, 'Hour': now.hour, 'Device': device, 'Merchant': merchant}])
        live_features = pd.get_dummies(live_data)
        # Align features with the training configuration to prevent schema mismatch errors
        live_features = live_features.reindex(columns=model_columns, fill_value=0)

        prediction = model.predict(live_features)[0] 
        raw_score = model.decision_function(live_features)[0]

        if prediction == -1: 
            # Normalize the decision function output to a realistic risk percentage (60% - 99%)
            risk_score = round(min(99.9, 60.0 + (abs(raw_score) * 350)), 2)
            
            print(f"🚨 [AI ALERT] Time: {time_only} | Account: {account_id} | {amount} TRY | {device} -> {merchant} | Risk: {risk_score}%", flush=True)
            cursor.execute('''INSERT INTO Live_Fraud_Alerts (AccountID, Amount, LocationCode, Device, Merchant, TransactionTime, RiskScore) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                        (account_id, amount, location, device, merchant, full_time_str, risk_score))
            conn.commit()
        else:
            print(f"✅ [SECURE] Time: {time_only} | Account: {account_id} | {amount} TRY | {device} -> {merchant}", flush=True)

except KeyboardInterrupt:
    print("\n[SYSTEM] Server safely terminated by user.")
    conn.close()
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

print("[SYSTEM] Initializing Comprehensive Banking Database Engine...")

# Configuration parameters for synthetic data generation
num_transactions = 250_000
start_time = datetime(2026, 4, 1, 0, 0, 0)

# Transaction categories translated to English for international standards
devices = ['Mobile_App', 'POS_Device', 'ATM', 'Web_Browser']
merchants = ['Grocery', 'Restaurant', 'Utility_Bill', 'Clothing', 'Electronics', 'Crypto_Exchange', 'International_Transfer']

# Generate baseline normal transaction behavior
account_ids = np.random.randint(1000, 5000, num_transactions)
amounts = np.abs(np.random.normal(150.0, 80.0, num_transactions)) 
time_deltas = np.sort(np.random.randint(0, 30 * 24 * 60 * 60, num_transactions))
timestamps = [start_time + timedelta(seconds=int(s)) for s in time_deltas]
locations = np.random.randint(1, 51, num_transactions)

transaction_devices = np.random.choice(devices, num_transactions, p=[0.4, 0.4, 0.1, 0.1])
transaction_merchants = np.random.choice(merchants, num_transactions, p=[0.4, 0.3, 0.15, 0.1, 0.03, 0.01, 0.01])

is_fraud = np.zeros(num_transactions, dtype=int)

# Inject complex fraud scenarios (2% contamination rate)
fraud_indices = np.random.choice(num_transactions, size=5000, replace=False)

for idx in fraud_indices:
    is_fraud[idx] = 1
    attack_type = np.random.choice(['Account_Takeover', 'ATM_Skimming', 'POS_Cloned_Card'])
    
    if attack_type == 'Account_Takeover':
        amounts[idx] = np.random.uniform(25000.0, 75000.0)
        locations[idx] = np.random.randint(90, 101) # Suspicious foreign locations
        transaction_devices[idx] = 'Web_Browser'
        transaction_merchants[idx] = np.random.choice(['Crypto_Exchange', 'International_Transfer'])
    elif attack_type == 'ATM_Skimming':
        amounts[idx] = np.random.uniform(8000.0, 15000.0)
        locations[idx] = np.random.randint(70, 85)
        transaction_devices[idx] = 'ATM'
        transaction_merchants[idx] = 'Cash_Withdrawal'
    else: # POS_Cloned_Card
        amounts[idx] = np.random.uniform(30000.0, 60000.0)
        locations[idx] = np.random.randint(1, 51)
        transaction_devices[idx] = 'POS_Device'
        transaction_merchants[idx] = 'Electronics'

df = pd.DataFrame({
    'AccountID': account_ids,
    'Amount': np.round(amounts, 2),
    'LocationCode': locations,
    'Device': transaction_devices,
    'Merchant': transaction_merchants,
    'TransactionTime': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
    'IsFraud': is_fraud
})

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'bank_transactions.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS Transactions')
cursor.execute('''
    CREATE TABLE Transactions (
        TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
        AccountID INTEGER,
        Amount REAL,
        LocationCode INTEGER,
        Device TEXT,
        Merchant TEXT,
        TransactionTime TEXT,
        IsFraud INTEGER
    )
''')

df.to_sql('Transactions', conn, if_exists='append', index=False)
conn.commit()
conn.close()

print(f"[SUCCESS] {num_transactions} synthetic transaction records have been successfully written to the database.")
# 🛡️ End-to-End Real-Time Fraud Detection Engine & SOC Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![C#](https://img.shields.io/badge/C%23-.NET_8.0-purple.svg)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Scikit_Learn-orange.svg)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Architecture](https://img.shields.io/badge/Architecture-Microservice-success.svg)

An enterprise-grade, real-time Fraud Detection System built with a hybrid security architecture. This project simulates a live banking environment, utilizes Machine Learning (Isolation Forest) alongside a strict Rule-Based Velocity Engine to intercept multi-vector cyber attacks, and visualizes threats via an asynchronous WPF-based Security Operations Center (SOC) dashboard.

## 🧠 System Architecture

The system is decoupled into three primary microservice-like layers:

1. **Data Engineering & Simulation:** Generates a synthetic but highly realistic dataset of 250,000+ banking transactions, incorporating complex fraud vectors (Account Takeover, ATM Skimming, POS Cloned Cards).
2. **AI & Inference Engine (Backend):** A serialized `scikit-learn` Isolation Forest model integrated with an in-memory Velocity Rule Engine to process real-time transaction streams.
3. **SOC Dashboard (Frontend):** A C# WPF desktop application operating on an asynchronous polling mechanism to visualize intercepted threats with zero I/O blocking.

---

## 🚀 Key Features & Engineering Highlights

* **Hybrid Threat Detection:** Combines the predictive power of Unsupervised Machine Learning (Isolation Forest) with deterministic, stateful Velocity Rules (e.g., blocking 3+ transactions within 30 seconds from the same account) to eliminate False Negatives.
* **Real-Time MLOps & Inference:** Solves the *Training-Serving Skew* by persisting the feature schema (`model_columns.pkl`) during training and dynamically re-indexing incoming live JSON/Dictionary payloads for seamless inference.
* **I/O Optimized Database Buffering:** The Python backend writes blocked transactions to a local SQLite database, acting as a buffer. The C# WPF application reads from this database asynchronously, completely decoupling the UI thread from the heavy machine learning computations.
* **Dynamic Risk Scoring:** Normalizes the raw algorithmic anomaly distances into a realistic, human-readable Risk Percentage (60% - 99.9%) for security analysts.

---

## 🛠️ Technology Stack

* **Data Science & Backend:** Python, Pandas, NumPy, Scikit-Learn, Joblib
* **Frontend / Desktop:** C#, .NET, WPF (Windows Presentation Foundation), XAML
* **Data Persistence:** SQLite, ADO.NET (`Microsoft.Data.Sqlite`)

---

## ⚙️ Installation & Usage

### Prerequisites
Ensure you have Python 3.10+ and the .NET SDK installed on your machine.

### Step 1: Python Environment Setup
Install the required machine learning and data processing libraries:

```bash
pip install pandas numpy scikit-learn joblib
```

### Step 2: Build the Database
Generate the synthetic banking history and the SQLite database:

```bash
python database_builder.py
```
*Expected Output: A `bank_transactions.db` file containing 250,000 records.*

### Step 3: Train & Serialize the AI Model
Train the Isolation Forest model and generate the `.pkl` artifact:

```bash
python 1_model_trainer.py
```
*Expected Output: `fraud_model.pkl` and `model_columns.pkl` files.*

### Step 4: Initiate the Live Transaction Feed
Start the real-time simulation and inference engine:

```bash
python 2_live_transaction_stream.py
```
*Note: Leave this terminal running. It simulates nationwide live transactions and intercepts threats in real-time.*

### Step 5: Launch the SOC Dashboard
Open a new terminal, navigate to the `FraudDashboard` directory, and run the WPF application:

```bash
cd FraudDashboard
dotnet run
```

---

## 📈 Engineering Challenges Solved

1. **Handling Categorical Data in Live Streams:** Addressed dimensionality mismatch errors during real-time inference by saving the training phase's One-Hot Encoded columns and utilizing `pd.reindex()` with zero-filling for live payloads.
2. **Mitigating Data Drift:** Adjusted the `contamination` hyperparameter and enriched the baseline synthetic data to ensure the model correctly identifies edge-case anomalies (e.g., extreme high-value POS transactions).
3. **Cross-Platform IPC (Inter-Process Communication):** Utilized SQLite as a lightweight, thread-safe intermediary state manager between the Python inference engine and the C# UI, avoiding complex socket programming while maintaining sub-second latency.

---
*Designed and engineered for high-performance financial security environments.*
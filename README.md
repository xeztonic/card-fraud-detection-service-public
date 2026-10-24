<p align="center">
  <img src="app/static/images/logo.png" alt="Logo" width="110">
</p>

<h1 align="center">Suspicious Card Transaction Detection and Notification Service</h1>

<p align="center">
  A Flask web application that scores card transactions for fraud risk with a Random Forest model,
  monitors them on a live dashboard and sends email alerts for suspicious activity.
</p>

<p align="center"><em>Master's thesis project</em></p>

![Dashboard](app/static/images/Page%20Dashboard%201.png)

---

## Table of Contents

- [Overview](#overview)
- [Key Results](#key-results)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Screenshots](#screenshots)
- [How the Risk Score Works](#how-the-risk-score-works)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Limitations and Future Work](#limitations-and-future-work)
- [Dataset](#dataset)

---

## Overview

The project has two parts:

1. **Machine learning research** ([`notebooks/eda_ieee.ipynb`](notebooks/eda_ieee.ipynb)): exploratory analysis of the **IEEE-CIS Fraud Detection** dataset (590,540 transactions), preprocessing, and a comparison of four models. The full dataset was used for training and evaluation.
2. **Web application** (`app/`): a demonstration system built around the selected model. It scores transactions entered manually, imported from CSV files or streamed in a simulated live feed, combines the ML probability with behavioral rules into a **risk score from 0 to 100**, stores the results in SQLite, and notifies the administrator and the cardholder when a transaction looks suspicious.

---

## Key Results

Four models were trained and compared on a stratified 80/20 split (118,108 test transactions, 4,133 of them fraudulent):

| Model | ROC-AUC | Precision (fraud) | Recall (fraud) | F1 (fraud) |
|---|---|---|---|---|
| Logistic Regression (baseline) | 0.863 | 0.140 | 0.731 | 0.235 |
| **Random Forest (selected)** | **0.938** | **0.945** | 0.413 | **0.575** |
| LightGBM | 0.930 | 0.213 | **0.816** | 0.338 |
| CatBoost | 0.887 | 0.903 | 0.331 | 0.485 |

**Random Forest** was selected for the application: it achieved the highest ROC-AUC and F1-score while keeping false alerts low (Average Precision = 0.73).

**Threshold tuning:** at the default 0.5 threshold the model favors precision. Lowering the threshold to **0.20** raises the F1-score from 0.575 to **0.702** (precision 0.76, recall 0.66), showing how the system can be tuned to catch more fraud at the cost of more manual reviews.

---

## Tech Stack

| Area | Technologies |
|---|---|
| Backend | Python, Flask, Jinja2 |
| Machine learning | scikit-learn (Random Forest, Logistic Regression), LightGBM, CatBoost, joblib |
| Data processing | pandas, NumPy |
| Database | SQLite |
| Email | SMTP (Gmail, SSL) |
| Analysis and visualization | Jupyter, Matplotlib, Seaborn |
| Frontend | HTML, CSS, JavaScript |
| Configuration | python-dotenv |

---

## Features

- **Authentication**: admin login with Flask sessions (30-minute lifetime, HTTP-only cookies, no-cache headers so protected pages are not shown after logout). Both HTML pages and JSON endpoints are protected.
- **Dashboard**: total transactions, average risk score, alerts sent, high-risk rate, risk category distribution, and a transactions table with search across all fields, filtering by risk category and pagination.
- **Transaction simulation**: manual entry of a transaction, with presets for legitimate, suspicious and high-risk examples. The result shows the base ML probability, the behavioral adjustment, the final risk score, the risk category and the detected risk factors.
- **Email alerts**: for transactions classified as **Suspicious** or **High Risk** in the simulation page, the system emails the fraud monitoring administrator and the cardholder.
- **Live monitoring**: simulates a real-time stream by scoring transactions one by one from the dataset. Each point on the live chart is a transaction, colored by risk category, with details on hover.
- **CSV import**: uploads an IEEE-CIS transaction file (`train_transaction.csv` or `test_transaction.csv`), validates its structure and scores a random sample of up to 2,000 transactions. Files with a different structure (for example the ULB `creditcard.csv` dataset) are rejected.
- **CSV export and history management**: a side "Actions" panel to simulate a transaction, import or export CSV files and clear the transaction history.

---

## Screenshots

> **About the data shown:** the application is a demonstration of how the trained model works on real transaction data. The transactions in these screenshots were imported into the application from the IEEE-CIS dataset (through CSV import and live monitoring), plus a few transactions entered manually in the simulation page. They do not represent real customers.

### Dashboard

![Dashboard](app/static/images/Page%20Dashboard%201.png)

### Live monitoring

Each point is a transaction colored by risk (green = legitimate, orange = suspicious, red = high risk). Hovering over a point shows its details.

![Live monitoring](app/static/images/Page%20Dashboard%202%20info.png)

### Recent transactions

Search, risk category filter, alert status and expandable risk factors.

![Recent transactions](app/static/images/Page%20Dashboard%203.png)

### Transaction simulation

![Simulation](app/static/images/Page%20Simulation.png)

### Email alerts

| Administrator alert | Cardholder notification |
|---|---|
| <img src="app/static/images/Page%20Admin%20Alert%20Email.jpg" width="300"> | <img src="app/static/images/Page%20Customer%20Alert%20Email.jpg" width="300"> |

### Login, actions and CSV import

| Login | Actions panel | CSV import |
|---|---|---|
| ![Login](app/static/images/Page%20Login.png) | ![Actions](app/static/images/Page%20Side%20Menu%20Actions.png) | ![Import](app/static/images/Page%20Import%20csv.png) |

---

## How the Risk Score Works

### System architecture

![Architecture](app/static/images/6.1%20General%20Diagram.png)

### Scoring logic

```
Transaction ──▶ Random Forest ──▶ Base ML probability × 100
                                          │
                                          ▼
                          + Behavioral risk adjustment
                                          │
                                          ▼
                    Final risk score (capped at 100) ──▶ Risk category ──▶ Alerts
```

**Behavioral adjustment rules:**

| Rule | Points added |
|---|---|
| Amount above 1,000 | +25 |
| Amount above 3,000 | +25 (additional) |
| Distance from usual location above 100 | +15 |
| Distance from usual location above 300 | +15 (additional) |
| Email domain not in the trusted provider list | +10 |
| Product category `C` (highest fraud rate in the dataset: 11.7%) | +10 |

**Risk categories:**

| Final risk score | Category |
|---|---|
| below 30 | Legitimate |
| 30 – 69.99 | Suspicious |
| 70 and above | High Risk |

A "High Risk" transaction is not automatically fraud: it is a transaction that should be prioritized for verification or manual review.

---

## Machine Learning Pipeline

The full analysis is in [`notebooks/eda_ieee.ipynb`](notebooks/eda_ieee.ipynb).

1. **Data**: merged `train_transaction` and `train_identity` on `TransactionID` → 590,540 rows, 434 columns. Only **3.5%** of transactions are fraudulent, so accuracy is not a meaningful metric; ROC-AUC, precision, recall, F1 and the Precision-Recall curve were used instead.
2. **Cleaning**: dropped columns with more than 90% missing values; 420 features remained (29 categorical, 391 numeric).
3. **Train/test split**: 80/20, stratified on the target to keep the same fraud rate in both sets.
4. **Preprocessing**: Ordinal Encoding for categorical features and median imputation for missing values, both fitted **only on the training set** to avoid data leakage.
5. **Class imbalance**: handled with `class_weight="balanced"`.
6. **Model comparison**: Logistic Regression, Random Forest, LightGBM and CatBoost (see [Key Results](#key-results)).
7. **Evaluation of the final model**: confusion matrix, ROC curve, Precision-Recall curve, feature importance and threshold tuning.
8. **Export**: the model, encoder, imputer and feature lists are saved with `joblib` and loaded by the web application.

**Most important features:** `TransactionAmt`, `TransactionDT`, card attributes (`card1`, `card2`, `card5`) and aggregated behavioral features (`C1`, `C13`, `C14`, `D1`, `D2`, `D15`).

---

## Project Structure

```
card-fraud-detection-service/
├── app/
│   ├── app.py                    # Flask entry point
│   ├── requirements.txt
│   ├── routes/                   # auth, dashboard, simulation, file (CSV) and live routes
│   ├── services/
│   │   ├── dashboard_service.py  # statistics, filtering, pagination, chart data
│   │   └── risk_service.py       # risk factors, score breakdown, alert handling
│   ├── utils/
│   │   ├── predictor.py          # loads the model and computes the risk score
│   │   ├── csv_importer.py       # IEEE-CIS validation and batch scoring
│   │   ├── live_monitor.py       # simulated live transaction stream
│   │   ├── database.py           # SQLite storage and CSV export
│   │   ├── email_alert.py        # administrator alerts
│   │   ├── customer_alert.py     # cardholder notifications
│   │   └── auth.py               # login_required decorators
│   ├── templates/
│   └── static/images/            # logo, diagram and screenshots
├── models/                       # trained model and preprocessing artifacts
├── notebooks/
│   └── eda_ieee.ipynb            # EDA, training and model comparison
├── data/                         # dataset, SQLite database, uploads (not versioned)
├── .env.example
└── README.md
```

---

## Getting Started

### 1. Clone the repository and install dependencies

```bash
git clone https://github.com/<your-username>/card-fraud-detection-service.git
cd card-fraud-detection-service
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r app/requirements.txt
```

### 2. Download the dataset

The dataset is not included in this repository (Kaggle competition data cannot be redistributed). Download it from [Kaggle – IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection/data) and place the files in `data/dataset-ieee/`:

```
data/dataset-ieee/train_transaction.csv
data/dataset-ieee/train_identity.csv
data/dataset-ieee/test_transaction.csv
data/dataset-ieee/test_identity.csv
```

The live monitoring feature reads `train_transaction.csv` from this folder.

### 3. Extract the model file

Because of GitHub's file size limits, the trained model is stored as a 7-Zip archive. Extract it in place (for example with [7-Zip](https://www.7-zip.org/)) so that `models/random_forest_model.pkl` exists:

```
models/random_forest_model.pkl.7z
```

### 4. Configure environment variables

Copy `.env.example` to `.env` in the project root and fill in your values:

```env
SECRET_KEY=change_this_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_RECEIVER=admin@example.com
```

Email alerts are sent through Gmail SMTP, so `MAIL_PASSWORD` must be a Gmail [App Password](https://support.google.com/accounts/answer/185833), not your normal password. Without email settings the application still works; alerts are simply not sent.

### 5. Run the application

```bash
cd app
python app.py
```

Then open http://127.0.0.1:5000 and log in with the credentials from `.env`. The SQLite database (`data/transactions.db`) is created automatically on first run.

---

## Limitations and Future Work

- **Demo data**: CSV import and live monitoring use samples from the IEEE-CIS dataset, including the training file. They demonstrate the application's workflow, not the model's performance on unseen data; the model's evaluation is the test-set analysis in the notebook.
- **Simulation inputs**: the simulation form fills only a few of the 420 model features (the rest default to 0), so for manual transactions the behavioral rules have a large influence on the final score.
- **Validation split**: the data was split randomly (stratified). Because fraud patterns change over time, a time-based split on `TransactionDT` would give a more realistic estimate of future performance.
- **Rules and threshold**: the behavioral rules and the risk thresholds are set manually; they could be made configurable or tuned with feedback from analysts.
- **Alerts** are sent only from the simulation page; imported and live transactions are scored and stored without notifications.
- Possible extensions: per-transaction explanations (SHAP), hyperparameter optimization, a real message-queue stream, Docker deployment and automated tests.

---

## Dataset

[IEEE-CIS Fraud Detection](https://www.kaggle.com/competitions/ieee-fraud-detection), provided by Vesta Corporation via Kaggle.

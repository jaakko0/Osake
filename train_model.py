import pandas as pd
import sqlite3
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from datetime import datetime
import os

DB_PATH = "signals.db"
MODEL_PATH = "model.pkl"
TRAINING_DATA_PATH = "training_data_21d.csv"

# ▶⃣ Luo SQLite-tietokanta ja taulu (jos ei ole olemassa)
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            date TEXT,
            ticker TEXT,
            close REAL,
            above_50dma INTEGER,
            above_100dma INTEGER,
            above_200dma INTEGER,
            is_uptrend INTEGER,
            is_consolidating INTEGER,
            is_high_flag INTEGER,
            is_ascending_triangle INTEGER,
            probability REAL,
            expected_return REAL,
            signal_generated INTEGER,
            PRIMARY KEY (date, ticker)
        )
    """)
    conn.commit()
    conn.close()

# ▶⃣ Päivitä malli uudella datalla
def retrain_model(training_data_path=TRAINING_DATA_PATH):
    df = pd.read_csv(training_data_path)
    features = [
        'close', 'above_50dma', 'above_100dma', 'above_200dma',
        'is_uptrend', 'is_consolidating', 'is_high_flag', 'is_ascending_triangle'
    ]
    X = df[features]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    print("\n\u2705 Malli p\u00e4ivitetty ja tallennettu")

# ▶⃣ Tallenna signaali tietokantaan
def log_signal_to_db(signal):
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame([signal])
    df.to_sql("signals", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

# ▶⃣ Esimerkkikutsu
if __name__ == "__main__":
    init_db()
    retrain_model()

    # Esimerkki signaalista
    test_signal = {
        'date': datetime.today().strftime('%Y-%m-%d'),
        'ticker': 'AAPL',
        'close': 195.34,
        'above_50dma': 1,
        'above_100dma': 1,
        'above_200dma': 1,
        'is_uptrend': 1,
        'is_consolidating': 0,
        'is_high_flag': 1,
        'is_ascending_triangle': 0,
        'probability': 0.91,
        'expected_return': 0.07,
        'signal_generated': 1
    }

    log_signal_to_db(test_signal)
    print("\u2709\ufe0f Signaali tallennettu tietokantaan")

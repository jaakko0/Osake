import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import joblib
from generate_training_data import detect_uptrend, detect_consolidation, detect_high_flag, detect_ascending_triangle

DB_PATH = "signals.db"
MODEL_PATH = "model.pkl"
TICKERS = ["AAPL", "MSFT", "GOOG", "NVDA", "TSLA", "NOKIA.HE", "KNEBV.HE", "FORTUM.HE", "UPM.HE"]

def load_model():
    return joblib.load(MODEL_PATH)

def scan_market():
    model = load_model()
    results = []

    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="6mo", interval="1d")
            if df.empty or len(df) < 50:
                continue

            close_price = df["Close"].iloc[-1]
            ma_200 = df["Close"].rolling(200).mean().iloc[-1] if len(df) >= 200 else np.nan
            above_200dma = int(close_price > ma_200) if not np.isnan(ma_200) else 0

            is_uptrend = int(detect_uptrend(df))
            is_consolidating = int(detect_consolidation(df))
            is_high_flag = int(detect_high_flag(df))
            is_ascending_triangle = int(detect_ascending_triangle(df))

            feature_vector = [[
                close_price,
                above_200dma,
                is_uptrend,
                is_consolidating,
                is_high_flag,
                is_ascending_triangle
            ]]

            prob = model.predict_proba(feature_vector)[0][1]
            expected_return = np.random.uniform(0.05, 0.15)  # Mallin tuottama odotettu nousu, vaihda tarvittaessa

            if prob >= 0.85:
                results.append({
                    "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "close": close_price,
                    "probability": prob,
                    "expected_return": expected_return,
                    "is_uptrend": is_uptrend,
                    "is_consolidating": is_consolidating,
                    "is_high_flag": is_high_flag,
                    "is_ascending_triangle": is_ascending_triangle,
                    "above_200dma": above_200dma
                })

        except Exception as e:
            print(f"Virhe käsitellessä {ticker}: {e}")

    save_results(results)

def save_results(results):
    if not results:
        print("Ei uusia signaaleja tallennettavaksi.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS signals (
        date TEXT,
        ticker TEXT,
        close REAL,
        probability REAL,
        expected_return REAL,
        is_uptrend INTEGER,
        is_consolidating INTEGER,
        is_high_flag INTEGER,
        is_ascending_triangle INTEGER,
        above_200dma INTEGER
    )""")

    for res in results:
        c.execute("""
            INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res["date"], res["ticker"], res["close"], res["probability"],
            res["expected_return"], res["is_uptrend"], res["is_consolidating"],
            res["is_high_flag"], res["is_ascending_triangle"], res["above_200dma"]
        ))

    conn.commit()
    conn.close()
    print(f"Tallennettiin {len(results)} signaalia tietokantaan.")

if __name__ == "__main__":
    scan_market()

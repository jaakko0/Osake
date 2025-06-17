import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import sqlite3
from datetime import datetime
from generate_training_data import (
    add_indicators,
    is_uptrend,
    is_consolidating,
    is_high_flag,
    is_ascending_triangle
)

MODEL_PATH = "model.pkl"
DB_PATH = "signals.db"
TICKERS = ["AAPL", "MSFT", "GOOG", "NVDA", "AMD"]  # Voit myöhemmin lukea esim. tiedostosta
HOLDING_DAYS = 21
MIN_PROB = 0.9
MIN_EXPECTED_RETURN = 0.05
CAPITAL = 10000
RISK_PCT = 0.01

# ▶⃣ Tallenna signaali tietokantaan
def log_signal_to_db(signal):
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame([signal])
    df.to_sql("signals", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()

# ▶⃣ Lataa koulutettu malli
def load_model():
    return joblib.load(MODEL_PATH)

# ▶⃣ Analysoi osake ja tuota signaali jos ehdot täyttyvät
def analyze_latest(ticker, model):
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        df.dropna(inplace=True)
        df = add_indicators(df)
        i = -1  # viimeinen päivä

        features = {
            'close': df['Close'].iloc[i],
            'above_50dma': int(df['Close'].iloc[i] > df['50DMA'].iloc[i]),
            'above_100dma': int(df['Close'].iloc[i] > df['100DMA'].iloc[i]),
            'above_200dma': int(df['Close'].iloc[i] > df['200DMA'].iloc[i]),
            'is_uptrend': int(is_uptrend(df, len(df)-1)),
            'is_consolidating': int(is_consolidating(df, len(df)-1)),
            'is_high_flag': int(is_high_flag(df, len(df)-1)),
            'is_ascending_triangle': int(is_ascending_triangle(df, len(df)-1)),
        }

        X = pd.DataFrame([features])
        prob = model.predict_proba(X)[0][1]

        if prob >= MIN_PROB:
            signal = {
                'date': datetime.today().strftime('%Y-%m-%d'),
                'ticker': ticker,
                **features,
                'probability': round(prob, 4),
                'expected_return': MIN_EXPECTED_RETURN,
                'signal_generated': 1
            }
            log_signal_to_db(signal)
            print(f"\u2705 Signaali: {ticker} ({prob:.2%})")
    except Exception as e:
        print(f"Virhe {ticker}: {e}")

# ▶⃣ Pääajelu
if __name__ == "__main__":
    model = load_model()
    for ticker in TICKERS:
        analyze_latest(ticker, model)
    print("\n\u2709\ufe0f Valmis. Signaalit tallennettu tietokantaan, jos ehtoja täyttyi.")

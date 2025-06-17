import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm
import os

# Pattern-tunnistimet
def add_indicators(df):
    df['50DMA'] = df['Close'].rolling(50).mean()
    df['100DMA'] = df['Close'].rolling(100).mean()
    df['200DMA'] = df['Close'].rolling(200).mean()
    return df

def is_uptrend(df, i):
    if i < 220:
        return False
    return df['Close'].iloc[i] > df['200DMA'].iloc[i] and df['200DMA'].iloc[i] > df['200DMA'].iloc[i-20]

def is_consolidating(df, i, window=15, threshold=0.05):
    if i < window:
        return False
    recent = df['Close'].iloc[i-window:i]
    return (recent.max() - recent.min()) / recent.mean() < threshold

def is_high_flag(df, i):
    if i < 20:
        return False
    recent = df['Close'].iloc[i-10:i]
    max_close = df['Close'].iloc[:i].max()
    return recent.mean() > 0.9 * max_close and is_uptrend(df, i)

def is_ascending_triangle(df, i):
    if i < 20:
        return False
    highs = df['High'].iloc[i-10:i].rolling(5).max()
    lows = df['Low'].iloc[i-10:i].rolling(5).min()
    resistance = highs.max()
    try:
        slope = np.polyfit(range(10), lows[-10:].values, 1)[0]
        return slope > 0 and abs(highs.iloc[-1] - resistance) / resistance < 0.01
    except:
        return False

def extract_feature_row(df, i):
    return {
        'close': df['Close'].iloc[i],
        'above_50dma': int(df['Close'].iloc[i] > df['50DMA'].iloc[i]),
        'above_100dma': int(df['Close'].iloc[i] > df['100DMA'].iloc[i]),
        'above_200dma': int(df['Close'].iloc[i] > df['200DMA'].iloc[i]),
        'is_uptrend': int(is_uptrend(df, i)),
        'is_consolidating': int(is_consolidating(df, i)),
        'is_high_flag': int(is_high_flag(df, i)),
        'is_ascending_triangle': int(is_ascending_triangle(df, i)),
    }

# Luo opetusdata yhdelle osakkeelle
def create_training_data_for_ticker(ticker, holding_days=21):
    try:
        df = yf.download(ticker, period="10y", interval="1d")
        df.dropna(inplace=True)
        df = add_indicators(df)

        data = []
        for i in range(250, len(df) - holding_days):
            features = extract_feature_row(df, i)
            future_return = (df['Close'].iloc[i + holding_days] - df['Close'].iloc[i]) / df['Close'].iloc[i]
            label = int(future_return > 0.05)  # nousiko yli 5 %
            features['target'] = label
            features['future_return'] = round(future_return, 4)
            features['date'] = df.index[i]
            features['ticker'] = ticker
            data.append(features)

        return pd.DataFrame(data)
    except Exception as e:
        print(f"Virhe {ticker}: {e}")
        return pd.DataFrame()

# Pääajelu usealla tickerillä
def generate_dataset(tickers, holding_days=21):
    all_data = []
    for ticker in tqdm(tickers):
        df = create_training_data_for_ticker(ticker, holding_days)
        if not df.empty:
            all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data)
        final_df.to_csv(f"training_data_{holding_days}d.csv", index=False)
        print(f"Tallennettu {len(final_df)} riviä tiedostoon.")
    else:
        print("Ei dataa tallennettavaksi.")

# Esimerkki ajosta
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOG", "NVDA", "AMD"]
    generate_dataset(tickers, holding_days=21)

import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import os

DB_PATH = "signals.db"

# ▶⃣ Lue signaalit tietokannasta
def load_signals():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()  # Palautetaan tyhjä DataFrame jos tietokantaa ei ole
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM signals", conn)
        conn.close()
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values(by="date", ascending=False)
    except Exception as e:
        st.error(f"Virhe ladattaessa tietokantaa: {e}")
        return pd.DataFrame()

# ▶⃣ Luo signaalikuvaus
def get_signal_tags(row):
    tags = []
    if row['is_uptrend']: tags.append("Uptrend")
    if row['is_consolidating']: tags.append("Consolidation")
    if row['is_high_flag']: tags.append("High Flag")
    if row['is_ascending_triangle']: tags.append("Asc. Triangle")
    return ", ".join(tags)

# ▶⃣ Streamlit-sovellus
def main():
    st.title("Osakesignaalit – Mallin perusteella")

    df = load_signals()

    if df.empty:
        st.info("Ei signaaleja tietokannassa. Aja ensin run_all.py luodaksesi signaaleja.")
        return

    df["Signals"] = df.apply(get_signal_tags, axis=1)
    df["Probability %"] = (df["probability"] * 100).round(2)
    df["Expected Return %"] = (df["expected_return"] * 100).round(2)

    st.sidebar.header("Suodatus")
    tickers = st.sidebar.multiselect("Valitse tickerit", sorted(df['ticker'].unique()), default=None)
    min_prob = st.sidebar.slider("Minimitodennäköisyys", 0.5, 1.0, 0.9)
    start_date = st.sidebar.date_input("Alkupäivä", df['date'].min())

    st.sidebar.header("Pattern-suodatus")
    filter_triangle = st.sidebar.checkbox("Ascending Triangle", value=False)
    filter_high_flag = st.sidebar.checkbox("High Flag", value=False)
    filter_moving_avg = st.sidebar.checkbox("Hinta yli 200DMA", value=False)

    filtered = df.copy()
    if tickers:
        filtered = filtered[filtered['ticker'].isin(tickers)]
    filtered = filtered[filtered['probability'] >= min_prob]
    filtered = filtered[filtered['date'] >= pd.to_datetime(start_date)]

    if filter_triangle:
        filtered = filtered[filtered['is_ascending_triangle'] == 1]
    if filter_high_flag:
        filtered = filtered[filtered['is_high_flag'] == 1]
    if filter_moving_avg:
        filtered = filtered[filtered['above_200dma'] == 1]

    st.subheader("Suodatetut signaalit")
    display_cols = ["date", "ticker", "close", "Probability %", "Expected Return %", "Signals"]
    st.dataframe(filtered[display_cols].reset_index(drop=True))

    if not filtered.empty:
        st.subheader("Signaalien määrä ajan mukaan")
        chart_data = filtered.groupby('date').size().reset_index(name='count')
        chart = alt.Chart(chart_data).mark_bar().encode(
            x='date:T',
            y='count:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()

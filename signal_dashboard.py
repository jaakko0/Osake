import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import os

DB_PATH = "signals.db"

def load_signals():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM signals", conn)
        conn.close()
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values(by="date", ascending=False)
    except Exception as e:
        st.error(f"Virhe ladattaessa tietokantaa: {e}")
        return pd.DataFrame()

def get_signal_tags(row):
    tags = []
    if row['is_uptrend']: tags.append("Uptrend")
    if row['is_consolidating']: tags.append("Consolidation")
    if row['is_high_flag']: tags.append("High Flag")
    if row['is_ascending_triangle']: tags.append("Asc. Triangle")
    return ", ".join(tags)

def main():
    st.title("Osakesignaalit – Aktiiviset mahdollisuudet")

    df = load_signals()

    if df.empty:
        st.info("Ei aktiivisia signaaleja. Aja run_all.py luodaksesi uusia.")
        return

    df["Signals"] = df.apply(get_signal_tags, axis=1)
    df["Probability %"] = (df["probability"] * 100).round(2)
    df["Expected Return %"] = (df["expected_return"] * 100).round(2)

    st.sidebar.header("Näytä osakkeet joissa:")
    filter_triangle = st.sidebar.checkbox("Ascending Triangle", value=True)
    filter_high_flag = st.sidebar.checkbox("High Flag", value=True)
    filter_moving_avg = st.sidebar.checkbox("Hinta yli 200DMA", value=True)

    filtered = df.copy()

    # Näytetään vain ne rivit joissa vähintään yksi valituista täyttyy
    conditions = []
    if filter_triangle:
        conditions.append(filtered['is_ascending_triangle'] == 1)
    if filter_high_flag:
        conditions.append(filtered['is_high_flag'] == 1)
    if filter_moving_avg:
        conditions.append(filtered['above_200dma'] == 1)

    if conditions:
        combined = conditions[0]
        for cond in conditions[1:]:
            combined |= cond
        filtered = filtered[combined]
    else:
        filtered = filtered.iloc[0:0]  # Tyhjä DataFrame jos mikään filtteri ei valittuna

    st.subheader("Aktiiviset osakkeet joissa signaali on täyttynyt")
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

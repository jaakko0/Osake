import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

DB_PATH = "signals.db"

# ▶⃣ Lue signaalit tietokannasta
def load_signals():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM signals", conn)
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values(by="date", ascending=False)

# ▶⃣ Streamlit-sovellus
def main():
    st.title("Osakesignaalit – Mallin perusteella")

    df = load_signals()

    if df.empty:
        st.warning("Ei signaaleja tietokannassa.")
        return

    tickers = st.multiselect("Valitse tickerit", sorted(df['ticker'].unique()), default=None)
    min_prob = st.slider("Minimitodennäköisyys", 0.5, 1.0, 0.9)
    start_date = st.date_input("Alkupäivä", df['date'].min())

    filtered = df.copy()
    if tickers:
        filtered = filtered[filtered['ticker'].isin(tickers)]
    filtered = filtered[filtered['probability'] >= min_prob]
    filtered = filtered[filtered['date'] >= pd.to_datetime(start_date)]

    st.subheader("\ud83d\udd0d Suodatetut signaalit")
    st.dataframe(filtered.reset_index(drop=True))

    st.subheader("\ud83d\udcca Signaalien määrä ajan mukaan")
    chart_data = filtered.groupby('date').size().reset_index(name='count')
    chart = alt.Chart(chart_data).mark_bar().encode(
        x='date:T',
        y='count:Q'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()

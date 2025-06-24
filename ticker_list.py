import pandas as pd

def get_sp500_tickers():
    try:
        sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        tickers = sp500["Symbol"].tolist()
        tickers = [t.replace('.', '-') for t in tickers]  # yfinance käyttää "-" pisteen sijaan
        return tickers
    except Exception as e:
        print(f"Virhe haettaessa S&P500 listaa: {e}")
        return []

def get_helsinki_tickers():
    return [
        "NOKIA.HE", "KNEBV.HE", "FORTUM.HE", "UPM.HE",
        "OUT1V.HE", "ELISA.HE", "NESTE.HE", "KESKOB.HE",
        "WRT1V.HE", "STERV.HE", "ORNBV.HE", "METSO.HE"
    ]

def generate_ticker_list():
    sp500 = get_sp500_tickers()
    helsinki = get_helsinki_tickers()
    combined = sp500 + helsinki

    with open("all_tickers.txt", "w") as f:
        for t in combined:
            f.write(t + "\n")

    print(f"Tallennettu {len(combined)} tikkeriä tiedostoon all_tickers.txt")

if __name__ == "__main__":
    generate_ticker_list()

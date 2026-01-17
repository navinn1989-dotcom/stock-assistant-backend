from fastapi import FastAPI, Query
from datetime import datetime
import yfinance as yf
import pandas as pd

app = FastAPI()

# --- STRATEGY ---
def generate_signal(df: pd.DataFrame):
    df["SMA5"] = df["Close"].rolling(5).mean()
    df["SMA10"] = df["Close"].rolling(10).mean()

    if df["SMA5"].iloc[-1] > df["SMA10"].iloc[-1]:
        return "BUY"
    elif df["SMA5"].iloc[-1] < df["SMA10"].iloc[-1]:
        return "SELL"
    return "HOLD"

# --- NSE SYMBOL MAP ---
NSE_MAP = {
    "TCS": "TCS.NS",
    "RELIANCE": "RELIANCE.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
}

@app.get("/stock")
def get_stock(symbol: str = Query("TCS")):
    yf_symbol = NSE_MAP.get(symbol.upper())

    if not yf_symbol:
        return {"error": "Invalid symbol"}

    data = yf.download(
        yf_symbol,
        period="1d",
        interval="5m",
        progress=False,
    )

    if data.empty or len(data) < 10:
        return {"error": "Insufficient market data"}

    price = round(float(data["Close"].iloc[-1]), 2)
    signal = generate_signal(data)

    return {
        "symbol": symbol,
        "price": price,
        "signal": signal,
        "time": datetime.now().strftime("%H:%M:%S"),
    }

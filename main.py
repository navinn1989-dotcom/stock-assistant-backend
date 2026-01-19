from fastapi import FastAPI, Query
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

def calculate_rsi(close, period=14):
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # ✅ SAFETY CHECK
    if rsi.dropna().empty:
        return None

    return round(float(rsi.dropna().iloc[-1]), 2)

@app.get("/stock")
def get_stock(symbol: str = Query("TCS")):
    try:
        yf_symbol = symbol.upper() + ".NS"

        df = yf.download(
            yf_symbol,
            period="1mo",
            interval="5m",
            progress=False
        )

        # ✅ SAFE EMPTY CHECK
        if df is None or df.empty:
            return {"error": "Invalid symbol"}

        close = df["Close"].dropna()

        if close.empty:
            return {"error": "No price data"}

        price = round(float(close.iloc[-1]), 2)

        ma20_series = close.rolling(20).mean().dropna()
        ma20 = round(float(ma20_series.iloc[-1]), 2) if not ma20_series.empty else None

        rsi = calculate_rsi(close)

        if rsi is None or ma20 is None:
            signal = "HOLD"
        elif rsi < 30 and price > ma20:
            signal = "BUY"
        elif rsi > 70 and price < ma20:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {
            "symbol": symbol.upper(),
            "price": price,
            "rsi": rsi,
            "ma20": ma20,
            "signal": signal,
            "time": datetime.now().strftime("%H:%M:%S")
        }

    except Exception as e:
        return {"error": str(e)}

import yfinance as yf
from datetime import datetime

# 🧱 Lista oficial de commodities/metales verificados en Yahoo Finance
TICKERS = {
    # --- Metales ---
    "ALUMINUM": "ALI=F",     # Aluminum Futures
    "IRON": "TIO=F",         # Iron Ore 62% Fe, CFR China
    "COPPER": "HG=F",        # High-Grade Copper Futures
    "GOLD": "GC=F",          # Gold Futures
    "SILVER": "SI=F",        # Silver Futures

    # --- Materiales de construcción ---
    "LUMBER": "LBR=F",       # Lumber Futures
    "PVC": "PVC-USD",        # PVC/USD (valor de referencia)
}

# 💱 Divisas (para futuras conversiones)
CURRENCIES = {
    "USD/MXN": "MXN=X",
    "USD/EUR": "EUR=X",
    "USD/JPY": "JPY=X",
}


def get_yfinance_prices(symbols=None):
    """
    Obtiene precios actualizados de metales y commodities desde Yahoo Finance.
    Si el mercado está cerrado, devuelve el último precio histórico disponible (1 mes).
    """
    if symbols is None:
        symbols = TICKERS.keys()

    prices = {}
    for name in symbols:
        ticker = TICKERS.get(name)
        try:
            data = yf.Ticker(ticker).history(period="1mo")
            if data.empty:
                print(f"❌ {name} ({ticker}) → sin datos disponibles.")
                continue
            last_close = data["Close"].dropna().iloc[-1]
            prices[name] = round(float(last_close), 4)
            print(f"✅ {name} ({ticker}) → {last_close:.4f} USD (último cierre disponible)")
        except Exception as e:
            print(f"⚠️ Error al obtener {name} ({ticker}): {e}")

    return prices


def get_currency_rates(symbols=None):
    """
    Obtiene tasas de cambio de divisas desde Yahoo Finance.
    """
    if symbols is None:
        symbols = CURRENCIES.keys()

    rates = {}
    for name in symbols:
        ticker = CURRENCIES[name]
        try:
            data = yf.Ticker(ticker).history(period="1mo")
            if data.empty:
                print(f"❌ {name} ({ticker}) → sin datos disponibles.")
                continue
            rate = data["Close"].dropna().iloc[-1]
            rates[name] = round(float(rate), 4)
            print(f"✅ {name} ({ticker}) → {rate:.4f}")
        except Exception as e:
            print(f"⚠️ Error al obtener tasa {name} ({ticker}): {e}")

    return rates

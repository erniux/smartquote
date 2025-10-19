import yfinance as yf
from datetime import datetime

# 🧱 Lista oficial de commodities/metales verificados en Yahoo Finance
TICKERS = {
    "GOLD": "GC=F",        # Oro (onza troy)
    "SILVER": "SI=F",      # Plata (onza troy)
    "COPPER": "HG=F",      # Cobre (libra)
    "ALUMINUM": "ALI=F",   # Aluminio (tonelada)
    "IRON": "TIO=F",       # Mineral de hierro (tonelada)
    "LUMBER": "LBR=F",     # Madera (mil pies tablares)
    "OIL": "CL=F",         # 🛢️ Crude Oil (Petróleo, USD/barril)
    "GAS": "NG=F",         # 🔥 Natural Gas (USD/MMBtu)
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

import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Seiten-Konfiguration (Scanner-Optik)
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

st.title("🖥️ RESTOR Trading Terminal")
st.markdown("**Regelwerk:** 4h-Chart | Sektor-Rotation | v6.1 & v7.1 | 0,5 % Risiko pro Trade")
st.markdown("---")

# 2. RESTOR Daten-Engine (Live von Yahoo Finance)
@st.cache_data(ttl=3600)
def fetch_restor_data():
    tickers = ["XLK", "XLF", "XLC", "XLY", "XLV", "XLI", "XLP", "XLE", "XLB", "XLRE", "XLU"]
    data = yf.download(tickers, period="200d", progress=False)['Close']
    
    results = []
    green_count = 0
    
    for ticker in tickers:
        current_price = data[ticker].iloc[-1]
        sma_130 = data[ticker].rolling(window=130).mean().iloc[-1]
        rsl = 0 if pd.isna(sma_130) or sma_130 == 0 else current_price / sma_130
        
        # Ampel und Klarwerte
        if rsl >= 1.010:
            status = "🟢 Long-Freigabe"
            green_count += 1
        elif rsl <= 0.989:
            status = "🔴 Short-Fokus"
        else:
            status = "🟡 Neutral (Pause)"
            
        results.append({
            "Sektor ETF": ticker, 
            "Kurs ($)": round(current_price, 2),
            "SMA 130": round(sma_130, 2),
            "RSL (RESTOR)": round(rsl, 3), 
            "Signal": status
        })
        
    return pd.DataFrame(results).sort_values(by="RSL (RESTOR)", ascending=False), green_count

with st.spinner("Lade Sektor-Daten..."):
    df_sectors, green_count = fetch_restor_data()

# 3. Das Dashboard (Metriken)
col1, col2, col3 = st.columns(3)
col1.metric("Marktbreite (Grün)", f"{green_count} / 11")
col2.metric("Stärkster Sektor", df_sectors.iloc[0]["Sektor ETF"], str(df_sectors.iloc[0]["RSL (RESTOR)"]))
col3.metric("Schwächster Sektor", df_sectors.iloc[-1]["Sektor ETF"], str(df_sectors.iloc[-1]["RSL (RESTOR)"]))

st.markdown("### 📊 Live Sektor-Matrix (RESTOR)")

# Tabelle mit Farb-Logik
def color_signals(val):
    if '🟢' in str(val):
        return 'background-color: rgba(0, 255, 0, 0.1)'
    elif '🔴' in str(val):
        return 'background-color: rgba(255, 0, 0, 0.1)'
    elif '🟡' in str(val):
        return 'background-color: rgba(255, 255, 0, 0.1)'
    return ''

st.dataframe(
    df_sectors.style.applymap(color_signals, subset=['Signal']),
    use_container_width=True
)

if st.button("🔄 Live-Daten jetzt aktualisieren"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# 4. Makro-Indikatoren Dashboard (Auf der selben Seite)
st.markdown("### 🌍 10 Kern-Indikatoren (Makro-Wetter)")
st.markdown("*Statische Übersicht für den Gesamtmarkt. Fokus liegt immer auf der Sektor-Auswertung oben.*")

macro_data = [
    {"Indikator": "VIX", "Wert": "14.50", "Signal": "🟡 Neutral"},
    {"Indikator": "RSI (14-Tage)", "Wert": "48.2", "Signal": "🟡 Neutral"},
    {"Indikator": "Put/Call Ratio", "Wert": "0.95", "Signal": "🟡 Neutral"},
    {"Indikator": "AAII Sentiment", "Wert": "38% Bull", "Signal": "🟡 Neutral"},
    {"Indikator": "P/E Ratio (trailing)", "Wert": "24.1", "Signal": "🔴 Bärisch"},
    {"Indikator": "MACD Histogram", "Wert": "-0.15", "Signal": "🔴 Bärisch"},
    {"Indikator": "On-Balance Volume", "Wert": "Fallend", "Signal": "🔴 Bärisch"},
    {"Indikator": "Credit Spreads", "Wert": "1.15%", "Signal": "🟢 Bullisch"},
    {"Indikator": "Advance-Decline Line", "Wert": "Seitwärts", "Signal": "🟡 Neutral"},
    {"Indikator": "CNN Fear & Greed", "Wert": "45", "Signal": "🟡 Neutral"}
]

df_macro = pd.DataFrame(macro_data)
st.dataframe(
    df_macro.style.applymap(color_signals, subset=['Signal']),
    use_container_width=True
)
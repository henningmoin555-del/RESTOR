import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Seiten-Konfiguration (Scanner-Optik)
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

st.title("🖥️ RESTOR Trading Terminal")
st.markdown("**Regelwerk:** 4h-Chart | v6.1 & v7.1 Setups | 0,5 % Risiko pro Trade")

with st.expander("📖 Wie deute ich diese App? (Die RESTOR-Logik)"):
    st.markdown('''
    Dieses Terminal filtert den institutionellen Kapitalfluss, indem es die **Relative Stärke (RSL)** der 11 US-Kernsektoren misst. 
    Dafür wird der aktuelle Kurs durch den gleitenden Durchschnitt der letzten 130 Tage (SMA 130) geteilt.
    
    * 🟢 **Long-Freigabe (RSL >= 1.010):** Der Sektor notiert stabil (> 1 %) über dem Durchschnitt. Das Momentum ist bullisch. **Aktion:** Im 4h-Chart nach Long-Mustern suchen.
    * 🔴 **Short-Fokus (RSL <= 0.989):** Der Sektor notiert signifikant unter dem Durchschnitt. Echter Verkaufsdruck. **Aktion:** Im 4h-Chart nach Short-Setups suchen.
    * 🟡 **Neutral / Pause (RSL 0.990 - 1.009):** Die "Todeszone" direkt am Durchschnitt. Kein klarer Trend. **Aktion:** Sektor komplett ignorieren, Kapital schützen.
    ''')

st.markdown("---")

# 2. RESTOR & Makro Daten-Engine (Live von Yahoo Finance)
@st.cache_data(ttl=3600)
def fetch_all_data():
    sector_map = {
        "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
        "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
        "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
        "XLRE": "Immobilien", "XLU": "Versorger"
    }
    
    # Sektoren + S&P 500 Index (^GSPC) + Volatilitätsindex (^VIX) laden
    all_tickers = list(sector_map.keys()) + ["^GSPC", "^VIX"]
    data = yf.download(all_tickers, period="200d", progress=False)['Close']
    
    # A. Sektoren-Berechnung
    sector_results = []
    green_count = 0
    
    for ticker in sector_map.keys():
        current_price = data[ticker].iloc[-1]
        sma_130 = data[ticker].rolling(window=130).mean().iloc[-1]
        rsl = 0.0 if pd.isna(sma_130) or sma_130 == 0 else current_price / sma_130
        
        if rsl >= 1.010:
            status = "🟢 Long-Freigabe"
            green_count += 1
        elif rsl <= 0.989:
            status = "🔴 Short-Fokus"
        else:
            status = "🟡 Neutral (Pause)"
            
        sector_results.append({
            "Sektor ETF": f"{ticker} ({sector_map[ticker]})", 
            "Kurs ($)": current_price,
            "SMA 130": sma_130,
            "RSL (RESTOR)": rsl, 
            "Signal": status
        })
        
    df_sectors = pd.DataFrame(sector_results).sort_values(by="RSL (RESTOR)", ascending=False)
    
    # B. Automatische Makro-Indikatoren berechnen
    # VIX
    vix_val = data["^VIX"].iloc[-1]
    vix_signal = "🟢 Bullisch" if vix_val < 20 else "🔴 Bärisch"
    
    # S&P 500 RSI (14)
    delta = data["^GSPC"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    rsi_series = 100 - (100 / (1 + rs))
    rsi_val = rsi_series.iloc[-1]
    rsi_signal = "🔴 Überkauft" if rsi_val > 70 else ("🟢 Überverkauft" if rsi_val < 30 else "🟡 Neutral")
    
    # S&P 500 MACD Histogram
    exp1 = data["^GSPC"].ewm(span=12, adjust=False).mean()
    exp2 = data["^GSPC"].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    hist_val = (macd - signal_line).iloc[-1]
    macd_signal = "🟢 Bullisch" if hist_val > 0 else "🔴 Bärisch"
    
    macro_list = [
        {"Indikator": "VIX", "Aktueller Wert": vix_val, "Signal": vix_signal, "Typ": "Automatisch"},
        {"Indikator": "RSI (14-Tage)", "Aktueller Wert": rsi_val, "Signal": rsi_signal, "Typ": "Automatisch"},
        {"Indikator": "MACD Histogram", "Aktueller Wert": hist_val, "Signal": macd_signal, "Typ": "Automatisch"},
        # Händische Werte (Basiswerte dienen als editierbare Platzhalter im Code)
        {"Indikator": "Put/Call Ratio (CBOE)", "Aktueller Wert": 0.950, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "AAII Sentiment Survey", "Aktueller Wert": 38.000, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "P/E Ratio (trailing)", "Aktueller Wert": 24.100, "Signal": "🔴 Bärisch", "Typ": "Händisch"},
        {"Indikator": "On-Balance Volume (OBV)", "Aktueller Wert": 0.000, "Signal": "🔴 Bärisch", "Typ": "Händisch"},
        {"Indikator": "Credit Spreads (BBB vs 10Y)", "Aktueller Wert": 1.150, "Signal": "🟢 Bullisch", "Typ": "Händisch"},
        {"Indikator": "Advance-Decline Line", "Aktueller Wert": 0.000, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "CNN Fear & Greed Index", "Aktueller Wert": 45.000, "Signal": "🟡 Neutral", "Typ": "Händisch"}
    ]
    df_macro = pd.DataFrame(macro_list)
    
    return df_sectors, green_count, df_macro

with st.spinner("Aktualisiere Terminal-Daten..."):
    df_sectors, green_count, df_macro = fetch_all_data()

# 3. Das Dashboard (Metriken)
col1, col2, col3 = st.columns(3)
col1.metric("Marktbreite (Grün)", f"{green_count} / 11")
col2.metric("Stärkster Sektor", df_sectors.iloc[0]["Sektor ETF"], f"{df_sectors.iloc[0]['RSL (RESTOR)']:.3f}")
col3.metric("Schwächster Sektor", df_sectors.iloc[-1]["Sektor ETF"], f"{df_sectors.iloc[-1]['RSL (RESTOR)']:.3f}")

st.markdown("### 📊 Live Sektor-Matrix (RESTOR)")

# Farb-Logik für Sektoren
def color_signals(val):
    if '🟢' in str(val): return 'background-color: rgba(0, 255, 0, 0.1)'
    elif '🔴' in str(val): return 'background-color: rgba(255, 0, 0, 0.1)'
    elif '🟡' in str(val): return 'background-color: rgba(255, 255, 0, 0.1)'
    return ''

st.dataframe(
    df_sectors.style.map(color_signals, subset=['Signal']).format({
        "Kurs ($)": "{:.3f}", "SMA 130": "{:.3f}", "RSL (RESTOR)": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

if st.button("🔄 Live-Daten jetzt aktualisieren"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# 4. Makro-Indikatoren Dashboard mit Zeilen-Styling (Händisch = Grau)
st.markdown("### 🌍 10 Kern-Indikatoren (Makro-Wetter)")
st.markdown("*Grau hinterlegte Zeilen müssen bei Bedarf händisch im Code angepasst werden. Farbige Zeilen laufen vollautomatisch.*")

def style_macro_rows(row):
    if row['Typ'] == 'Händisch':
        return ['background-color: rgba(128, 128, 128, 0.2); color: #999999; font-style: italic'] * len(row)
    else:
        if '🟢' in str(row['Signal']): return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row)
        elif '🔴' in str(row['Signal']): return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)
        else: return ['background-color: rgba(255, 255, 0, 0.1)'] * len(row)

st.dataframe(
    df_macro.style.apply(style_macro_rows, axis=1).format({
        "Aktueller Wert": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

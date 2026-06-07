import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. Seiten-Konfiguration
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

st.title("🖥️ RESTOR Trading Terminal")
st.markdown("**Regelwerk:** 4h-Chart | v6.1 & v7.1 Setups | 0,5 % Risiko pro Trade")

with st.expander("📖 Wie deute ich diese App? (Die RESTOR-Logik)"):
    st.markdown('''
    Dieses Terminal filtert den institutionellen Kapitalfluss, indem es die **Relative Stärke (RSL)** misst. 
    Dafür wird der aktuelle Kurs durch den gleitenden Durchschnitt der letzten 130 Tage (SMA 130) geteilt.
    
    * 🟢 **Long-Freigabe (RSL >= 1.010):** Der Sektor notiert stabil (> 1 %) über dem Durchschnitt. Das Momentum ist bullisch. **Aktion:** Im 4h-Chart nach Long-Mustern suchen.
    * 🔴 **Short-Fokus (RSL <= 0.989):** Der Sektor notiert signifikant unter dem Durchschnitt. Echter Verkaufsdruck. **Aktion:** Im 4h-Chart nach Short-Setups suchen.
    * 🟡 **Neutral / Pause (RSL 0.990 - 1.009):** Die "Todeszone" direkt am Durchschnitt. Kein klarer Trend. **Aktion:** Sektor komplett ignorieren, Kapital schützen.
    ''')

st.markdown("---")

# 2. RESTOR Daten-Engine (Live von Yahoo Finance)
@st.cache_data(ttl=3600)
def fetch_all_data():
    sector_map_us = {
        "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
        "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
        "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
        "XLRE": "Immobilien", "XLU": "Versorger"
    }
    
    # Offizielle iShares Euro Stoxx 600 Sektor-ETFs (Xetra-Kürzel)
    sector_map_eu = {
        "EXV3.DE": "Technologie", "EXV1.DE": "Banken", "EXV2.DE": "Telekommunikation", 
        "EXV6.DE": "Automobile & Teile", "EXV4.DE": "Gesundheit", "EXV9.DE": "Industrie", 
        "EXV8.DE": "Nahrungsmittel", "EXVC.DE": "Energie", "EXVK.DE": "Grundstoffe", 
        "EXVE.DE": "Immobilien", "EXVG.DE": "Versorger"
    }
    
    all_tickers = list(sector_map_us.keys()) + list(sector_map_eu.keys()) + ["^GSPC", "^VIX"]
    data = yf.download(all_tickers, period="200d", progress=False)['Close']
    
    def process_sectors(sector_map):
        results = []
        green = 0
        for ticker, name in sector_map.items():
            if ticker not in data.columns:
                continue
                
            # WICHTIG: .dropna() filtert Feiertage und leere Felder sofort heraus!
            ticker_data = data[ticker].dropna()
            
            if len(ticker_data) < 130:
                continue
                
            current_price = ticker_data.iloc[-1]
            sma_130 = ticker_data.rolling(window=130).mean().iloc[-1]
            rsl = 0.0 if pd.isna(sma_130) or sma_130 == 0 else current_price / sma_130
            
            if rsl >= 1.010:
                status = "🟢 Long-Freigabe"
                green += 1
            elif rsl <= 0.989:
                status = "🔴 Short-Fokus"
            else:
                status = "🟡 Neutral (Pause)"
                
            results.append({
                "Sektor ETF": f"{ticker} ({name})", 
                "Kurs": current_price,
                "SMA 130": sma_130,
                "RSL (RESTOR)": rsl, 
                "Signal": status
            })
            
        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="RSL (RESTOR)", ascending=False)
        return df, green
        
    df_us, green_us = process_sectors(sector_map_us)
    df_eu, green_eu = process_sectors(sector_map_eu)
    
    # Makro-Indikatoren
    sp500_data = data["^GSPC"].dropna()
    vix_data = data["^VIX"].dropna()
    
    # VIX
    vix_val = vix_data.iloc[-1] if not vix_data.empty else 0
    vix_signal = "🟢 Bullisch" if vix_val < 20 else "🔴 Bärisch"
    
    # RSI (14)
    if len(sp500_data) > 14:
        delta = sp500_data.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        rsi_series = 100 - (100 / (1 + rs))
        rsi_val = rsi_series.iloc[-1]
    else:
        rsi_val = 50.0
    rsi_signal = "🔴 Überkauft" if rsi_val > 70 else ("🟢 Überverkauft" if rsi_val < 30 else "🟡 Neutral")
    
    # MACD Histogram
    if len(sp500_data) > 26:
        exp1 = sp500_data.ewm(span=12, adjust=False).mean()
        exp2 = sp500_data.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        hist_val = (macd - signal_line).iloc[-1]
    else:
        hist_val = 0.0
    macd_signal = "🟢 Bullisch" if hist_val > 0 else "🔴 Bärisch"
    
    macro_list = [
        {"Indikator": "VIX", "Aktueller Wert": vix_val, "Signal": vix_signal, "Typ": "Automatisch"},
        {"Indikator": "RSI (14-Tage)", "Aktueller Wert": rsi_val, "Signal": rsi_signal, "Typ": "Automatisch"},
        {"Indikator": "MACD Histogram", "Aktueller Wert": hist_val, "Signal": macd_signal, "Typ": "Automatisch"},
        {"Indikator": "Put/Call Ratio (CBOE)", "Aktueller Wert": 0.950, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "AAII Sentiment Survey", "Aktueller Wert": 38.000, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "P/E Ratio (trailing)", "Aktueller Wert": 24.100, "Signal": "🔴 Bärisch", "Typ": "Händisch"},
        {"Indikator": "On-Balance Volume (OBV)", "Aktueller Wert": 0.000, "Signal": "🔴 Bärisch", "Typ": "Händisch"},
        {"Indikator": "Credit Spreads (BBB vs 10Y)", "Aktueller Wert": 1.150, "Signal": "🟢 Bullisch", "Typ": "Händisch"},
        {"Indikator": "Advance-Decline Line", "Aktueller Wert": 0.000, "Signal": "🟡 Neutral", "Typ": "Händisch"},
        {"Indikator": "CNN Fear & Greed Index", "Aktueller Wert": 45.000, "Signal": "🟡 Neutral", "Typ": "Händisch"}
    ]
    df_macro = pd.DataFrame(macro_list)
    
    return df_us, green_us, df_eu, green_eu, df_macro

with st.spinner("Aktualisiere Terminal-Daten..."):
    df_us, green_us, df_eu, green_eu, df_macro = fetch_all_data()

def color_signals(val):
    if '🟢' in str(val): return 'background-color: rgba(0, 255, 0, 0.1)'
    elif '🔴' in str(val): return 'background-color: rgba(255, 0, 0, 0.1)'
    elif '🟡' in str(val): return 'background-color: rgba(255, 255, 0, 0.1)'
    return ''

st.markdown("### 🇺🇸 RSL - SP500")
col1, col2, col3 = st.columns(3)
col1.metric("Marktbreite (Grün)", f"{green_us} / 11")
if not df_us.empty:
    col2.metric("Stärkster Sektor", df_us.iloc[0]["Sektor ETF"], f"{df_us.iloc[0]['RSL (RESTOR)']:.3f}")
    col3.metric("Schwächster Sektor", df_us.iloc[-1]["Sektor ETF"], f"{df_us.iloc[-1]['RSL (RESTOR)']:.3f}")

st.dataframe(
    df_us.style.map(color_signals, subset=['Signal']).format({
        "Kurs": "{:.3f}", "SMA 130": "{:.3f}", "RSL (RESTOR)": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

st.markdown("### 🇪🇺 RSL - Eurostoxx")
col4, col5, col6 = st.columns(3)
col4.metric("Marktbreite (Grün)", f"{green_eu} / 11")
if not df_eu.empty:
    col5.metric("Stärkster Sektor", df_eu.iloc[0]["Sektor ETF"], f"{df_eu.iloc[0]['RSL (RESTOR)']:.3f}")
    col6.metric("Schwächster Sektor", df_eu.iloc[-1]["Sektor ETF"], f"{df_eu.iloc[-1]['RSL (RESTOR)']:.3f}")

st.dataframe(
    df_eu.style.map(color_signals, subset=['Signal']).format({
        "Kurs": "{:.3f}", "SMA 130": "{:.3f}", "RSL (RESTOR)": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

if st.button("🔄 Live-Daten jetzt aktualisieren"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

st.markdown("### 🌍 10 Kern-Indikatoren (Makro-Wetter)")
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

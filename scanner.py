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
    Dieses Terminal filtert den institutionellen Kapitalfluss durch Messung der **Relative Stärke (RSL)**. 
    Formel: RSL = Aktueller Kurs / SMA 130.
    
    * 🟢 **Long-Freigabe (RSL >= 1.010):** Sektor notiert stabil über dem SMA 130. **Aktion:** Im 4h-Chart nach Long-Mustern suchen.
    * 🔴 **Short-Fokus (RSL <= 0.989):** Sektor notiert signifikant unter dem SMA 130. **Aktion:** Im 4h-Chart nach Short-Setups suchen.
    * 🟡 **Neutral / Pause (RSL 0.990 - 1.009):** Trendlos. **Aktion:** Ignorieren.
    ''')

st.markdown("---")

# 2. RESTOR Daten-Engine
@st.cache_data(ttl=3600)
def fetch_sector_data():
    sector_map_us = {
        "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
        "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
        "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
        "XLRE": "Immobilien", "XLU": "Versorger"
    }
    
    sector_map_eu = {
        "EXV3.DE": "Technologie", "EXV1.DE": "Banken", "EXV2.DE": "Telekommunikation", 
        "EXV6.DE": "Automobile & Teile", "EXV4.DE": "Gesundheit", "EXV9.DE": "Industrie", 
        "EXV8.DE": "Nahrungsmittel", "EXVC.DE": "Energie", "EXVK.DE": "Grundstoffe", 
        "EXVE.DE": "Immobilien", "EXVG.DE": "Versorger"
    }
    
    def process_sectors(sector_map):
        results = []
        green = 0
        for ticker, name in sector_map.items():
            ticker_data = yf.download(ticker, period="200d", progress=False)['Close']
            if ticker_data.empty or len(ticker_data) < 130: continue
                
            current_price = ticker_data.iloc[-1]
            sma_130 = ticker_data.rolling(window=130).mean().iloc[-1]
            rsl = 0.0 if pd.isna(sma_130) or sma_130 == 0 else current_price / sma_130
            
            status = "🟢 Long" if rsl >= 1.010 else ("🔴 Short" if rsl <= 0.989 else "🟡 Neutral")
            if rsl >= 1.010: green += 1
                
            results.append({
                "Sektor": f"{ticker} ({name})", 
                "Kurs": current_price,
                "SMA 130": sma_130,
                "RSL": rsl, 
                "Signal": status
            })
        df = pd.DataFrame(results)
        return df.sort_values(by="RSL", ascending=False), green
        
    df_us, green_us = process_sectors(sector_map_us)
    df_eu, green_eu = process_sectors(sector_map_eu)
    return df_us, green_us, df_eu, green_eu

with st.spinner("Aktualisiere Sektor-Matrix..."):
    df_us, green_us, df_eu, green_eu = fetch_sector_data()

def color_signals(val):
    if '🟢' in str(val): return 'background-color: rgba(0, 255, 0, 0.1)'
    elif '🔴' in str(val): return 'background-color: rgba(255, 0, 0, 0.1)'
    elif '🟡' in str(val): return 'background-color: rgba(255, 255, 0, 0.1)'
    return ''

st.markdown("### 🇺🇸 RSL - SP500")
st.metric("Marktbreite (Grün)", f"{green_us} / 11")
st.dataframe(
    df_us.style.map(color_signals, subset=['Signal']).format({
        "Kurs": "{:.3f}", "SMA 130": "{:.3f}", "RSL": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

st.markdown("### 🇪🇺 RSL - Eurostoxx")
st.metric("Marktbreite (Grün)", f"{green_eu} / 11")
st.dataframe(
    df_eu.style.map(color_signals, subset=['Signal']).format({
        "Kurs": "{:.3f}", "SMA 130": "{:.3f}", "RSL": "{:.3f}"
    }),
    use_container_width=True, hide_index=True
)

if st.button("🔄 Live-Daten aktualisieren"):
    st.cache_data.clear()
    st.rerun()

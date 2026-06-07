import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Seiten-Konfiguration
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")
st.title("🖥️ RESTOR Trading Terminal")
st.markdown("**Regelwerk:** 4h-Chart | v6.1 & v7.1 Setups | 0,5 % Risiko pro Trade")

# 2. RESTOR Daten-Engine
@st.cache_data(ttl=3600)
def fetch_sector_data():
    maps = {
        "US": {"XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", "XLY": "Zykl. Konsum", "XLV": "Gesundheit", "XLI": "Industrie", "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", "XLRE": "Immobilien", "XLU": "Versorger"},
        "EU": {"EXV3.DE": "Technologie", "EXV1.DE": "Banken", "EXV2.DE": "Telekommunikation", "EXV6.DE": "Automobile", "EXV4.DE": "Gesundheit", "EXV9.DE": "Industrie", "EXV8.DE": "Nahrungsmittel", "EXVC.DE": "Energie", "EXVK.DE": "Grundstoffe", "EXVE.DE": "Immobilien", "EXVG.DE": "Versorger"}
    }
    
    results = {"US": [], "EU": []}
    counts = {"US": 0, "EU": 0}
    
    for region, sector_map in maps.items():
        for ticker, name in sector_map.items():
            try:
                data = yf.download(ticker, period="200d", progress=False)
                if 'Close' not in data.columns or data['Close'].dropna().empty: continue
                
                prices = data['Close'].dropna()
                if len(prices) < 130: continue
                
                curr = float(prices.iloc[-1])
                sma = float(prices.rolling(window=130).mean().iloc[-1])
                rsl = curr / sma if sma != 0 else 0
                
                status = "🟢 Long" if rsl >= 1.010 else ("🔴 Short" if rsl <= 0.989 else "🟡 Neutral")
                if rsl >= 1.010: counts[region] += 1
                
                results[region].append({"Sektor": f"{ticker} ({name})", "Kurs": curr, "SMA 130": sma, "RSL": rsl, "Signal": status})
            except:
                continue
                
    return pd.DataFrame(results["US"]), counts["US"], pd.DataFrame(results["EU"]), counts["EU"]

# App-Daten abrufen
df_us, c_us, df_eu, c_eu = fetch_sector_data()

# 3. Flexible Formatierung (ohne Spalten-Abhängigkeit)
def style_df(df):
    return df.style.map(
        lambda v: 'background-color: rgba(0,255,0,0.1)' if '🟢' in str(v) 
        else ('background-color: rgba(255,0,0,0.1)' if '🔴' in str(v) else ''), 
        subset=df.columns
    ).format({
        "Kurs": "{:.3f}", 
        "SMA 130": "{:.3f}", 
        "RSL": "{:.3f}"
    })

# 4. Anzeige
st.markdown("### 🇺🇸 RSL - SP500")
st.metric("Marktbreite (Grün)", f"{c_us} / 11")
if not df_us.empty:
    st.dataframe(style_df(df_us), use_container_width=True, hide_index=True)

st.markdown("### 🇪🇺 RSL - Eurostoxx")
st.metric("Marktbreite (Grün)", f"{c_eu} / 11")
if not df_eu.empty:
    st.dataframe(style_df(df_eu), use_container_width=True, hide_index=True)

if st.button("🔄 Live-Daten jetzt aktualisieren"):
    st.cache_data.clear()
    st.rerun()

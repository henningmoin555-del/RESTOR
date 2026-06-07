import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")
st.title("🖥️ RESTOR Trading Terminal")

@st.cache_data(ttl=3600)
def fetch_sector_data():
    maps = {
        "US": {"XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", "XLY": "Zykl. Konsum", "XLV": "Gesundheit", "XLI": "Industrie", "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", "XLRE": "Immobilien", "XLU": "Versorger"},
        "EU": {"EXV3.DE": "Technologie", "EXV1.DE": "Banken", "EXV2.DE": "Telekommunikation", "EXV6.DE": "Automobile", "EXV4.DE": "Gesundheit", "EXV9.DE": "Industrie", "EXV8.DE": "Nahrungsmittel", "EXVC.DE": "Energie", "EXVK.DE": "Grundstoffe", "EXVE.DE": "Immobilien", "EXVG.DE": "Versorger"}
    }
    
    data_frames = {}
    green_counts = {}
    
    for region, sector_map in maps.items():
        results = []
        green = 0
        for ticker, name in sector_map.items():
            try:
                df = yf.download(ticker, period="150d", progress=False)
                if not df.empty and 'Close' in df.columns:
                    prices = df['Close'].dropna()
                    if len(prices) >= 130:
                        # Hier die Korrektur: .item() extrahiert den Wert sicher
                        curr = float(prices.iloc[-1].item())
                        sma = float(prices.rolling(window=130).mean().iloc[-1].item())
                        
                        rsl = curr / sma if sma != 0 else 0
                        status = "🟢 Long" if rsl >= 1.010 else ("🔴 Short" if rsl <= 0.989 else "🟡 Neutral")
                        if rsl >= 1.010: green += 1
                        
                        results.append({"Sektor": f"{ticker} ({name})", "Kurs": curr, "SMA 130": sma, "RSL": rsl, "Signal": status})
            except Exception:
                continue
        
        data_frames[region] = pd.DataFrame(results)
        green_counts[region] = green
        
    return data_frames["US"], green_counts["US"], data_frames["EU"], green_counts["EU"]

# Daten abrufen
df_us, c_us, df_eu, c_eu = fetch_sector_data()

def display_table(df, title, count):
    st.markdown(f"### {title}")
    st.metric("Marktbreite (Grün)", f"{count} / 11")
    if not df.empty:
        # Formatierung: Wir stellen sicher, dass alle Spalten numerisch sind
        styled_df = df.style.format({"Kurs": "{:.3f}", "SMA 130": "{:.3f}", "RSL": "{:.3f}"})
        # Einfärben basierend auf dem 'Signal' Text
        styled_df = styled_df.map(lambda v: 'background-color: rgba(0,255,0,0.1)' if '🟢' in str(v) else ('background-color: rgba(255,0,0,0.1)' if '🔴' in str(v) else ''), subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Keine Daten verfügbar. Bitte 'Daten neu laden' klicken.")

display_table(df_us, "🇺🇸 RSL - SP500", c_us)
display_table(df_eu, "🇪🇺 RSL - Eurostoxx", c_eu)

if st.button("🔄 Daten neu laden"):
    st.cache_data.clear()
    st.rerun()

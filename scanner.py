import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

# Dummy-Datenbanken für Einzelaktien (Auszug für Performance-Zwecke - hier deine Watchlists ergänzen)
SP500_STOCKS = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "AMD", "INTC", "CSCO", "QCOM", "TXN", "IBM", "AMAT", "NOW", "INTU"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "SPGI", "GS", "MS", "AXP", "C", "BLK", "CB", "PGR", "MMC"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PXD", "PSX", "VLO", "OXY", "HES", "HAL", "WMB", "BKR", "CTRA"],
    # Weitere Sektoren hier ergänzen...
}

EUROSTOXX_STOCKS = {
    "Technologie": ["ASML.AS", "SAP.DE", "INF.DE", "ASM.AS", "CAP.PA"],
    "Finanzen": ["SAN.MC", "BNP.PA", "ALV.DE", "INGA.AS", "ISP.MI"],
    # Weitere Sektoren hier ergänzen...
}

SECTOR_MAP = {
    "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
    "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
    "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
    "XLRE": "Immobilien", "XLU": "Versorger"
}

# --- Hilfsfunktionen ---
@st.cache_data(ttl=3600)
def fetch_sector_rsl():
    tickers = list(SECTOR_MAP.keys())
    data = yf.download(tickers, period="200d", progress=False)['Close']
    
    results = []
    for ticker in tickers:
        current_price = data[ticker].iloc[-1]
        sma_130 = data[ticker].rolling(window=130).mean().iloc[-1]
        rsl = 0 if pd.isna(sma_130) or sma_130 == 0 else current_price / sma_130
        
        if rsl >= 1.010:
            status = "Long"
        elif rsl <= 0.989:
            status = "Short"
        else:
            status = "Neutral"
            
        results.append({
            "Sektor": ticker,
            "Name": SECTOR_MAP[ticker],
            "RSL": round(rsl, 3),
            "RSL Signal": status
        })
    return pd.DataFrame(results).sort_values(by="RSL", ascending=False)

@st.cache_data(ttl=3600)
def analyze_stocks(tickers, apply_ema_filter):
    if not tickers:
        return pd.DataFrame()
    
    data = yf.download(tickers, period="200d", progress=False)['Close']
    if len(tickers) == 1:
        data = data.to_frame(name=tickers[0])
        
    results = []
    for ticker in tickers:
        if ticker not in data.columns:
            continue
            
        series = data[ticker].dropna()
        if len(series) < 130:
            continue
            
        current_price = series.iloc[-1]
        sma_130 = series.rolling(window=130).mean().iloc[-1]
        rsl = current_price / sma_130 if sma_130 > 0 else 0
        
        if rsl < 1.10:
            continue # Harter Schwellenwert
            
        # EMA Filter Check
        passed_ema = True
        if apply_ema_filter:
            ema5 = series.ewm(span=5, adjust=False).mean()
            ema20 = series.ewm(span=20, adjust=False).mean()
            
            # Prüfen ob EMA5 > EMA20 heute UND EMA5 <= EMA20 vor 3 Tagen (Frisches Signal)
            if len(ema5) >= 4:
                today_bullish = ema5.iloc[-1] > ema20.iloc[-1]
                past_bearish = ema5.iloc[-4] <= ema20.iloc[-4]
                passed_ema = today_bullish and past_bearish
            else:
                passed_ema = False
                
        if passed_ema:
            results.append({
                "Ticker": ticker,
                "Kurs": round(current_price, 2),
                "RSL": round(rsl, 3)
            })
            
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="RSL", ascending=False).head(15)
    return df

def color_match(val):
    if val == "Match 🟢": return 'background-color: rgba(0, 255, 0, 0.2)'
    if val == "Match 🔴": return 'background-color: rgba(255, 0, 0, 0.2)'
    if val == "Mismatch ⚠️": return 'background-color: rgba(255, 165, 0, 0.2)'
    return ''

# --- UI Aufbau ---
st.title("🖥️ RESTOR Trading Terminal (v6.1 & v7.1)")
st.markdown("**Regelwerk:** 4h-Chart Ausführung | 1d-Filterung | 0,5 % Risiko pro Trade")
st.markdown("---")

# SCHRITT 1: Sektor RSL
st.header("Schritt 1: Sektor-RSL Analyse")
df_sectors = fetch_sector_rsl()

col1, col2 = st.columns([2, 1])
with col1:
    st.dataframe(df_sectors, use_container_width=True)

# SCHRITT 2: Screenshot & Abgleich
st.markdown("---")
st.header("Schritt 2: Screenshot-Abgleich")
st.markdown("Lade deinen Screenshot mit den Long/Short-Markierungen hoch und gleiche die Werte ab.")

col_upload, col_match = st.columns([1, 2])

with col_upload:
    uploaded_file = st.file_uploader("Screenshot hochladen (Referenz)", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Dein Referenz-Chart", use_column_width=True)

with col_match:
    st.markdown("**Manuelles Alignment (OCR Bypass für Stabilität)**")
    # Generiere Editor für Abgleich
    match_data = df_sectors.copy()
    match_data['Screenshot Markierung'] = "Neutral" # Default
    
    edited_df = st.data_editor(
        match_data[['Sektor', 'Name', 'RSL Signal', 'Screenshot Markierung']],
        column_config={
            "Screenshot Markierung": st.column_config.SelectboxColumn(
                "Screenshot Markierung",
                help="Wähle die Richtung aus deinem Screenshot",
                options=["Long", "Short", "Neutral"],
                required=True,
            )
        },
        use_container_width=True,
        key="screenshot_editor"
    )

    # Berechne Matches
    conditions = [
        (edited_df['RSL Signal'] == 'Long') & (edited_df['Screenshot Markierung'] == 'Long'),
        (edited_df['RSL Signal'] == 'Short') & (edited_df['Screenshot Markierung'] == 'Short')
    ]
    choices = ['Match 🟢', 'Match 🔴']
    edited_df['Status'] = np.select(conditions, choices, default='Mismatch ⚠️')
    
    st.markdown("### 🚦 Match / Mismatch Auswertung")
    st.dataframe(edited_df.style.map(color_match, subset=['Status']), use_container_width=True)

# SCHRITT 3: Einzelaktien Deep Dive
st.markdown("---")
st.header("Schritt 3: Einzelaktien Deep Dive (RSL > 1.10)")

# Filtere nur Sektoren die ein Long-Match sind
long_matches = edited_df[edited_df['Status'] == 'Match 🟢']['Sektor'].tolist()

if not long_matches:
    st.info("Keine 'Match 🟢' Sektoren gefunden. Suche nach Long/Long Übereinstimmungen für den Deep Dive.")
else:
    st.success(f"Analysiere starke Aktien für bestätigte Long-Sektoren: {', '.join(long_matches)}")
    
    apply_ema = st.checkbox("🔥 Frisches Signal: EMA5 kreuzte EMA20 in den letzten 3 Tagen", value=False)
    
    tab1, tab2 = st.tabs(["🇺🇸 S&P 500 Auswertung", "🇪🇺 EuroStoxx Auswertung"])
    
    all_strong_tickers = []
    
    with tab1:
        for sector in long_matches:
            st.subheader(f"Sektor: {sector} ({SECTOR_MAP[sector]})")
            tickers_to_check = SP500_STOCKS.get(sector, [])
            
            if not tickers_to_check:
                st.warning("Keine Aktien für diesen Sektor in der internen Liste hinterlegt.")
                continue
                
            with st.spinner(f"Scanne {len(tickers_to_check)} Aktien..."):
                df_stocks = analyze_stocks(tickers_to_check, apply_ema)
                
                if df_stocks.empty:
                    st.write("Keine Aktien über RSL 1.10 oder Filterkriterien nicht erfüllt.")
                else:
                    st.dataframe(df_stocks, use_container_width=True)
                    all_strong_tickers.extend(df_stocks['Ticker'].tolist())

    with tab2:
        st.markdown("*Hinweis: EuroStoxx-Sektoren müssen in den Skript-Konstanten noch manuell gemappt werden.*")
        for sector in long_matches:
            sector_name = SECTOR_MAP[sector]
            st.subheader(f"Europa: {sector_name}")
            eu_tickers = EUROSTOXX_STOCKS.get(sector_name, [])
            
            if eu_tickers:
                df_eu = analyze_stocks(eu_tickers, apply_ema)
                if not df_eu.empty:
                    st.dataframe(df_eu, use_container_width=True)
                    all_strong_tickers.extend(df_eu['Ticker'].tolist())
            else:
                st.write("Keine europäische Watchlist für diesen Sektor hinterlegt.")

    # TradingView Export
    st.markdown("---")
    st.subheader("📺 TradingView Export")
    if all_strong_tickers:
        tv_string = ",".join(all_strong_tickers)
        st.code(tv_string, language="text")
        st.caption("Kopiere diese Zeile und füge sie in deine TradingView Watchlist ein (Klick auf das '+' Symbol in TV und strg+v).")
    else:
        st.write("Noch keine starken Aktien für den Export gefunden.")

# --- Quellen & Fußzeile ---
st.markdown("---")
st.markdown("""
**Quellen & Datenbasis:**
* **Kursdaten:** Yahoo Finance (`yfinance` API)
* **Berechnungsgrundlage:** Tagesendkurse (Daily Close). Der SMA130 basiert auf exakt 130 fortlaufenden Handelstagen.
* **Match-Logik:** Exklusiver Fokus auf Sektoren mit bestätigtem Kapitalfluss (RSL) **und** manuell validierter Marktstruktur.
* **Filter:** RSL > 1.10 identifiziert High-Momentum-Werte. Der optionale EMA 5/20 Filter sucht nach kurzfristigen Pullback-Reversals oder frischen Breakouts.
""")

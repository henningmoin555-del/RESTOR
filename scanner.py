import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

# Interne Sektor-Datenbanken für Einzelaktien (Erweitere diese nach Belieben)
SP500_STOCKS = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "AMD", "INTC", "CSCO", "QCOM", "TXN", "IBM", "AMAT", "NOW", "INTU"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "SPGI", "GS", "MS", "AXP", "C", "BLK", "CB", "PGR", "MMC"],
    "XLC": ["META", "GOOGL", "NFLX", "TMUS", "CHTR", "DIS", "EA", "TTWO"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "LOW", "NKE", "SBUX", "TJX", "ORLY"],
    "XLV": ["LLY", "UNH", "JNJ", "ABV", "MRK", "TMO", "ABT", "PFE", "AMGN"],
    "XLI": ["GE", "CAT", "UNP", "HON", "ETN", "WM", "FEDEX", "UPS", "LMT"],
    "XLP": ["PG", "COST", "WMT", "KO", "PEP", "PM", "MO", "CL"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO"],
    "XLB": ["LIN", "APD", "SHW", "FCX", "ECL", "NEM"],
    "XLRE": ["PLD", "AMT", "CCI", "EQIX", "PSA"],
    "XLU": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP"]
}

EUROSTOXX_STOCKS = {
    "Technologie": ["ASML.AS", "SAP.DE", "INF.DE", "ASM.AS", "CAP.PA"],
    "Finanzen": ["SAN.MC", "BNP.PA", "ALV.DE", "INGA.AS", "ISP.MI"],
    "Kommunikation": ["ORAN.PA", "DTE.DE", "VOD.L"],
    "Zyklischer Konsum": ["RMS.PA", "LVMH.PA", "OR.PA", "BMW.DE", "MBG.DE"],
    "Gesundheit": ["SAN.PA", "BAYN.DE", "MRK.DE"],
    "Industrie": ["SIE.DE", "AIR.PA", "DHL.DE", "ALST.PA"],
    "Basiskonsum": ["HEIA.AS", "BN.PA", "ULVR.L"],
    "Energie": ["TTE.PA", "ENI.MI", "REP.MC"],
    "Materialien": ["BAS.DE", "CRH.L"],
    "Immobilien": ["VNA.DE"],
    "Versorger": ["IBE.MC", "ENEL.MI", "RWE.DE"]
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
def analyze_stocks(tickers, apply_ema_filter, rsl_threshold):
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
        
        if rsl < rsl_threshold:
            continue
            
        ema5 = series.ewm(span=5, adjust=False).mean()
        ema20 = series.ewm(span=20, adjust=False).mean()
        
        has_fresh_cross = False
        if len(ema5) >= 4:
            today_bullish = ema5.iloc[-1] > ema20.iloc[-1]
            past_bearish = ema5.iloc[-4] <= ema20.iloc[-4]
            has_fresh_cross = today_bullish and past_bearish
            
        signal_text = "🔥 Frisches Cross" if has_fresh_cross else "-"
        
        if apply_ema_filter and not has_fresh_cross:
            continue
                
        results.append({
            "Ticker": ticker,
            "Kurs ($)": round(current_price, 2),
            "RSL": round(rsl, 3),
            "EMA 5/20 Signal": signal_text
        })
            
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="RSL", ascending=False).head(15)
    return df

def color_match(val):
    if isinstance(val, str):
        if "Match 🟢" in val: return 'background-color: rgba(0, 255, 0, 0.2)'
        if "Match 🔴" in val: return 'background-color: rgba(255, 0, 0, 0.2)'
        if "Mismatch ⚠️" in val: return 'background-color: rgba(255, 165, 0, 0.2)'
    return ''

def display_styled_dataframe(df):
    """Sicheres Einfärben der Tabelle, egal welche Pandas Version installiert ist."""
    if df.empty:
        st.write("Keine Daten vorhanden.")
        return
    try:
        st.dataframe(df.style.map(color_match, subset=['Status']), use_container_width=True)
    except AttributeError:
        st.dataframe(df.style.applymap(color_match, subset=['Status']), use_container_width=True)

# --- UI Aufbau ---
st.title("🖥️ RESTOR Trading Terminal (v6.1 & v7.1)")
st.markdown("**Regelwerk:** 4h-Chart Ausführung | 1d-Filterung | 0,5 % Risiko pro Trade")

# SCHRITT 1: Sektor RSL
st.markdown("---")
st.header("Schritt 1: Sektor-RSL Analyse")
df_sectors = fetch_sector_rsl()
st.dataframe(df_sectors, use_container_width=True)

# SCHRITT 2: Manueller Abgleich
st.markdown("---")
st.header("Schritt 2: Signalvalidierung (Manuell)")
st.markdown("Trage hier die Werte (Long/Short/Neutral) aus deiner Marktstruktur-Tabelle ein.")

match_data = df_sectors.copy()
# Standardwert für das Dropdown
match_data['T-S (Manuell)'] = "Neutral"

col_edit, col_result = st.columns([1, 1.5])

with col_edit:
    st.markdown("**Eingabemaske**")
    edited_df = st.data_editor(
        match_data[['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)']],
        column_config={
            "T-S (Manuell)": st.column_config.SelectboxColumn(
                "T-S (Manuell)",
                options=["Long", "Short", "Neutral"],
                required=True,
            )
        },
        use_container_width=True,
        key="screenshot_editor"
    )

with col_result:
    # Berechne Matches
    conditions = [
        (edited_df['RSL Signal'] == 'Long') & (edited_df['T-S (Manuell)'] == 'Long'),
        (edited_df['RSL Signal'] == 'Short') & (edited_df['T-S (Manuell)'] == 'Short')
    ]
    choices = ['Match 🟢', 'Match 🔴']
    edited_df['Status'] = np.select(conditions, choices, default='Mismatch ⚠️')
    
    df_matches = edited_df[edited_df['Status'].str.contains('Match')]
    df_mismatches = edited_df[edited_df['Status'] == 'Mismatch ⚠️']
    
    st.markdown("### 🎯 Trade-Freigaben (Matches)")
    if not df_matches.empty:
        display_styled_dataframe(df_matches)
    else:
        st.warning("Noch keine perfekten Matches gefunden. Kapital schützen.")
        
    st.markdown("

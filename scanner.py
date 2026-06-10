import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

# Interne Sektor-Datenbanken für Einzelaktien
SP500_AKTIEN = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "AMD", "INTC", "CSCO", "QCOM", "TXN", "IBM", "AMAT", "NOW", "INTU", "ORCL", "PANW", "MU", "LRCX", "KLAC"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "SPGI", "GS", "MS", "AXP", "C", "BLK", "CB", "PGR", "MMC", "SCHW", "CME", "AON", "ICE", "USB"],
    "XLC": ["META", "GOOGL", "NFLX", "TMUS", "CHTR", "DIS", "EA", "TTWO", "CMCSA", "VZ", "T", "WBD", "OMC", "IPG", "LYV", "FOXA", "NWSA"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "LOW", "NKE", "SBUX", "TJX", "ORLY", "BKNG", "MAR", "GM", "F", "CMG", "LVS", "RCL", "HLT", "EBAY", "ROST", "YUM"],
    "XLV": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "PFE", "AMGN", "DHR", "ISRG", "SYK", "BMY", "CVS", "CI", "BSX", "MDT", "EW", "VRTX", "ZTS"],
    "XLI": ["GE", "CAT", "UNP", "HON", "ETN", "WM", "FDX", "UPS", "LMT", "RTX", "BA", "DE", "CSX", "NSC", "GWW", "EMR", "ROP", "PH", "PCAR", "TT"],
    "XLP": ["PG", "COST", "WMT", "KO", "PEP", "PM", "MO", "CL", "TGT", "EL", "KMB", "GIS", "HSY", "KR", "K", "CHD", "SYY", "STZ", "ADM", "MDLZ"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "OXY", "WMB", "KMI", "HES", "BKR", "HAL", "DVN", "FANG", "TRGP", "CTRA", "MRO"],
    "XLB": ["LIN", "APD", "SHW", "FCX", "ECL", "NEM", "DOW", "NUE", "CTVA", "DD", "VMC", "MLM", "ALB", "CE", "EMN", "FMC", "CF", "MOS"],
    "XLRE": ["PLD", "AMT", "CCI", "EQIX", "PSA", "O", "SPG", "WELL", "DLR", "CSGP", "AVB", "EQR", "VTR", "ARE", "EXR", "INVH", "BXP"],
    "XLU": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "EXC", "XEL", "ED", "PEG", "WEC", "AWK", "ETR", "FE", "EIX", "PPL"]
}

EUROSTOXX_AKTIEN = {
    "Technologie": ["ASML.AS", "SAP.DE", "INF.DE", "ASM.AS", "CAP.PA", "SU.PA", "BSEM.AS", "DSY.PA", "STM.MI", "NOKIA.HE"],
    "Finanzen": ["SAN.MC", "BNP.PA", "ALV.DE", "INGA.AS", "ISP.MI", "MUV2.DE", "CS.PA", "BBVA.MC", "UCG.MI", "DBK.DE", "KBC.BR", "NDA-FI.HE"],
    "Kommunikation": ["ORAN.PA", "DTE.DE", "VOD.L", "TEF.MC", "KPN.AS", "TIM.MI", "VIV.PA", "PROX.BR", "DNA.HE"],
    "Zyklischer Konsum": ["RMS.PA", "LVMH.PA", "OR.PA", "BMW.DE", "MBG.DE", "VOW3.DE", "STE.PA", "IAG.MC", "PUM.DE", "CDI.PA", "ITX.MC", "RNO.PA"],
    "Gesundheit": ["SAN.PA", "BAYN.DE", "MRK.DE", "UCB.BR", "FRE.DE", "QIA.DE", "EL.PA", "FME.DE", "SRG.MI"],
    "Industrie": ["SIE.DE", "AIR.PA", "DHL.DE", "ALST.PA", "SU.PA", "SAF.PA", "DSY.PA", "VCI.PA", "HO.PA", "ENR.DE", "MTX.DE", "PRY.MI"],
    "Basiskonsum": ["HEIA.AS", "BN.PA", "ULVR.L", "ABI.BR", "ABEA.DE", "BEI.DE", "CA.PA", "AH.AS", "KERRY.I"],
    "Energie": ["TTE.PA", "ENI.MI", "REP.MC", "TEN.MI", "OMV.VI", "SHEL.AS", "GALP.LS", "NESTE.HE"],
    "Materialien": ["BAS.DE", "CRH.L", "AI.PA", "SY1.DE", "MT.AS", "UPM.HE", "COV.DE", "HEI.DE", "DSM.AS", "SOLB.BR"],
    "Immobilien": ["VNA.DE", "URW.AS", "LEG.DE", "AROUNDTOWN.DE", "ICAD.PA", "KLEIM.PA", "WDP.BR"],
    "Versorger": ["IBE.MC", "ENEL.MI", "RWE.DE", "ENGIE.PA", "EOAN.DE", "EDP.LS", "ITRN.MI", "TER.MC", "FUM1V.HE"]
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
    try:
        data = yf.download(tickers, period="200d", progress=False)
        
        if data.empty:
            return pd.DataFrame()
            
        # Robuster Umgang mit yfinance MultiIndex Änderungen
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close'] if 'Close' in data.columns.get_level_values(0) else data
        else:
            close_data = data
            
    except Exception as e:
        st.error(f"Fehler beim Laden der Sektor-Daten: {e}")
        return pd.DataFrame()
        
    results = []
    for ticker in tickers:
        if ticker not in close_data.columns:
            continue
            
        # Fehlende Tagesdaten entfernen, um iloc[-1] Fehler zu vermeiden
        series = close_data[ticker].dropna()
        
        if len(series) < 130:
            continue
            
        current_price = float(series.iloc[-1])
        sma_130 = float(series.rolling(window=130).mean().iloc[-1])
        rsl = 0 if sma_130 == 0 else current_price / sma_130
        
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
        
    if not results:
        return pd.DataFrame()
        
    return pd.DataFrame(results).sort_values(by="RSL", ascending=False)

@st.cache_data(ttl=3600)
def analyze_stocks(tickers, apply_ema_filter, rsl_threshold):
    if not tickers:
        return pd.DataFrame()
    
    try:
        data = yf.download(tickers, period="200d", progress=False)
        
        if data.empty:
            return pd.DataFrame()
            
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close'] if 'Close' in data.columns.get_level_values(0) else data
        elif len(tickers) == 1:
            close_data = data[['Close']].rename(columns={'Close': tickers[0]}) if 'Close' in data.columns else data
        else:
            close_data = data
            
    except Exception:
        return pd.DataFrame()
        
    results = []
    for ticker in tickers:
        if ticker not in close_data.columns:
            continue
            
        series = close_data[ticker].dropna()
        if len(series) < 130:
            continue
            
        current_price = float(series.iloc[-1])
        sma_130 = float(series.rolling(window=130).mean().iloc[-1])
        rsl = current_price / sma_130 if sma_130 > 0 else 0
        
        if rsl < rsl_threshold:
            continue
            
        ema5 = series.ewm(span=5, adjust=False).mean()
        ema20 = series.ewm(span=20, adjust=False).mean()
        
        has_fresh_cross = False
        if len(ema5) >= 4:
            today_bullish = float(ema5.iloc[-1]) > float(ema20.iloc[-1])
            past_bearish = float(ema5.iloc[-4]) <= float(ema20.iloc[-4])
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

def color_cells(val):
    """Zentrale Farblogik für Long, Short, Neutral und Matches."""
    if isinstance(val, str):
        if val == "Long" or "Match 🟢" in val:
            return 'background-color: rgba(0, 255, 0, 0.2)'
        elif val == "Short" or "Match 🔴" in val:
            return 'background-color: rgba(255, 0, 0, 0.2)'
        elif val == "Neutral":
            return 'background-color: rgba(255, 255, 0, 0.2)'
        elif "Mismatch ⚠️" in val:
            return 'background-color: rgba(255, 165, 0, 0.2)'
    return ''

def display_styled_dataframe(df):
    """Sicheres Einfärben der gesamten Tabelle, egal welche Pandas Version installiert ist."""
    if df.empty:
        st.write("Keine Daten vorhanden (Eventuell Verbindungsfehler zu Yahoo Finance).")
        return
    try:
        st.dataframe(df.style.map(color_cells), use_container_width=True)
    except AttributeError:
        st.dataframe(df.style.applymap(color_cells), use_container_width=True)

# --- UI Aufbau ---
st.title("🖥️ RESTOR Trading Terminal (v6.1 & v7.1)")
st.markdown("**Regelwerk:** 4h-Chart Ausführung | 1d-Filterung | 0,5 % Risiko pro Trade")

# SCHRITT 1: Sektor RSL
st.markdown("---")
st.header("Schritt 1: Sektor-RSL Analyse")

# Layout-Anpassung: Die Tabelle in Schritt 1 erhält dieselbe Breite wie die Mismatch-Tabelle in Schritt 2
col_t1, col_t_empty = st.columns([1.5, 1])

with col_t1:
    df_sectors = fetch_sector_rsl()
    if not df_sectors.empty:
        display_styled_dataframe(df_sectors)
    else:
        st.warning("Ladefehler: Bitte versuche es mit dem Button unten erneut.")
        
    if st.button("🔄 Live-Daten jetzt aktualisieren"):
        st.cache_data.clear()
        st.rerun()

# SCHRITT 2: Manueller Abgleich
st.markdown("---")
st.header("Schritt 2: Sektortrend hinterlegen (Höhere Hochs / Höhere Tiefs)")
st.markdown("Trage hier die Werte (Long/Short/Neutral) aus deiner Marktstruktur-Tabelle ein.")

if not df_sectors.empty:
    match_data = df_sectors.copy()
else:
    # Fallback leere Struktur, falls Yahoo streikt
    match_data = pd.DataFrame([{"Sektor": k, "Name": v, "RSL Signal": "Neutral"} for k, v in SECTOR_MAP.items()])

match_data['T-S (Manuell)'] = "Neutral"

col_edit, col_result = st.columns([1, 1.5])

with col_edit:
    st.markdown("**Eingabemaske**")
    # Nur Sektor, Name und das manuelle Feld anzeigen
    edited_df_view = st.data_editor(
        match_data[['Sektor', 'Name', 'T-S (Manuell)']],
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
    # Das RSL Signal für die Status-Berechnung im Hintergrund wieder anfügen
    edited_df = edited_df_view.merge(match_data[['Sektor', 'RSL Signal']], on='Sektor', how='left')
    
    conditions = [
        (edited_df['RSL Signal'] == 'Long') & (edited_df['T-S (Manuell)'] == 'Long'),
        (edited_df['RSL Signal'] == 'Short') & (edited_df['T-S (Manuell)'] == 'Short')
    ]
    choices = ['Match 🟢', 'Match 🔴']
    edited_df['Status'] = np.select(conditions, choices, default='Mismatch ⚠️')
    
    # Spaltenordnung für die Ergebnistabellen anpassen, damit das RSL Signal dort wieder sichtbar ist
    result_columns = ['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']
    df_matches = edited_df[edited_df['Status'].str.contains('Match')][result_columns]
    df_mismatches = edited_df[edited_df['Status'] == 'Mismatch ⚠️'][result_columns]
    
    st.markdown("### 🎯 Trade-Freigaben (Matches)")
    if not df_matches.empty:
        display_styled_dataframe(df_matches)
    else:
        st.warning("Noch keine perfekten Matches gefunden. Kapital schützen.")
        
    st.markdown("### ❌ Unstimmigkeiten (Mismatches)")
    display_styled_dataframe(df_mismatches)

# --- SCHRITT 3: Einzelaktien Deep Dive ---
st.markdown("---")
st.header("Schritt 3: Einzelaktien Deep Dive")

long_matches = edited_df[edited_df['Status'] == 'Match 🟢']['Sektor'].tolist()

if not long_matches:
    st.info("Warte auf bestätigte 'Match 🟢' Sektoren aus Schritt 2...")
else:
    st.success(f"Starte High-Momentum-Scan für: {', '.join(long_matches)}")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        rsl_limit = st.slider("Minimale Relative Stärke (RSL)", min_value=1.00, max_value=1.20, value=1.05, step=0.01, help="1.05 bedeutet, die Aktie notiert 5% über ihrem SMA 130.")
    with col_f2:
        st.write("") 
        st.write("")
        apply_ema = st.checkbox("Zwingend: Nur Aktien mit frischem EMA5/20 Cross anzeigen", value=False)
    
    tab1, tab2 = st.tabs(["🇺🇸 S&P 500 Auswertung", "🇪🇺 EuroStoxx Auswertung"])
    all_strong_tickers = []
    
    with tab1:
        for sector in long_matches:
            st.subheader(f"Sektor: {sector} ({SECTOR_MAP[sector]})")
            tickers_to_check = SP500_AKTIEN.get(sector, [])
            
            if tickers_to_check:
                with st.spinner(f"Scanne {len(tickers_to_check)} Aktien..."):
                    df_stocks = analyze_stocks(tickers_to_check, apply_ema, rsl_limit)
                    if not df_stocks.empty:
                        st.dataframe(df_stocks, use_container_width=True)
                        all_strong_tickers.extend(df_stocks['Ticker'].tolist())
                    else:
                        st.warning(f"Keine Aktie im Sektor {sector} erreicht aktuell einen RSL von {rsl_limit} (bzw. erfüllt den EMA-Filter).")

    with tab2:
        for sector in long_matches:
            sector_name = SECTOR_MAP[sector]
            st.subheader(f"Europa Sektor: {sector_name}")
            eu_tickers = EUROSTOXX_AKTIEN.get(sector_name, [])
            
            if eu_tickers:
                with st.spinner(f"Scanne {len(eu_tickers)} europäische Aktien..."):
                    df_eu = analyze_stocks(eu_tickers, apply_ema, rsl_limit)
                    if not df_eu.empty:
                        st.dataframe(df_eu, use_container_width=True)
                        all_strong_tickers.extend(df_eu['Ticker'].tolist())
                    else:
                        st.warning(f"Keine Aktie im Sektor {sector_name} erreicht aktuell einen RSL von {rsl_limit} (bzw. erfüllt den EMA-Filter).")

    # TradingView Export
    st.markdown("---")
    st.subheader("📺 TradingView Export")
    if all_strong_tickers:
        st.code(",".join(all_strong_tickers), language="text")
        st.caption("Kopiere diese Zeile und füge sie direkt per STRG+V in deine TradingView Watchlist ein.")

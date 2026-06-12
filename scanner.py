import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="RESTOR Trading Terminal", page_icon="📈", layout="wide")

# Interne Sektor-Datenbanken für Einzelaktien
SP500_AKTIEN = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "AMD", "ADBE", "CSCO", "INTC", "TXN", "QCOM", "INTU", "IBM", "AMAT", "NOW", "LRCX", "MU", "PANW", "KLAC", "ADI", "ROP", "TEL", "HPQ", "STX", "WDC", "FTNT", "ANET", "CDW", "CDNS", "SNPS", "APH", "GLW", "MSI", "SMCI", "TYL", "PTC", "FICO", "TER", "ANSS", "MCHP", "ON", "NTAP", "AKAM", "JNPR", "TRMB", "FFIV", "SWKS", "QRVO", "MPWR", "ENPH", "SEDG"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "AXP", "SPGI", "BX", "CB", "MMC", "PGR", "CME", "SCHW", "BLK", "AON", "ICE", "FI", "USB", "PNC", "TFC", "COF", "BK", "AIG", "TRV", "MET", "PRU", "AFL", "ALL", "DFS", "SYF", "STT", "NTRS", "MTMT", "AMP", "FITB", "MTB", "HBAN", "RF", "CFG", "KEY", "CMA", "ZION"],
    "XLC": ["META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "VZ", "T", "CHTR", "TMUS", "ATVI", "EA", "TTWO", "WBD", "FOXA", "FOX", "PARA", "OMC", "IPG", "LYV", "MTCH", "NWSA", "NWS", "LBRDA"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "BKNG", "TJX", "CMG", "MAR", "HLT", "ORLY", "AZO", "TSCO", "F", "GM", "DHI", "LEN", "ROST", "LVS", "EXPE", "RCL", "CCL", "YUM", "DRI", "KMX", "EBAY", "ETSY", "HAS", "MAT", "APTV", "BWA", "LKQ", "GPC", "DVA", "PHM", "NVR", "POOL", "GRMN"],
    "XLV": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "DHR", "ABT", "PFE", "AMGN", "ISRG", "SYK", "BSY", "VRTX", "BSX", "ZTS", "CI", "CVS", "GILD", "BDX", "HUM", "MCK", "MTD", "ALGN", "IDXX", "RMD", "DXCM", "EW", "HCA", "A", "CAH", "BIIB", "ILMN", "STE", "WST", "COO", "HOLX", "BAX", "ZBH", "COR", "INCY", "VTRS", "CRL", "XRAY"],
    "XLI": ["CAT", "GE", "RTX", "LMT", "BA", "UNP", "UPS", "HON", "DE", "EMR", "ETN", "ITW", "NOC", "GD", "PH", "CMI", "PCAR", "ROK", "TT", "CARR", "OTIS", "URI", "CPRT", "FAST", "GWW", "FDX", "DAL", "UAL", "AAL", "LUV", "CSX", "NSC", "RSG", "WM", "CHRW", "EXPD", "JBHT", "ODFL", "R", "NDSN", "SNA", "SWK"],
    "XLP": ["WMT", "PG", "COST", "KO", "PEP", "PM", "MO", "MDLZ", "TGT", "EL", "CL", "KMB", "GIS", "SYY", "K", "HSY", "KHC", "CHD", "CLX", "MKC", "CPB", "SJM", "TAP", "STZ", "MNST", "KR", "WBA", "DG", "DLTR", "TSN", "CAG", "LW"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "OXY", "WMB", "KMI", "HAL", "BKR", "HES", "DVN", "FANG", "CTRA", "TRGP", "MRO", "APA", "OKE", "EQT", "CHK"],
    "XLB": ["LIN", "SHW", "ECL", "APD", "NEM", "FCX", "DOW", "DD", "CTVA", "NUE", "VMC", "MLM", "ALB", "FMC", "CE", "EMN", "IFF", "PPG", "CF", "MOS", "STLD", "PKG", "WRK", "IP", "AMCR", "BALL", "SEE"],
    "XLRE": ["PLD", "AMT", "EQIX", "WELL", "SPG", "PSA", "O", "DLR", "CSGP", "CCI", "VICI", "CBRE", "AVB", "EQR", "EXR", "ARE", "INVH", "MAA", "UDR", "BXP", "HST", "IRM", "KIM", "REG", "VTR", "WY", "CPT", "ESS"],
    "XLU": ["NEE", "SO", "DUK", "SRE", "AEP", "D", "EXC", "XEL", "ED", "WEC", "PEG", "AWK", "EIX", "ETR", "FE", "PPL", "CMS", "AEE", "LNT", "NI", "PNW", "CNP", "ES", "EVRG", "ATO", "NRG", "VST"]
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
    match_data = pd.DataFrame([{"Sektor": k, "Name": v, "RSL Signal": "Neutral"} for k, v in SECTOR_MAP.items()])

match_data['T-S (Manuell)'] = "Neutral"

col_edit, col_result = st.columns([1, 1.5])

with col_edit:
    st.markdown("**Eingabemaske**")
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
    edited_df = edited_df_view.merge(match_data[['Sektor', 'RSL Signal']], on='Sektor', how='left')
    
    conditions = [
        (edited_df['RSL Signal'] == 'Long') & (edited_df['T-S (Manuell)'] == 'Long'),
        (edited_df['RSL Signal'] == 'Short') & (edited_df['T-S (Manuell)'] == 'Short')
    ]
    choices = ['Match 🟢', 'Match 🔴']
    edited_df['Status'] = np.select(conditions, choices, default='Mismatch ⚠️')
    
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
    
    # Getrennte Listen für den Export
    sp500_strong_tickers = []
    euro_strong_tickers = []
    
    with tab1:
        for sector in long_matches:
            st.subheader(f"Sektor: {sector} ({SECTOR_MAP[sector]})")
            tickers_to_check = SP500_AKTIEN.get(sector, [])
            
            if tickers_to_check:
                with st.spinner(f"Scanne {len(tickers_to_check)} Aktien..."):
                    df_stocks = analyze_stocks(tickers_to_check, apply_ema, rsl_limit)
                    if not df_stocks.empty:
                        st.dataframe(df_stocks, use_container_width=True)
                        sp500_strong_tickers.extend(df_stocks['Ticker'].tolist())
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
                        euro_strong_tickers.extend(df_eu['Ticker'].tolist())
                    else:
                        st.warning(f"Keine Aktie im Sektor {sector_name} erreicht aktuell einen RSL von {rsl_limit} (bzw. erfüllt den EMA-Filter).")

    # TradingView Export - Getrennt nach Märkten
    st.markdown("---")
    st.subheader("📺 TradingView Export")
    st.caption("Kopiere diese Zeilen und füge sie direkt per STRG+V in deine TradingView Watchlists ein.")
    
    if sp500_strong_tickers or euro_strong_tickers:
        col_tv1, col_tv2 = st.columns(2)
        
        with col_tv1:
            st.markdown("**🇺🇸 S&P 500 Matches**")
            if sp500_strong_tickers:
                st.code(",".join(sp500_strong_tickers), language="text")
            else:
                st.info("Keine S&P 500 Ticker zum Exportieren.")
                
        with col_tv2:
            st.markdown("**🇪🇺 EuroStoxx Matches**")
            if euro_strong_tickers:
                st.code(",".join(euro_strong_tickers), language="text")
            else:
                st.info("Keine EuroStoxx Ticker zum Exportieren.")
    else:
        st.info("Aktuell keine Ticker für den Export vorhanden.")

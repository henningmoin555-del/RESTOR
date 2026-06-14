import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="Sektorfilter Trading nach RSL / HH-HT", page_icon="📈", layout="wide")

TRENDS_FILE = "sector_trends.json"

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
    "Technologie": ["ASML.AS", "SAP.DE", "INF.DE", "ASM.AS", "CAP.PA", "SU.PA", "BSEM.AS", "DSY.PA", "STM.MI", "NOKIA.HE", "LOGN.SW", "TEMN.SW", "SOON.SW"],
    "Finanzen": ["SAN.MC", "BNP.PA", "ALV.DE", "INGA.AS", "ISP.MI", "MUV2.DE", "CS.PA", "BBVA.MC", "UCG.MI", "DBK.DE", "KBC.BR", "NDA-FI.HE", "UBSG.SW", "ZURN.SW", "BARC.L", "HSBA.L", "LLOY.L", "NWG.L", "PRU.L", "AGN.AS", "CBK.DE", "SREN.SW", "SCB.L"],
    "Kommunikation": ["ORAN.PA", "DTE.DE", "VOD.L", "TEF.MC", "KPN.AS", "TIM.MI", "VIV.PA", "PROX.BR", "DNA.HE", "ELISA.HE", "BT-A.L", "UMG.AS", "PUB.PA", "WPP.L", "INW.MI", "SGEF.PA"],
    "Zyklischer Konsum": ["RMS.PA", "LVMH.PA", "OR.PA", "BMW.DE", "MBG.DE", "VOW3.DE", "STE.PA", "IAG.MC", "PUM.DE", "CDI.PA", "ITX.MC", "RNO.PA", "RACE.MI", "MONC.MI", "STLA.MI", "HMB.ST", "NXT.L", "PORS.DE", "PAH3.DE", "CFR.SW", "CPG.L", "ADS.DE", "JD.L"],
    "Gesundheit": ["SAN.PA", "BAYN.DE", "MRK.DE", "UCB.BR", "FRE.DE", "QIA.DE", "EL.PA", "FME.DE", "SRG.MI", "NOVN.SW", "ROG.SW", "LONN.SW", "GSK.L", "AZN.L", "NOVO-B.CO", "ALC.SW", "SHL.DE", "COLO-B.CO", "HLN.L", "SNW.DE"],
    "Industrie": ["SIE.DE", "AIR.PA", "DHL.DE", "ALST.PA", "SU.PA", "SAF.PA", "DSY.PA", "VCI.PA", "HO.PA", "ENR.DE", "MTX.DE", "PRY.MI", "ABB.SW", "VOLV-B.ST", "BAE.L", "DSV.CO", "KNIN.SW", "SGO.PA", "GEBN.SW", "EPI-A.ST", "SAND.ST", "ASSA-B.ST", "RTO.L", "RHM.DE"],
    "Basiskonsum": ["HEIA.AS", "BN.PA", "ULVR.L", "ABI.BR", "ABEA.DE", "BEI.DE", "CA.PA", "AH.AS", "KERRY.I", "NESN.SW", "LIND.SW", "DGE.L", "BATS.L", "IMB.L", "RKT.L", "ORK.OL", "SALM.OL", "AD.AS", "AAK.ST"],
    "Energie": ["TTE.PA", "ENI.MI", "REP.MC", "TEN.MI", "OMV.VI", "SHEL.AS", "GALP.LS", "NESTE.HE", "BP.L", "EQNR.OL", "SNAM.MI", "AKRBP.OL", "VWS.CO"],
    "Materialien": ["BAS.DE", "CRH.L", "AI.PA", "SY1.DE", "MT.AS", "UPM.HE", "COV.DE", "HEI.DE", "DSM.AS", "SOLB.BR", "RIO.L", "GLEN.L", "AAL.L", "HOLN.SW", "SIKA.SW", "GIVN.SW", "STORAERV.HE", "NZYM-B.CO", "BHP.L", "AKZA.AS", "KNEBV.HE"],
    "Immobilien": ["VNA.DE", "URW.AS", "LEG.DE", "AROUNDTOWN.DE", "ICAD.PA", "KLEIM.PA", "WDP.BR", "PSPN.SW", "SPSN.SW", "LAND.L", "SGRO.L", "BALD-B.ST", "CAST.ST", "GFC.PA", "AED.BR"],
    "Versorger": ["IBE.MC", "ENEL.MI", "RWE.DE", "ENGIE.PA", "EOAN.DE", "EDP.LS", "ITRN.MI", "TER.MC", "FUM1V.HE", "NG.L", "SSE.L", "SVT.L", "ORSTED.CO", "A2A.MI", "HER.MI", "IREN.MI"]
}

US_SECTOR_MAP = {
    "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
    "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
    "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
    "XLRE": "Immobilien", "XLU": "Versorger"
}

EU_SECTOR_MAP = {
    "EXV3.DE": "Technologie", "EXV1.DE": "Finanzen", "EXV9.DE": "Kommunikation", 
    "EXV6.DE": "Zyklischer Konsum", "EXV5.DE": "Gesundheit", "EXV4.DE": "Industrie", 
    "EXV2.DE": "Basiskonsum", "EXV8.DE": "Energie", "EXV7.DE": "Materialien", 
    "EXSA.DE": "Immobilien", "EXVA.DE": "Versorger"
}

# --- Hilfsfunktionen für das Speichern der Trends ---
def load_trends():
    if os.path.exists(TRENDS_FILE):
        try:
            with open(TRENDS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_trends(trends_dict):
    with open(TRENDS_FILE, "w") as f:
        json.dump(trends_dict, f)

# --- Hilfsfunktionen für die Marktdaten ---
@st.cache_data(ttl=3600)
def fetch_sector_rsl(region="US"):
    sector_map = US_SECTOR_MAP if region == "US" else EU_SECTOR_MAP
    tickers = list(sector_map.keys())
    
    try:
        data = yf.download(tickers, period="200d", progress=False)
        
        if data.empty:
            return pd.DataFrame()
            
        if isinstance(data.columns, pd.MultiIndex):
            close_data = data['Close'] if 'Close' in data.columns.get_level_values(0) else data
        else:
            close_data = data
            
    except Exception as e:
        st.error(f"Fehler beim Laden der Sektor-Daten ({region}): {e}")
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
        rsl = 0 if sma_130 == 0 else current_price / sma_130
        
        if rsl >= 1.010:
            status = "Long"
        elif rsl <= 0.989:
            status = "Short"
        else:
            status = "Neutral"
            
        results.append({
            "Sektor": ticker,
            "Name": sector_map[ticker],
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
            
        # Volatilität berechnen (Annualisierte Standardabweichung der letzten 130 Tage)
        returns = series.pct_change().dropna()
        if len(returns) >= 130:
            volatility = float(returns.tail(130).std() * np.sqrt(252))
        else:
            volatility = 0.0
            
        # Smooth Momentum Score: RSL risikoadjustiert
        smooth_rsl = rsl / volatility if volatility > 0 else 0
            
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
            "Kurs": round(current_price, 2),
            "RSL": round(rsl, 3),
            "Vola (p.a.)": f"{round(volatility * 100, 1)}%",
            "Smooth RSL": round(smooth_rsl, 2),
            "EMA 5/20 Signal": signal_text
        })
            
    df = pd.DataFrame(results)
    if not df.empty:
        # Sortierung erfolgt nach dem risikoadjustierten Score
        df = df.sort_values(by="Smooth RSL", ascending=False).head(15)
    return df

def color_cells(val):
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
    if df.empty:
        st.write("Keine Daten vorhanden.")
        return
    try:
        st.dataframe(df.style.map(color_cells), use_container_width=True)
    except AttributeError:
        st.dataframe(df.style.applymap(color_cells), use_container_width=True)

# --- UI Aufbau ---
st.title("🖥️ Sektorfilter Trading nach RSL / HH-HT")

# Roter HTML Disclaimer
st.markdown("""
<div style="background-color: #ffe6e6; border-left: 5px solid #ff4d4d; padding: 15px; color: #cc0000; border-radius: 5px; margin-bottom: 20px;">
    <strong>⚠️ Haftungsausschluss (Disclaimer):</strong><br>
    Die App dient ausschließlich zu Informations- und Bildungszwecken. Es handelt sich um keine Anlageberatung und keine Aufforderung zum Kauf oder Verkauf von Wertpapieren. Alle Daten sind ohne Gewähr (keine Garantie für Richtigkeit, Vollständigkeit oder Aktualität der Kurse). Jeder Nutzer handelt auf eigenes Risiko.
</div>
""", unsafe_allow_html=True)

st.markdown("**Regelwerk (v7.1):** 4h-Chart Ausführung | 1d-Filterung | 0,5 % Risiko pro Trade")

# Aufklappbare Info-Bereiche
col_info1, col_info2 = st.columns(2)

with col_info1:
    with st.expander("ℹ️ Funktionsaufbau (Wie funktioniert das Tool & v7.1?)"):
        st.markdown("""
        **Die Strategie (v7.1) im Detail:**
        Dieses Terminal automatisiert den Top-Down-Ansatz. Gefiltert wird auf dem **Tageschart (1d)**, die exakte Trade-Ausführung findet auf dem **4-Stunden-Chart (4h)** statt, um Rauschen zu vermeiden. Das Risiko ist strikt auf **0,5 % pro Trade** begrenzt.
        
        **Der 3-Schritte-Prozess:**
        1. **Marktphase (Sektor-RSL):** Die Relative Stärke (RSL) der übergeordneten Sektoren wird auf Basis des 130-Tage-SMA berechnet. 
           * RSL $\ge$ 1.010 $\rightarrow$ **Long**
           * RSL $\le$ 0.989 $\rightarrow$ **Short**
        2. **Trendabgleich (HH/HT):** Das maschinelle RSL-Signal wird in der Eingabemaske manuell mit deiner Chartanalyse (Marktstruktur: Höhere Hochs / Höhere Tiefs) abgeglichen. Nur bei einem **Match** (z.B. RSL Long + Struktur Long) wird der Sektor freigegeben.
        3. **Deep Dive & "Smooth RSL":** Im freigegebenen Sektor sucht das Tool nach den stärksten Einzelaktien. Hier greift das v7.1 Qualitätskriterium:
           * **Smooth RSL = RSL / Volatilität (p.a.)**
           * *Der Sinn:* Statt stur nach dem stärksten Momentum zu filtern, belohnt dieser Score Aktien, die **ruhig und stetig** steigen. Hochvolatile "Zocker-Aktien" werden abgestraft. Das schützt dich vor heftigen Intraday-Schwankungen und verhindert unnötige Stop-Outs im 4h-Chart. Das Setup wird durch ein optionales frisches **EMA 5/20 Cross** abgerundet.
        """)

with col_info2:
    with st.expander("📊 Datenherkunft & Technik"):
        st.markdown("""
        * **Datenquelle:** Alle Kursdaten werden in Echtzeit via **Yahoo Finance** (`yfinance`) bezogen. Es werden Tagesendkurse (1d) verarbeitet.
        * **S&P 500 Sektoren:** Für den US-Markt werden die bekannten SPDR Sector ETFs genutzt (z. B. XLK für Technologie).
        * **EuroStoxx Sektoren:** Für den europäischen Markt greift das Tool auf die iShares STOXX Europe 600 Sektor-ETFs zurück (z. B. EXV3.DE für Technologie).
        * **Einzelaktien:** Die durchsuchten Aktienlisten sind fest im Code hinterlegt und repräsentieren die Schwergewichte und liquidesten Werte des jeweiligen Sektors.
        * **Speicherung:** Deine manuellen Eingaben aus Schritt 2 werden lokal in einer Datei (`sector_trends.json`) gespeichert, sodass sie beim Neuladen der Seite erhalten bleiben.
        """)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔄 Alle Live-Daten jetzt aktualisieren", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Globale Variablen für den Export sammeln
sp500_strong_tickers = []
euro_strong_tickers = []


# =====================================================================
# BLOCK 1: S&P 500
# =====================================================================
st.markdown("---")
st.markdown("## 🇺🇸 S&P500 Analyse")

# S&P500 - Schritt 1
st.subheader("S&P500 - Schritt 1: Sektor-RSL Analyse")
col_us1, col_us2 = st.columns([1.5, 1])

with col_us1:
    df_sectors_us = fetch_sector_rsl("US")
    if not df_sectors_us.empty:
        display_styled_dataframe(df_sectors_us)
    else:
        st.warning("Ladefehler US-Sektoren.")

# S&P500 - Schritt 2
st.subheader("S&P500 - Schritt 2: Sektortrend hinterlegen (HH / HT)")
if not df_sectors_us.empty:
    match_data_us = df_sectors_us.copy()
else:
    match_data_us = pd.DataFrame([{"Sektor": k, "Name": v, "RSL Signal": "Neutral"} for k, v in US_SECTOR_MAP.items()])

# Aktuell gespeicherte Trends laden und in das DataFrame einfügen
saved_trends = load_trends()
match_data_us['T-S (Manuell)'] = match_data_us['Sektor'].apply(lambda x: saved_trends.get(x, "Neutral"))

col_edit_us, col_result_us = st.columns([1, 1.5])

with col_edit_us:
    st.markdown("**US Eingabemaske**")
    # Nur Sektor, Name und Dropdown, OHNE RSL Signal Spalte und ohne Index-Zahlen
    edited_df_view_us = st.data_editor(
        match_data_us[['Sektor', 'Name', 'T-S (Manuell)']],
        column_config={"T-S (Manuell)": st.column_config.SelectboxColumn("T-S (Manuell)", options=["Long", "Short", "Neutral"], required=True)},
        use_container_width=True,
        hide_index=True,
        key="editor_us"
    )

    # Nach der Eingabe prüfen, ob sich Werte geändert haben und abspeichern
    current_trends = load_trends()
    needs_save = False
    for _, row in edited_df_view_us.iterrows():
        if current_trends.get(row['Sektor']) != row['T-S (Manuell)']:
            current_trends[row['Sektor']] = row['T-S (Manuell)']
            needs_save = True
    if needs_save:
        save_trends(current_trends)

with col_result_us:
    edited_df_us = edited_df_view_us.merge(match_data_us[['Sektor', 'RSL Signal']], on='Sektor', how='left')
    conditions_us = [
        (edited_df_us['RSL Signal'] == 'Long') & (edited_df_us['T-S (Manuell)'] == 'Long'),
        (edited_df_us['RSL Signal'] == 'Short') & (edited_df_us['T-S (Manuell)'] == 'Short')
    ]
    edited_df_us['Status'] = np.select(conditions_us, ['Match 🟢', 'Match 🔴'], default='Mismatch ⚠️')
    
    df_matches_us = edited_df_us[edited_df_us['Status'].str.contains('Match')][['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']]
    df_mismatches_us = edited_df_us[edited_df_us['Status'] == 'Mismatch ⚠️'][['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']]
    
    st.markdown("##### 🎯 US Trade-Freigaben")
    if not df_matches_us.empty: display_styled_dataframe(df_matches_us)
    else: st.warning("Noch keine perfekten US Matches gefunden.")
        
    st.markdown("##### ❌ US Unstimmigkeiten")
    display_styled_dataframe(df_mismatches_us)

# S&P500 - Schritt 3
st.subheader("S&P500 - Schritt 3: Einzelaktien Deep Dive")
long_matches_us = edited_df_us[edited_df_us['Status'] == 'Match 🟢']['Sektor'].tolist()

if not long_matches_us:
    st.info("Warte auf bestätigte 'Match 🟢' US Sektoren aus Schritt 2...")
else:
    col_f1_us, col_f2_us = st.columns(2)
    with col_f1_us:
        rsl_limit_us = st.slider("Minimale RSL (US)", 1.00, 1.20, 1.05, 0.01, key="slider_us")
    with col_f2_us:
        st.write("") 
        st.write("")
        apply_ema_us = st.checkbox("Nur Aktien mit frischem EMA5/20 Cross (US)", False, key="chk_us")
    
    for sector in long_matches_us:
        st.markdown(f"**US Sektor: {sector} ({US_SECTOR_MAP[sector]})**")
        tickers_to_check = SP500_AKTIEN.get(sector, [])
        if tickers_to_check:
            with st.spinner(f"Scanne US Aktien..."):
                df_stocks = analyze_stocks(tickers_to_check, apply_ema_us, rsl_limit_us)
                if not df_stocks.empty:
                    st.dataframe(df_stocks, use_container_width=True, hide_index=True)
                    sp500_strong_tickers.extend(df_stocks['Ticker'].tolist())
                else:
                    st.warning(f"Keine Treffer im Sektor {sector}.")


# =====================================================================
# BLOCK 2: EUROSTOXX
# =====================================================================
st.markdown("---")
st.markdown("## 🇪🇺 EuroStoxx Analyse")

# EuroStoxx - Schritt 1
st.subheader("EuroStoxx - Schritt 1: Sektor-RSL Analyse")
col_eu1, col_eu2 = st.columns([1.5, 1])

with col_eu1:
    df_sectors_eu = fetch_sector_rsl("EU")
    if not df_sectors_eu.empty:
        display_styled_dataframe(df_sectors_eu)
    else:
        st.warning("Ladefehler EU-Sektoren.")

# EuroStoxx - Schritt 2
st.subheader("EuroStoxx - Schritt 2: Sektortrend hinterlegen (HH / HT)")
if not df_sectors_eu.empty:
    match_data_eu = df_sectors_eu.copy()
else:
    match_data_eu = pd.DataFrame([{"Sektor": k, "Name": v, "RSL Signal": "Neutral"} for k, v in EU_SECTOR_MAP.items()])

# Aktuell gespeicherte Trends für EU laden
saved_trends_eu = load_trends()
match_data_eu['T-S (Manuell)'] = match_data_eu['Sektor'].apply(lambda x: saved_trends_eu.get(x, "Neutral"))

col_edit_eu, col_result_eu = st.columns([1, 1.5])

with col_edit_eu:
    st.markdown("**EU Eingabemaske**")
    # Nur Sektor, Name und Dropdown, OHNE RSL Signal Spalte und ohne Index-Zahlen
    edited_df_view_eu = st.data_editor(
        match_data_eu[['Sektor', 'Name', 'T-S (Manuell)']],
        column_config={"T-S (Manuell)": st.column_config.SelectboxColumn("T-S (Manuell)", options=["Long", "Short", "Neutral"], required=True)},
        use_container_width=True,
        hide_index=True,
        key="editor_eu"
    )

    # Nach der Eingabe prüfen, ob sich Werte geändert haben und abspeichern
    current_trends_eu = load_trends()
    needs_save_eu = False
    for _, row in edited_df_view_eu.iterrows():
        if current_trends_eu.get(row['Sektor']) != row['T-S (Manuell)']:
            current_trends_eu[row['Sektor']] = row['T-S (Manuell)']
            needs_save_eu = True
    if needs_save_eu:
        save_trends(current_trends_eu)

with col_result_eu:
    edited_df_eu = edited_df_view_eu.merge(match_data_eu[['Sektor', 'RSL Signal']], on='Sektor', how='left')
    conditions_eu = [
        (edited_df_eu['RSL Signal'] == 'Long') & (edited_df_eu['T-S (Manuell)'] == 'Long'),
        (edited_df_eu['RSL Signal'] == 'Short') & (edited_df_eu['T-S (Manuell)'] == 'Short')
    ]
    edited_df_eu['Status'] = np.select(conditions_eu, ['Match 🟢', 'Match 🔴'], default='Mismatch ⚠️')
    
    df_matches_eu = edited_df_eu[edited_df_eu['Status'].str.contains('Match')][['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']]
    df_mismatches_eu = edited_df_eu[edited_df_eu['Status'] == 'Mismatch ⚠️'][['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']]
    
    st.markdown("##### 🎯 EU Trade-Freigaben")
    if not df_matches_eu.empty: display_styled_dataframe(df_matches_eu)
    else: st.warning("Noch keine perfekten EU Matches gefunden.")
        
    st.markdown("##### ❌ EU Unstimmigkeiten")
    display_styled_dataframe(df_mismatches_eu)

# EuroStoxx - Schritt 3
st.subheader("EuroStoxx - Schritt 3: Einzelaktien Deep Dive")
long_matches_eu = edited_df_eu[edited_df_eu['Status'] == 'Match 🟢']['Sektor'].tolist()

if not long_matches_eu:
    st.info("Warte auf bestätigte 'Match 🟢' EU Sektoren aus Schritt 2...")
else:
    col_f1_eu, col_f2_eu = st.columns(2)
    with col_f1_eu:
        rsl_limit_eu = st.slider("Minimale RSL (EU)", 1.00, 1.20, 1.05, 0.01, key="slider_eu")
    with col_f2_eu:
        st.write("") 
        st.write("")
        apply_ema_eu = st.checkbox("Nur Aktien mit frischem EMA5/20 Cross (EU)", False, key="chk_eu")
    
    for sector in long_matches_eu:
        sector_name = EU_SECTOR_MAP[sector]
        st.markdown(f"**EU Sektor: {sector_name} ({sector})**")
        eu_tickers = EUROSTOXX_AKTIEN.get(sector_name, [])
        if eu_tickers:
            with st.spinner(f"Scanne EU Aktien..."):
                df_eu_stocks = analyze_stocks(eu_tickers, apply_ema_eu, rsl_limit_eu)
                if not df_eu_stocks.empty:
                    st.dataframe(df_eu_stocks, use_container_width=True, hide_index=True)
                    euro_strong_tickers.extend(df_eu_stocks['Ticker'].tolist())
                else:
                    st.warning(f"Keine Treffer im Sektor {sector_name}.")


# =====================================================================
# BLOCK 4: EXPORT
# =====================================================================
st.markdown("---")
st.subheader("📺 TradingView Export")
st.caption("Kopiere diese Zeilen und füge sie direkt per STRG+V in deine TradingView Watchlists ein.")

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

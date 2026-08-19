import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="Sektorfilter Trading nach RSL / HH-HT", page_icon="📈", layout="wide")

TRENDS_FILE = "sector_trends.json"

# Vollständige Sektor-Datenbanken
SP500_AKTIEN = {
    "XLK": ["AAPL","MSFT","NVDA","AVGO","ORCL","CRM","AMD","ADBE","CSCO","INTC","TXN","QCOM","INTU","IBM","AMAT","NOW","LRCX","MU","PANW","KLAC","ADI","ROP","TEL","HPQ","STX","WDC","FTNT","ANET","CDW","CDNS","SNPS","APH","GLW","MSI","SMCI","TYL","PTC","FICO","TER","ANSS","MCHP","ON","NTAP","AKAM","JNPR","TRMB","FFIV","SWKS","QRVO","MPWR","ENPH","SEDG","FSLR","IT","EPAM","GEN","JBL","KEYS","TDY","ZBRA","NXPI","PAYC","VRSN"],
    "XLF": ["BRK-B","JPM","V","MA","BAC","WFC","GS","MS","C","AXP","SPGI","BX","CB","MMC","PGR","CME","SCHW","BLK","AON","ICE","FI","USB","PNC","TFC","COF","BK","AIG","TRV","MET","PRU","AFL","ALL","DFS","SYF","STT","NTRS","AMP","FITB","MTB","HBAN","RF","CFG","KEY","CMA","ZION","BEN","CBOE","CINF","FDS","GL","HIG","IVZ","L","MCO","NDAQ","PFG","RJF","WRB","WTW","BRO","EG","EVR","FHN","GPN","JKHY","LNC"],
    "XLC": ["META","GOOGL","GOOG","NFLX","DIS","CMCSA","VZ","T","CHTR","TMUS","EA","TTWO","WBD","FOXA","FOX","PARA","OMC","IPG","LYV","MTCH","NWSA","NWS","LBRDA","DISH","LBRDK","NTES","SIRI"],
    "XLY": ["AMZN","TSLA","HD","MCD","NKE","SBUX","LOW","BKNG","TJX","CMG","MAR","HLT","ORLY","AZO","TSCO","F","GM","DHI","LEN","ROST","LVS","EXPE","RCL","CCL","YUM","DRI","KMX","EBAY","ETSY","HAS","MAT","APTV","BWA","LKQ","GPC","DVA","PHM","NVR","POOL","GRMN","AAP","BBY","CZR","DPZ","MGM","MHK","NCLH","PEN","RL","TGT","UAA","VFC","WHR","WYNN"],
    "XLV": ["LLY","UNH","JNJ","ABBV","MRK","TMO","DHR","ABT","PFE","AMGN","ISRG","SYK","BSX","VRTX","ZTS","CI","CVS","GILD","BDX","HUM","MCK","MTD","ALGN","IDXX","RMD","DXCM","EW","HCA","A","CAH","BIIB","ILMN","STE","WST","COO","HOLX","BAX","ZBH","COR","INCY","VTRS","CRL","XRAY","BIO","BMY","HSIC","IQV","LH","MRNA","REGN","TFX","UHS"],
    "XLI": ["CAT","GE","RTX","LMT","BA","UNP","UPS","HON","DE","EMR","ETN","ITW","NOC","GD","PH","CMI","PCAR","ROK","TT","CARR","OTIS","URI","CPRT","FAST","GWW","FDX","DAL","UAL","AAL","LUV","CSX","NSC","RSG","WM","CHRW","EXPD","JBHT","ODFL","R","NDSN","SNA","SWK","AME","AOS","EFX","GNRC","HWM","IEX","INFO","JCI","LHX","MAS","PNR","PWR","TXT","VRSK","WAB","XYL"],
    "XLP": ["WMT","PG","COST","KO","PEP","PM","MO","MDLZ","TGT","EL","CL","KMB","GIS","SYY","K","HSY","KHC","CHD","CLX","MKC","CPB","SJM","TAP","STZ","MNST","KR","WBA","DG","DLTR","TSN","CAG","LW","ADM","BF-B"],
    "XLE": ["XOM","CVX","COP","EOG","SLB","MPC","PSX","VLO","OXY","WMB","KMI","HAL","BKR","HES","DVN","FANG","CTRA","TRGP","MRO","APA","OKE","EQT","CHK","CIVI","PR"],
    "XLB": ["LIN","SHW","ECL","APD","NEM","FCX","DOW","DD","CTVA","NUE","VMC","MLM","ALB","FMC","CE","EMN","IFF","PPG","CF","MOS","STLD","PKG","WRK","IP","AMCR","BALL","SEE"],
    "XLRE": ["PLD","AMT","EQIX","WELL","SPG","PSA","O","DLR","CSGP","CCI","VICI","CBRE","AVB","EQR","EXR","ARE","INVH","MAA","UDR","BXP","HST","IRM","KIM","REG","VTR","WY","CPT","ESS","FRT","SBAC"],
    "XLU": ["NEE","SO","DUK","SRE","AEP","D","EXC","XEL","ED","WEC","PEG","AWK","EIX","ETR","FE","PPL","CMS","AEE","LNT","NI","PNW","CNP","ES","EVRG","ATO","NRG","VST","CEG"]
}

EUROSTOXX_GETTEX_AKTIEN = {
    "EXV1": ["BNP", "ISP", "UCG", "SAN", "BBVA", "DBK", "CBK", "KBC", "INN", "NDB", "DNB", "EBS", "CABK", "ABN", "HBC1", "BCY", "LLD", "NWG", "STAN", "BKT", "SAB", "BCP", "UNI", "BAMI", "BPER", "FINE", "BGN", "BAER", "JYSK", "SYDB"],
    "EXV2": ["DTE", "FTE", "VOD", "TNE5", "KPN", "BTV1", "TLS1", "ELI1", "TEF", "SIA", "O2D", "PROX", "INW", "TEL", "MTX", "SESG"],
    "EXV3": ["ASME", "SAP", "PRX", "IFX", "CGP", "SGM", "NOA3", "BEI", "DSY", "SUG", "LOGN", "SOON", "ASM", "NEM", "BSI", "DTG", "AIXA", "JEN", "SOW", "ATO", "SQ1", "NEX", "WKL", "KNM"],
    "EXV4": ["NOVC", "NOT", "ZEGN", "RHO5", "SNW", "GS7", "BAYN", "FME", "HLN", "ALC", "COLB", "SRT", "QIA", "GRI", "SNH", "DIA", "UCB", "GN", "AMBU", "CHR", "ELE", "GETI", "LONN", "VIFN", "TEC", "GMD", "RDY", "UMG", "CARL", "EVT"],
    "EXV5": ["MBG", "BMW", "8TI", "VOW3", "2FE", "RNL", "PAH3", "CON", "P911", "MICP", "VLE", "FOR", "APTV", "BWA", "RNO", "AML", "NRE1", "SAU", "PUM"],
    "EXV6": ["RIO1", "GLJ", "UPM", "NRS", "SDF", "SY1", "AAL", "BOL", "MT", "STE", "SCMN", "HOLN", "SSAB", "PKN", "ANTO", "FRES", "KAZ", "MDI", "POLY", "VED"],
    "EXV7": ["BAS", "SY1", "COV", "EVK", "DSM", "AKZ", "AI", "CRO", "GIV", "UMG", "LAN", "WCH", "SGO", "JMAT", "EMS", "CLX", "KWS", "SHL", "YAR"],
    "EXV8": ["SGO", "CRH", "HEI", "ACS", "HO", "DG", "FER", "SKA-B", "BDEV", "PSN", "TW", "BKG", "VWS", "GIB", "NIBE", "ROCK-B", "SIG", "SPM"],
    "EXV9": ["LHA", "TUI1", "IAG", "IHG", "EZJ", "AMC", "FLTR", "ENT", "FDP", "SOD", "WIZZ", "RYA", "ACC", "CPG", "EVR", "GRG", "KIN", "PNN", "WTB", "AAL"],
    "EXH1": ["R6C0", "TTE", "BPE5", "ENI", "DNQ", "REP", "GALP", "SNAM", "AKRBP", "LUN", "SU", "OMV", "TEN", "SBM", "VWS", "NEL", "ORST", "PKN"],
    "EXH2": ["UBSG", "LSEG", "DB1", "PRU", "SDR", "HL", "EXPN", "STJ", "III", "KINV", "EQT", "ADJ", "ICP", "SJP", "MNG", "IGG", "NXG", "AJB", "OSB"],
    "EXH3": ["NESR", "UNVB", "GUI", "ABI", "BSN", "HEIA", "BMT", "LND", "DGE", "BATS", "IMB", "KRY", "ORK", "CFR", "DSY", "TATE", "BVIC", "GNC", "AAK", "SALM", "MOWI", "BAK"],
    "EXH4": ["SIE", "SND", "AIR", "ABBN", "DPW", "MTX", "DSV", "VOLV", "EPI", "KNEBV", "BA", "SAFR", "SGE", "RTO", "HTG", "SMIN", "WEIR", "IMI", "SPX", "KNIN", "SGSN", "ADEN", "RND", "BURE"],
    "EXH5": ["ALV", "CS", "ZURN", "MUV2", "HAN", "ASR", "SAM", "SWISS", "LGEN", "NN", "G", "AV", "RSA", "PHNX", "HIS", "ADM", "Baloise", "HELN", "TOP", "GJF"],
    "EXH6": ["REL", "WPP", "PUB", "RTL", "UMG", "INF", "ITV", "PRS", "TF1", "MFEA", "VIV", "PEO", "CTS", "STR", "NWS", "EDH", "SCHA", "SBO"],
    "EXH7": ["MOH", "LOR", "RMI", "HEN3", "KER", "BEI", "PND", "CFR", "CDI", "MONC", "NXT", "BRBY", "SWC", "HUGO", "RCH", "ELE", "HUSQ", "THOM", "UBI", "CDPR"],
    "EXH8": ["ITX", "HM-B", "ZAL", "JD", "KGF", "BME", "SMWH", "MKS", "ICA", "SBRY", "TSCO", "MRW", "NXT", "CRF", "AHD", "COLR", "JER", "MARS", "BMM"],
    "EXH9": ["IBE", "ENEL", "EGI", "RWE", "EOAN", "SSE", "NG", "EDF", "SVTI", "TER", "CNA", "UU", "SVT", "PNN", "A2A", "TRN", "HERA", "EDP", "EDPR", "FUM", "VER"],
    "EXI5": ["VNA", "URW", "LEG", "ARND", "PSP", "SRE", "LAND", "BLND", "GFC", "SPSN", "SEGRO", "BBOX", "DLN", "WKP", "GCP", "TAG", "CST", "KLE", "COV", "WDP"]
}

US_SECTOR_MAP = {
    "XLK": "Technologie", "XLF": "Finanzen", "XLC": "Kommunikation", 
    "XLY": "Zyklischer Konsum", "XLV": "Gesundheit", "XLI": "Industrie", 
    "XLP": "Basiskonsum", "XLE": "Energie", "XLB": "Materialien", 
    "XLRE": "Immobilien", "XLU": "Versorger"
}

EU_SECTOR_MAP = {
    "EXV1.DE": "Banken", "EXV2.DE": "Telekommunikation", "EXV3.DE": "Technologie",
    "EXV4.DE": "Gesundheitswesen", "EXV5.DE": "Automobile & Zulieferer",
    "EXV6.DE": "Grundstoffe", "EXV7.DE": "Chemie", "EXV8.DE": "Bauhauptgewerbe & Materialien",
    "EXV9.DE": "Reise & Freizeit", "EXH1.DE": "Energie / Öl & Gas",
    "EXH2.DE": "Finanzdienstleistungen", "EXH3.DE": "Nahrungsmittel & Getränke",
    "EXH4.DE": "Industrie & Dienstleistungen", "EXH5.DE": "Versicherungen",
    "EXH6.DE": "Medien", "EXH7.DE": "Konsumgüter / Haushalt",
    "EXH8.DE": "Einzelhandel", "EXH9.DE": "Versorger", "EXI5.DE": "Immobilien"
}

# --- Hilfsfunktionen für State & JSON ---
def load_trends():
    if os.path.exists(TRENDS_FILE):
        try:
            with open(TRENDS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_trends(trends_dict):
    with open(TRENDS_FILE, "w") as f:
        json.dump(trends_dict, f)

def get_close_data(tickers):
    """Lädt die Close-Preise für eine Liste von Tickers."""
    data = yf.download(tickers, period="200d", progress=False, threads=True)
    if data.empty:
        return pd.DataFrame()
    
    if isinstance(data.columns, pd.MultiIndex):
        return data['Close'] if 'Close' in data.columns.get_level_values(0) else data
    elif len(tickers) == 1:
        return data[['Close']].rename(columns={'Close': tickers[0]}) if 'Close' in data.columns else data
    return data

# --- Vektorisierte Marktdaten-Analyse ---
@st.cache_data(ttl=14400)
def fetch_sector_rsl(region="US"):
    sector_map = US_SECTOR_MAP if region == "US" else EU_SECTOR_MAP
    tickers = list(sector_map.keys())
    
    try:
        close_data = get_close_data(tickers)
        if close_data.empty: return pd.DataFrame()
    except Exception as e:
        st.error(f"Fehler beim Laden der Sektor-Daten ({region}): {e}")
        return pd.DataFrame()

    close_data = close_data.dropna(axis=1, thresh=130)
    if close_data.empty: return pd.DataFrame()

    current_price = close_data.iloc[-1]
    sma_130 = close_data.rolling(window=130).mean().iloc[-1]
    rsl = current_price / sma_130
    rsl = rsl.replace([np.inf, -np.inf], np.nan).fillna(0)

    df = pd.DataFrame({"Sektor": rsl.index, "RSL": rsl.values})
    df["Name"] = df["Sektor"].map(sector_map)
    df["RSL Signal"] = np.where(df["RSL"] >= 1.010, "Long", np.where(df["RSL"] <= 0.989, "Short", "Neutral"))
    df["RSL"] = df["RSL"].round(3)
    
    return df[["Sektor", "Name", "RSL", "RSL Signal"]].sort_values(by="RSL", ascending=False)

@st.cache_data(ttl=14400)
def analyze_stocks(tickers, apply_ema_filter, rsl_threshold):
    if not tickers: return pd.DataFrame()
    
    try:
        close_data = get_close_data(tickers)
        if close_data.empty: return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    close_data = close_data.dropna(axis=1, thresh=130)
    if close_data.empty: return pd.DataFrame()

    current_price = close_data.iloc[-1]
    sma_130 = close_data.rolling(window=130).mean().iloc[-1]
    rsl = (current_price / sma_130).fillna(0)

    valid_tickers = rsl[rsl >= rsl_threshold].index
    if valid_tickers.empty: return pd.DataFrame()

    close_data = close_data[valid_tickers]
    rsl = rsl[valid_tickers]
    current_price = current_price[valid_tickers]

    returns = close_data.pct_change().tail(130)
    volatility = returns.std() * np.sqrt(252)
    smooth_rsl = rsl / volatility.replace(0, np.nan)

    ema5 = close_data.ewm(span=5, adjust=False).mean()
    ema20 = close_data.ewm(span=20, adjust=False).mean()
    
    today_bullish = ema5.iloc[-1] > ema20.iloc[-1]
    past_bearish = ema5.iloc[-4] <= ema20.iloc[-4]
    has_fresh_cross = today_bullish & past_bearish

    results_df = pd.DataFrame({
        "Ticker": valid_tickers,
        "Kurs": current_price.round(2),
        "RSL": rsl.round(3),
        "Vola (p.a.)": (volatility * 100).round(1).astype(str) + "%",
        "Smooth RSL": smooth_rsl.round(2).fillna(0),
        "Fresh_Cross": has_fresh_cross
    })

    if apply_ema_filter:
        results_df = results_df[results_df["Fresh_Cross"]]

    results_df["EMA 5/20 Signal"] = np.where(results_df["Fresh_Cross"], "🔥 Frisches Cross", "-")
    results_df = results_df.drop(columns=["Fresh_Cross"])

    return results_df.sort_values(by="Smooth RSL", ascending=False).head(15)

@st.cache_data(ttl=14400)
def fetch_top_25_overall(stock_dict, is_eu=False):
    """Berechnet die Top 25 Gesamtmarkt-Werte basierend auf RSL."""
    all_tickers = []
    for ticker_list in stock_dict.values():
        all_tickers.extend(ticker_list)
    all_tickers = list(set(all_tickers))

    download_tickers = [f"{t}.DE" for t in all_tickers] if is_eu else all_tickers

    try:
        close_data = get_close_data(download_tickers)
        if close_data.empty: return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    close_data = close_data.dropna(axis=1, thresh=130)
    if close_data.empty: return pd.DataFrame()

    current_price = close_data.iloc[-1]
    sma_130 = close_data.rolling(window=130).mean().iloc[-1]
    rsl = (current_price / sma_130).fillna(0)

    returns = close_data.pct_change().tail(130)
    volatility = returns.std() * np.sqrt(252)
    smooth_rsl = (rsl / volatility.replace(0, np.nan)).fillna(0)

    df_result = pd.DataFrame({
        "Ticker": close_data.columns,
        "Kurs": current_price.round(2),
        "RSL": rsl.round(3),
        "Vola (p.a.)": (volatility * 100).round(1).astype(str) + "%",
        "Smooth RSL": smooth_rsl.round(2)
    })

    df_result["TV-Ticker"] = df_result["Ticker"].apply(lambda x: x.split(".")[0] if is_eu else x)

    return df_result.sort_values(by="RSL", ascending=False).head(25)

# --- UI Helfer ---
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
    else:
        st.dataframe(df.style.map(color_cells), use_container_width=True, hide_index=True)

# --- DRY Rendering Funktion für Sektoren ---
def render_market_section(region_name, flag, sector_map, stock_dict, is_eu=False):
    st.markdown("---")
    st.markdown(f"## {flag} {region_name} Analyse")
    region_code = "EU" if is_eu else "US"

    st.subheader(f"{region_name} - Schritt 1: Sektor-RSL Analyse")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        df_sectors = fetch_sector_rsl(region_code)
        if not df_sectors.empty:
            display_styled_dataframe(df_sectors)
        else:
            st.warning(f"Ladefehler {region_code}-Sektoren.")

    st.subheader(f"{region_name} - Schritt 2: Sektortrend hinterlegen (HH / HT)")
    match_data = df_sectors.copy() if not df_sectors.empty else pd.DataFrame([{"Sektor": k, "Name": v, "RSL Signal": "Neutral"} for k, v in sector_map.items()])
    
    saved_trends = load_trends()
    match_data['T-S (Manuell)'] = match_data['Sektor'].apply(lambda x: saved_trends.get(x, "Neutral"))

    col_edit, col_result = st.columns([1, 1.5])
    with col_edit:
        st.markdown(f"**{region_code} Eingabemaske**")
        edited_df_view = st.data_editor(
            match_data[['Sektor', 'Name', 'T-S (Manuell)']],
            column_config={"T-S (Manuell)": st.column_config.SelectboxColumn("T-S (Manuell)", options=["Long", "Short", "Neutral"], required=True)},
            use_container_width=True, hide_index=True, key=f"editor_{region_code}"
        )

        needs_save = False
        for _, row in edited_df_view.iterrows():
            if saved_trends.get(row['Sektor']) != row['T-S (Manuell)']:
                saved_trends[row['Sektor']] = row['T-S (Manuell)']
                needs_save = True
        if needs_save: save_trends(saved_trends)

    with col_result:
        edited_df = edited_df_view.merge(match_data[['Sektor', 'RSL Signal']], on='Sektor', how='left')
        conditions = [
            (edited_df['RSL Signal'] == 'Long') & (edited_df['T-S (Manuell)'] == 'Long'),
            (edited_df['RSL Signal'] == 'Short') & (edited_df['T-S (Manuell)'] == 'Short')
        ]
        edited_df['Status'] = np.select(conditions, ['Match 🟢', 'Match 🔴'], default='Mismatch ⚠️')
        
        df_matches = edited_df[edited_df['Status'].str.contains('Match')]
        df_mismatches = edited_df[edited_df['Status'] == 'Mismatch ⚠️']
        
        st.markdown(f"##### 🎯 {region_code} Trade-Freigaben")
        if not df_matches.empty: display_styled_dataframe(df_matches[['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']])
        else: st.warning(f"Noch keine perfekten {region_code} Matches gefunden.")
            
        st.markdown(f"##### ❌ {region_code} Unstimmigkeiten")
        display_styled_dataframe(df_mismatches[['Sektor', 'Name', 'RSL Signal', 'T-S (Manuell)', 'Status']])

    st.subheader(f"{region_name} - Schritt 3: Einzelaktien Deep Dive")
    long_matches = edited_df[edited_df['Status'] == 'Match 🟢']['Sektor'].tolist()
    strong_tickers_export = []

    if not long_matches:
        st.info(f"Warte auf bestätigte 'Match 🟢' {region_code} Sektoren aus Schritt 2...")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1: rsl_limit = st.slider(f"Minimale RSL ({region_code})", 1.00, 1.20, 1.05, 0.01, key=f"slider_{region_code}")
        with col_f2:
            st.write("\n")
            apply_ema = st.checkbox(f"Nur Aktien mit frischem EMA5/20 Cross ({region_code})", False, key=f"chk_{region_code}")
        
        for sector in long_matches:
            sector_name = sector_map[sector]
            st.markdown(f"**{region_code} Sektor: {sector_name} ({sector})**")
            
            clean_sector_key = sector.split(".")[0] if is_eu else sector
            raw_tickers = stock_dict.get(clean_sector_key, [])
            tickers_to_check = [f"{t}.DE" for t in raw_tickers] if is_eu else raw_tickers
            
            if tickers_to_check:
                with st.spinner(f"Scanne {region_code} Aktien (vektorisiert)..."):
                    df_stocks = analyze_stocks(tickers_to_check, apply_ema, rsl_limit)
                    if not df_stocks.empty:
                        st.dataframe(df_stocks, use_container_width=True, hide_index=True)
                        export_list = [t.split(".")[0] for t in df_stocks['Ticker'].tolist()] if is_eu else df_stocks['Ticker'].tolist()
                        strong_tickers_export.extend(export_list)
                    else:
                        st.warning(f"Keine Treffer im Sektor {sector_name}.")
                        
    return strong_tickers_export

# =====================================================================
# UI Aufbau Main
# =====================================================================
st.title("🖥️ Sektorfilter Trading nach RSL / HH-HT")

st.markdown("""
<div style="background-color: #ffe6e6; border-left: 5px solid #ff4d4d; padding: 15px; color: #cc0000; border-radius: 5px; margin-bottom: 20px;">
    <strong>⚠️ Haftungsausschluss (Disclaimer):</strong><br>
    Die App dient ausschließlich zu Informations- und Bildungszwecken. Es handelt sich um keine Anlageberatung und keine Aufforderung zum Kauf oder Verkauf von Wertpapieren. Alle Daten sind ohne Gewähr (keine Garantie für Richtigkeit, Vollständigkeit oder Aktualität der Kurse). Jeder Nutzer handelt auf eigenes Risiko.
</div>
""", unsafe_allow_html=True)

st.markdown("**Regelwerk (v7.1):** 4h-Chart Ausführung | 1d-Filterung | 0,5 % Risiko pro Trade")

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
        2. **Trendabgleich (HH/HT):** Das maschinelle RSL-Signal wird in der Eingabemaske manuell mit deiner Chartanalyse (Marktstruktur: Höhere Hochs / Höhere Tiefs) abgeglichen. Nur bei einem **Match** wird der Sektor freigegeben.
        3. **Deep Dive & "Smooth RSL":** Im freigegebenen Sektor sucht das Tool nach den stärksten Einzelaktien.
        """)

with col_info2:
    with st.expander("📊 Datenherkunft & Technik"):
        st.markdown("""
        * **Datenquelle:** Alle Kursdaten werden in Echtzeit via **Yahoo Finance** (`yfinance`) bezogen.
        * **Performance:** Die Analysen erfolgen vollständig vektorisiert, um minimale Ladezeiten zu garantieren.
        * **Speicherung:** Deine manuellen Eingaben aus Schritt 2 werden lokal gespeichert.
        """)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔄 Alle Live-Daten jetzt aktualisieren", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- Tabs für bessere Übersichtlichkeit ---
tab1, tab2 = st.tabs(["📊 Sektor-Analyse (Top-Down)", "🏆 Top 25 (Gesamtmarkt)"])

with tab1:
    # --- Hauptblöcke Rendern ---
    sp500_export = render_market_section("S&P500", "🇺🇸", US_SECTOR_MAP, SP500_AKTIEN, is_eu=False)
    euro_export = render_market_section("EuroStoxx", "🇪🇺", EU_SECTOR_MAP, EUROSTOXX_GETTEX_AKTIEN, is_eu=True)

    # --- TradingView Export ---
    st.markdown("---")
    st.subheader("📺 TradingView Export (Sektor-Matches)")
    st.caption("Kopiere diese Zeilen und füge sie direkt per STRG+V in deine TradingView Watchlists ein.")

    col_tv1, col_tv2 = st.columns(2)
    with col_tv1:
        st.markdown("**🇺🇸 S&P 500 Matches**")
        if sp500_export: st.code(",".join(sp500_export), language="text")
        else: st.info("Keine S&P 500 Ticker zum Exportieren.")
            
    with col_tv2:
        st.markdown("**🇪🇺 EuroStoxx Matches**")
        if euro_export: st.code(",".join(euro_export), language="text")
        else: st.info("Keine EuroStoxx Ticker zum Exportieren.")

with tab2:
    st.header("🏆 Top 25 Gesamtmarkt nach RSL")
    st.markdown("Diese Ansicht ignoriert die Sektoren und filtert stur alle hinterlegten Aktien nach der höchsten Relativen Stärke (RSL).")

    col_top_us, col_top_eu = st.columns(2)

    with col_top_us:
        st.subheader("🇺🇸 S&P 500 Top 25")
        with st.spinner("Scanne S&P 500 Gesamtmarkt..."):
            df_top_us = fetch_top_25_overall(SP500_AKTIEN, is_eu=False)
            
        if not df_top_us.empty:
            st.dataframe(df_top_us[["Ticker", "Kurs", "RSL", "Vola (p.a.)", "Smooth RSL"]], use_container_width=True, hide_index=True)
            st.caption("📺 TradingView Export (US Top 25):")
            st.code(",".join(df_top_us["TV-Ticker"].tolist()), language="text")

    with col_top_eu:
        st.subheader("🇪🇺 EuroStoxx Top 25")
        with st.spinner("Scanne EuroStoxx Gesamtmarkt..."):
            df_top_eu = fetch_top_25_overall(EUROSTOXX_GETTEX_AKTIEN, is_eu=True)
            
        if not df_top_eu.empty:
            st.dataframe(df_top_eu[["Ticker", "Kurs", "RSL", "Vola (p.a.)", "Smooth RSL"]], use_container_width=True, hide_index=True)
            st.caption("📺 TradingView Export (EU Top 25):")
            st.code(",".join(df_top_eu["TV-Ticker"].tolist()), language="text")

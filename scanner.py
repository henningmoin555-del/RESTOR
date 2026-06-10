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
        ema20 = series.ewm(span=20, adjust

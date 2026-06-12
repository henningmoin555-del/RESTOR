import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Konfiguration & Konstanten ---
st.set_page_config(page_title="Sektorfilter Trading nach RSL / HH-HT", page_icon="📈", layout="wide")

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
    "EXV

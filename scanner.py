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
    "XLV": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "DHR", "ABT", "PFE", "AMGN", "ISRG", "SYK", "BSY", "VRTX", "BSX", "ZTS", "CI", "CVS", "GILD", "BDX", "HUM", "MCK", "MTD", "ALGN", "IDXX", "RMD",

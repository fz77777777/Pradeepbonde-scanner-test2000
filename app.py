import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="Stockbee Indian Market Ultra-Scanner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimalist Theme
st.markdown("""
    <style>
    .stButton>button { 
        background-color: #2b5797; 
        color: white; 
        border-radius: 6px; 
        font-weight: bold;
        padding: 0.5rem 2.5rem;
        font-size: 16px;
    }
    .stButton>button:hover { background-color: #1e3f66; color: #ffffff; }
    h1 { color: #111111; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Indian Market: Stockbee EP Mega-Scanner (2000+ Stocks)")
st.markdown("### **Multi-Cap Institutional Momentum Engine (Large, Mid & Small Cap Only | No Microcaps)**")
st.write("---")

# ==========================================
# SIDEBAR CONTROL PANEL
# ==========================================
with st.sidebar:
    st.header("🎯 Strategy Parameters")
    min_gain = st.slider("Minimum Price Gain (%)", min_value=3.0, max_value=15.0, value=5.0, step=0.5)
    vol_multiplier = st.slider("Volume Multiplier (x Volume SMA50)", min_value=1.5, max_value=6.0, value=2.5, step=0.1)
    
    st.write("---")
    st.header("⚙️ Structure & Timeline Filters")
    
    # Dropdown to select the exact structural phase based on Pradeep Bonde strategy
    setup_filter = st.selectbox(
        "Select Setup Structure",
        options=[
            "All Setups Combined",
            "Fresh EP Breakout",
            "Late EP / Consolidation Phase",
            "Pullback (Near 10/20 EMA)"
        ],
        index=0
    )
    
    # Historical timeline dropdown selector
    scan_mode = st.selectbox(
        "Select Scan Execution Date",
        options=[
            "Current (Today's Live/Close)", "1 Day Ago", "2 Days Ago", "3 Days Ago", 
            "4 Days Ago", "5 Days Ago", "6 Days Ago", "7 Days Ago",
            "2 Weeks Ago", "3 Weeks Ago", "1 Month Ago", "2 Months Ago"
        ],
        index=0
    )
    
    # Mapping selection to strict day offsets
    offset_mapping = {
        "Current (Today's Live/Close)": 0, "1 Day Ago": 1, "2 Days Ago": 2, "3 Days Ago": 3,
        "4 Days Ago": 4, "5 Days Ago": 5, "6 Days Ago": 6, "7 Days Ago": 7,
        "2 Weeks Ago": 14, "3 Weeks Ago": 21, "1 Month Ago": 30, "2 Months Ago": 60
    }
    target_offset = offset_mapping[scan_mode]

# ==========================================
# DYNAMIC 2000+ INDIAN TICKER LOADER (BULLETPROOF)
# ==========================================
@st.cache_data(ttl=86400)
def load_indian_mega_universe_clean():
    """Builds a robust pool of 2000+ large, mid, and small cap Indian stocks without relying on strict column cases"""
    base_pool = []
    
    # STEP 1: Load Nifty 500 (Core Base)
    try:
        url_500 = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df_500 = pd.read_csv(url_500)
        
        # Standardize all columns to uppercase
        df_500.columns = [c.upper().strip() for c in df_500.columns]
        symbol_col = 'SYMBOL' if 'SYMBOL' in df_500.columns else df_500.columns[2]
        industry_col = 'INDUSTRY' if 'INDUSTRY' in df_500.columns else df_500.columns[3]
        company_col = 'COMPANY NAME' if 'COMPANY NAME' in df_500.columns else df_500.columns[0]

        for _, row in df_500.iterrows():
            yf_symbol = str(row[symbol_col]).strip() + ".NS"
            base_pool.append({
                'Symbol_YF': yf_symbol,
                'Company Name': row[company_col],
                'Sector': row[industry_col] if pd.notna(row[industry_col]) else 'Core Sector'
            })
    except Exception as e:
        st.warning(f"Nifty 500 parse alert (Using direct stream fallback): {e}")

    # STEP 2: Fetch and merge full NSE Equities List safely to scale to 2000+
    try:
        url_total = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        df_total = pd.read_csv(url_total)
        
        # Standardize columns to uppercase to completely bypass key errors like 'SERIES'
        df_total.columns = [c.upper().strip() for c in df_total.columns]
        
        symbol_col = 'SYMBOL' if 'SYMBOL' in df_total.columns else df_total.columns[0]
        name_col = 'NAME OF COMPANY' if 'NAME OF COMPANY' in df_total.columns else df_total.columns[1]
        series_col = 'SERIES' if 'SERIES' in df_total.columns else (df_total.columns[2] if len(df_total.columns) > 2 else None)
        
        # Filter active standard equities safely
        if series_col and series_col in df_total.columns:
            df_total = df_total[df_total[series_col].astype(str).str.upper().str.strip() == 'EQ']
            
        existing_symbols = {r['Symbol_YF']

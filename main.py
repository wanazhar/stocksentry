import streamlit as st
import yfinance as yf
from utils.stock_data import get_stock_data, get_company_info, save_user_preference, format_number
from utils.visualizations import create_price_chart, create_volume_chart, create_metrics_chart
from utils.database import init_db
import plotly.io as pio

# Initialize database
init_db()

# Set default plotly theme
pio.templates.default = "plotly_dark"

# Page config
st.set_page_config(
    page_title="Stock Analysis Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title and Description
st.title('Stock Analysis Tool 📈')

# Input Section
col1, col2 = st.columns([2, 1])
with col1:
    symbol = st.text_input('Enter Stock Symbol:', value='AAPL', help="""
    Enter stock symbol (examples):
    - US stocks: AAPL, GOOGL, MSFT
    - Hong Kong: 0700.HK, 9988.HK
    - London: BP.L, HSBA.L
    - Tokyo: 7203.T, 6758.T
    - Singapore: D05.SI, Z74.SI
    """).upper()

with col2:
    period = st.selectbox(
        'Select Time Period:',
        ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
    )

# Save user preference when inputs change
if symbol or period:
    save_user_preference(symbol, period)

try:
    # Get data
    df = get_stock_data(symbol, period)
    info = get_company_info(symbol)

    # Company Profile Section
    st.subheader("Company Profile")
    profile_col1, profile_col2 = st.columns([1, 1])

    with profile_col1:
        st.write(f"**Company:** {info['longName']}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Market Cap:** {format_number(info.get('marketCap'), symbol)}")
        st.write(f"**Enterprise Value:** {format_number(info.get('enterpriseValue'), symbol)}")

    with profile_col2:
        st.write("**Current Trading Info**")
        st.write(f"Price: {format_number(info.get('currentPrice'), symbol)}")
        st.write(f"Day Range: {format_number(info.get('dayLow'), symbol)} - {format_number(info.get('dayHigh'), symbol)}")
        st.write(f"52W Range: {format_number(info.get('fiftyTwoWeekLow'), symbol)} - {format_number(info.get('fiftyTwoWeekHigh'), symbol)}")
        st.write(f"Volume: {format_number(info.get('volume'), symbol, False)}")

    # Trading Metrics Section
    st.subheader("Trading Metrics")
    trading_col1, trading_col2, trading_col3 = st.columns(3)

    with trading_col1:
        st.write("**Valuation Ratios**")
        st.write(f"P/E Ratio: {format_number(info.get('trailingPE'), symbol, False)}")
        st.write(f"Forward P/E: {format_number(info.get('forwardPE'), symbol, False)}")
        st.write(f"PEG Ratio: {format_number(info.get('pegRatio'), symbol, False)}")
        st.write(f"Price/Book: {format_number(info.get('priceToBook'), symbol, False)}")

    with trading_col2:
        st.write("**Performance**")
        st.write(f"Beta: {format_number(info.get('beta'), symbol, False)}")
        st.write(f"Year Change: {format_number(info.get('52WeekChange', 0) * 100, symbol, False)}%")
        st.write(f"YTD Return: {format_number(info.get('ytdReturn', 0) * 100, symbol, False)}%")
        st.write(f"Avg Volume: {format_number(info.get('averageVolume'), symbol, False)}")

    with trading_col3:
        st.write("**Dividends & Splits**")
        st.write(f"Dividend Rate: {format_number(info.get('dividendRate', 0), symbol)}")
        st.write(f"Dividend Yield: {format_number(info.get('dividendYield', 0) * 100, symbol, False)}%")
        st.write(f"Ex-Dividend Date: {info.get('exDividendDate', 'N/A')}")
        st.write(f"Last Split: {info.get('lastSplitDate', 'N/A')}")

    # Charts Section (Collapsible)
    with st.expander("📊 Price Analysis", expanded=False):
        st.plotly_chart(
            create_price_chart(df, symbol),
            use_container_width=True
        )

    with st.expander("📈 Volume Analysis", expanded=False):
        st.plotly_chart(
            create_volume_chart(df),
            use_container_width=True
        )

    with st.expander("📉 Financial Metrics", expanded=False):
        st.plotly_chart(
            create_metrics_chart(info),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check the stock symbol and try again.")

# Footer
st.markdown("""
---
<div style='text-align: center; color: #666;'>
    vibecoded by wanazhar on replit
</div>
""", unsafe_allow_html=True)
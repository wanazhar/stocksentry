import streamlit as st
import yfinance as yf
from utils.stock_data import get_stock_data, get_company_info, save_user_preference
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

    with profile_col2:
        metrics = {
            "Market Cap": info.get('marketCap', 'N/A'),
            "P/E Ratio": info.get('trailingPE', 'N/A'),
            "52W High/Low": f"{info.get('fiftyTwoWeekHigh', 'N/A')}/{info.get('fiftyTwoWeekLow', 'N/A')}"
        }
        for key, value in metrics.items():
            st.metric(key, value)

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
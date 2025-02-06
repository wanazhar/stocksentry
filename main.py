import streamlit as st
import yfinance as yf
from utils.stock_data import get_stock_data, get_company_info
from utils.visualizations import create_price_chart, create_volume_chart, create_metrics_chart
import plotly.io as pio

# Set default plotly theme
pio.templates.default = "plotly_dark"

# Page config
st.set_page_config(
    page_title="Stock Analysis Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title('Stock Analysis Tool')
symbol = st.sidebar.text_input('Enter Stock Symbol:', value='AAPL').upper()
period = st.sidebar.selectbox(
    'Select Time Period:',
    ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
)

try:
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title(f"{symbol} Stock Analysis")
        
        # Get stock data
        df = get_stock_data(symbol, period)
        info = get_company_info(symbol)
        
        # Price chart
        st.plotly_chart(
            create_price_chart(df, symbol),
            use_container_width=True
        )
        
        # Volume chart
        st.plotly_chart(
            create_volume_chart(df),
            use_container_width=True
        )
    
    with col2:
        # Company info
        st.subheader("Company Information")
        st.write(f"**Company:** {info['longName']}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        
        # Key metrics
        st.subheader("Key Metrics")
        metrics = {
            "Market Cap": info.get('marketCap', 'N/A'),
            "P/E Ratio": info.get('trailingPE', 'N/A'),
            "52 Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52 Week Low": info.get('fiftyTwoWeekLow', 'N/A'),
            "Volume": info.get('volume', 'N/A'),
            "Avg Volume": info.get('averageVolume', 'N/A')
        }
        
        for key, value in metrics.items():
            st.metric(key, value)
        
        # Financial indicators chart
        st.plotly_chart(
            create_metrics_chart(info),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check the stock symbol and try again.")

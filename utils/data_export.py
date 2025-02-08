import pandas as pd
import plotly.io as pio
import io
from datetime import datetime
import yfinance as yf
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import base64

def export_to_excel(symbol: str, df: pd.DataFrame, info: dict, figures: list) -> io.BytesIO:
    """
    Export stock data, metrics, and charts to Excel
    """
    output = io.BytesIO()
    
    # Create Excel writer
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Write price data
    df.to_excel(writer, sheet_name='Historical Data', index=True)
    
    # Write company metrics
    metrics_df = pd.DataFrame({
        'Metric': [
            'Market Cap', 'Enterprise Value', 'P/E Ratio', 'Forward P/E',
            'PEG Ratio', 'Price/Book', 'EV/EBITDA', 'EV/Revenue',
            'Profit Margin', 'Operating Margin', 'ROE', 'ROA'
        ],
        'Value': [
            info.get('marketCap'), info.get('enterpriseValue'),
            info.get('trailingPE'), info.get('forwardPE'),
            info.get('pegRatio'), info.get('priceToBook'),
            info.get('enterpriseToEbitda'), info.get('enterpriseToRevenue'),
            info.get('profitMargins'), info.get('operatingMargins'),
            info.get('returnOnEquity'), info.get('returnOnAssets')
        ]
    })
    metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
    
    # Save and convert charts to images
    for i, fig in enumerate(figures):
        img_bytes = fig.to_image(format="png")
        writer.sheets[f'Chart_{i+1}'] = writer.book.create_sheet(f'Chart_{i+1}')
        img = Image(io.BytesIO(img_bytes))
        writer.sheets[f'Chart_{i+1}'].add_image(img, 'A1')
    
    writer.close()
    output.seek(0)
    return output

def get_historical_data(symbols: list, start_date: str, end_date: str) -> dict:
    """
    Fetch historical data for multiple symbols within a date range
    """
    data = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            data[symbol] = df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            continue
    return data

def get_peer_comparison(symbol: str) -> tuple:
    """
    Get peer comparison data
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        peers = info.get('recommendationKey', [])
        
        # Get data for peers
        peer_data = {}
        for peer in peers:
            peer_stock = yf.Ticker(peer)
            peer_data[peer] = peer_stock.info
            
        return peers, peer_data
    except Exception as e:
        print(f"Error fetching peer data: {str(e)}")
        return [], {}

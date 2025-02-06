import yfinance as yf
import pandas as pd

def get_stock_data(symbol: str, period: str) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch stock data: {str(e)}")

def get_company_info(symbol: str) -> dict:
    """
    Fetch company information from Yahoo Finance
    """
    try:
        stock = yf.Ticker(symbol)
        return stock.info
    except Exception as e:
        raise Exception(f"Failed to fetch company information: {str(e)}")

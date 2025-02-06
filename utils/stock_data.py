import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .database import get_session, StockData, UserPreference

def get_stock_data(symbol: str, period: str) -> pd.DataFrame:
    """
    Fetch stock data from database cache or Yahoo Finance
    """
    try:
        session = get_session()

        # Check cache first
        latest_data = session.query(StockData)\
            .filter(StockData.symbol == symbol)\
            .order_by(StockData.date.desc())\
            .first()

        if latest_data and (datetime.utcnow() - latest_data.created_at) < timedelta(hours=1):
            # Return cached data if less than 1 hour old
            data = session.query(StockData)\
                .filter(StockData.symbol == symbol)\
                .order_by(StockData.date.asc())\
                .all()

            df = pd.DataFrame([{
                'Open': d.open_price,
                'High': d.high_price,
                'Low': d.low_price,
                'Close': d.close_price,
                'Volume': d.volume,
                'Date': d.date
            } for d in data])
            df.set_index('Date', inplace=True)
            return df

        # Fetch new data from Yahoo Finance
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)

        # Cache the data
        for index, row in df.iterrows():
            stock_data = StockData(
                symbol=symbol,
                date=index,
                open_price=row['Open'],
                high_price=row['High'],
                low_price=row['Low'],
                close_price=row['Close'],
                volume=row['Volume']
            )
            session.add(stock_data)

        session.commit()
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

def save_user_preference(symbol: str, period: str):
    """
    Save user's stock symbol and period preference
    """
    try:
        session = get_session()
        pref = UserPreference(symbol=symbol, period=period)
        session.add(pref)
        session.commit()
    except Exception as e:
        print(f"Failed to save preference: {str(e)}")
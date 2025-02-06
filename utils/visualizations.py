import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_price_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive price chart with candlesticks and moving averages
    """
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        )
    )
    
    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'].rolling(window=20).mean(),
            name='20 Day MA',
            line=dict(color='orange')
        )
    )
    
    fig.update_layout(
        title=f'{symbol} Stock Price',
        yaxis_title='Price',
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_volume_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create volume chart
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color='rgba(255, 75, 75, 0.7)'
        )
    )
    
    fig.update_layout(
        title='Trading Volume',
        yaxis_title='Volume',
        template='plotly_dark'
    )
    
    return fig

def create_metrics_chart(info: dict) -> go.Figure:
    """
    Create a chart for financial metrics
    """
    metrics = {
        'Forward P/E': info.get('forwardPE', 0),
        'PEG Ratio': info.get('pegRatio', 0),
        'Price to Book': info.get('priceToBook', 0),
        'Profit Margin': info.get('profitMargin', 0) * 100 if info.get('profitMargin') else 0
    }
    
    fig = go.Figure([
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color='rgba(75, 192, 192, 0.7)'
        )
    ])
    
    fig.update_layout(
        title='Key Financial Metrics',
        template='plotly_dark',
        showlegend=False
    )
    
    return fig

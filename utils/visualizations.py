import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import ta

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

def create_technical_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an advanced technical analysis chart with multiple indicators
    """
    # Calculate technical indicators using ta library
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Middle'] = bollinger.bollinger_mavg()
    df['BB_Lower'] = bollinger.bollinger_lband()
    
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.2, 0.15, 0.15]
    )
    
    # Main price chart with candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )
    
    # Add EMAs
    fig.add_trace(
        go.Scatter(x=df.index, y=df['EMA20'], name='EMA20', line=dict(color='orange')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['EMA50'], name='EMA50', line=dict(color='blue')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['EMA200'], name='EMA200', line=dict(color='red')),
        row=1, col=1
    )
    
    # Add Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                  line=dict(color='gray', dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                  line=dict(color='gray', dash='dash'),
                  fill='tonexty'),
        row=1, col=1
    )
    
    # Volume chart
    colors = ['red' if row['Open'] > row['Close'] else 'green' 
              for index, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume',
               marker_color=colors),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                  line=dict(color='purple')),
        row=3, col=1
    )
    # Add RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                  line=dict(color='blue')),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal',
                  line=dict(color='orange')),
        row=4, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD Hist',
               marker_color='gray'),
        row=4, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        template='plotly_dark',
        showlegend=True,
        height=1000,
        xaxis_rangeslider_visible=False
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    
    return fig

def create_advanced_metrics_chart(info: dict) -> go.Figure:
    """
    Create advanced metrics visualization with scoring system
    """
    scores = calculate_composite_scores(info)
    
    fig = go.Figure()
    
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Create radar chart
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Company Metrics'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title='Company Performance Metrics',
        template='plotly_dark'
    )
    
    return fig

def calculate_composite_scores(info: dict) -> Dict[str, float]:
    """
    Calculate composite scores for different aspects of the company
    """
    scores = {}
    
    # Valuation Score
    valuation_metrics = {
        'P/E Ratio': (info.get('trailingPE', 0), 0, 50, True),
        'Forward P/E': (info.get('forwardPE', 0), 0, 30, True),
        'PEG Ratio': (info.get('pegRatio', 0), 0, 3, True),
        'Price/Book': (info.get('priceToBook', 0), 0, 5, True)
    }
    
    scores['Valuation'] = np.mean([
        score_metric(val, min_val, max_val, inverse)
        for (val, min_val, max_val, inverse) in valuation_metrics.values()
        if val is not None and val > 0
    ])
    
    # Growth Score
    growth_metrics = {
        'Revenue Growth': (info.get('revenueGrowth', 0) * 100, -20, 50, False),
        'Earnings Growth': (info.get('earningsGrowth', 0) * 100, -30, 100, False)
    }
    
    scores['Growth'] = np.mean([
        score_metric(val, min_val, max_val, inverse)
        for (val, min_val, max_val, inverse) in growth_metrics.values()
        if val is not None
    ])
    
    # Profitability Score
    profitability_metrics = {
        'Operating Margin': (info.get('operatingMargins', 0) * 100, 0, 40, False),
        'Profit Margin': (info.get('profitMargins', 0) * 100, 0, 30, False),
        'ROE': (info.get('returnOnEquity', 0) * 100, 0, 25, False),
        'ROA': (info.get('returnOnAssets', 0) * 100, 0, 15, False)
    }
    
    scores['Profitability'] = np.mean([
        score_metric(val, min_val, max_val, inverse)
        for (val, min_val, max_val, inverse) in profitability_metrics.values()
        if val is not None
    ])
    
    # Financial Health Score
    health_metrics = {
        'Current Ratio': (info.get('currentRatio', 0), 0.5, 3, False),
        'Quick Ratio': (info.get('quickRatio', 0), 0.5, 2, False),
        'Debt/Equity': (info.get('debtToEquity', 0), 0, 200, True)
    }
    
    scores['Financial Health'] = np.mean([
        score_metric(val, min_val, max_val, inverse)
        for (val, min_val, max_val, inverse) in health_metrics.values()
        if val is not None and val > 0
    ])
    
    return scores

def score_metric(value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
    """
    Convert a metric to a score between 0 and 100
    """
    if value is None or max_val <= min_val:
        return 50  # Return neutral score for invalid inputs
    
    # Clip value to range
    value = np.clip(value, min_val, max_val)
    
    # Calculate score (0-100)
    score = ((value - min_val) / (max_val - min_val)) * 100
    
    # Inverse score if needed (higher raw value = lower score)
    if inverse:
        score = 100 - score
        
    return score

def create_peer_comparison_chart(peers_data: Dict[str, dict], metric: str, is_percentage: bool = False) -> go.Figure:
    """
    Create an advanced peer comparison chart with statistical analysis
    """
    # Extract metric values
    values = []
    labels = []
    
    for symbol, data in peers_data.items():
        value = data.get(metric)
        if value is not None:
            if is_percentage and not isinstance(value, str):
                value *= 100
            values.append(value)
            labels.append(symbol)
    
    if not values:
        return None
    
    # Calculate statistics
    mean_val = np.mean(values)
    std_val = np.std(values)
    median_val = np.median(values)
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            name=metric,
            marker_color='rgba(75, 192, 192, 0.7)'
        ),
        secondary_y=False
    )
    
    # Add mean and standard deviation lines
    fig.add_hline(y=mean_val, line_dash="dash", line_color="red",
                 annotation_text=f"Mean: {mean_val:.2f}")
    fig.add_hline(y=median_val, line_dash="dash", line_color="green",
                 annotation_text=f"Median: {median_val:.2f}")
    
    # Update layout
    title_suffix = " (%)" if is_percentage else ""
    fig.update_layout(
        title=f'Peer Comparison: {metric}{title_suffix}',
        template='plotly_dark',
        showlegend=True,
        xaxis_title="Companies",
        yaxis_title=f"{metric}{title_suffix}"
    )
    
    return fig

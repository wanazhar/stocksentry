import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import talib

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
    # Calculate technical indicators
    df['EMA20'] = talib.EMA(df['Close'], timeperiod=20)
    df['EMA50'] = talib.EMA(df['Close'], timeperiod=50)
    df['EMA200'] = talib.EMA(df['Close'], timeperiod=200)
    
    # RSI
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    
    # MACD
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(
        df['Close'], fastperiod=12, slowperiod=26, signalperiod=9
    )
    
    # Bollinger Bands
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(
        df['Close'], timeperiod=20
    )
    
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
        height=1000,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)
    
    return fig

def create_advanced_metrics_chart(info: dict) -> Tuple[go.Figure, Dict]:
    """
    Create advanced metrics visualization with scoring system
    """
    # Calculate composite scores
    scores = calculate_composite_scores(info)
    
    # Create radar chart
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    
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
        title="Company Metrics Scorecard",
        template='plotly_dark'
    )
    
    return fig, scores

def calculate_composite_scores(info: dict) -> Dict[str, float]:
    """
    Calculate composite scores for different aspects of the company
    """
    scores = {}
    
    # Valuation Score
    pe_score = score_metric(info.get('trailingPE', 0), 0, 50, inverse=True)
    pb_score = score_metric(info.get('priceToBook', 0), 0, 10, inverse=True)
    peg_score = score_metric(info.get('pegRatio', 0), 0, 3, inverse=True)
    scores['Valuation'] = (pe_score + pb_score + peg_score) / 3
    
    # Growth Score
    rev_growth = info.get('revenueGrowth', 0) * 100
    earnings_growth = info.get('earningsGrowth', 0) * 100
    scores['Growth'] = (
        score_metric(rev_growth, -20, 50) +
        score_metric(earnings_growth, -30, 70)
    ) / 2
    
    # Profitability Score
    profit_margin = info.get('profitMargins', 0) * 100
    roe = info.get('returnOnEquity', 0) * 100
    scores['Profitability'] = (
        score_metric(profit_margin, 0, 30) +
        score_metric(roe, 0, 25)
    ) / 2
    
    # Financial Health Score
    current_ratio = info.get('currentRatio', 0)
    debt_to_equity = info.get('debtToEquity', 0)
    scores['Financial Health'] = (
        score_metric(current_ratio, 0.5, 3) +
        score_metric(debt_to_equity, 0, 200, inverse=True)
    ) / 2
    
    # Dividend Score
    dividend_yield = info.get('dividendYield', 0) * 100
    payout_ratio = info.get('payoutRatio', 0) * 100
    scores['Dividend'] = (
        score_metric(dividend_yield, 0, 6) +
        score_metric(payout_ratio, 0, 75)
    ) / 2
    
    return scores

def score_metric(value: float, min_val: float, max_val: float, inverse: bool = False) -> float:
    """
    Convert a metric to a score between 0 and 100
    """
    if not value or np.isnan(value):
        return 0
    
    score = (value - min_val) / (max_val - min_val) * 100
    score = max(0, min(100, score))
    
    if inverse:
        score = 100 - score
    
    return score

def create_peer_comparison_chart(peers_data: Dict[str, dict], 
                               metric: str,
                               is_percentage: bool = False) -> go.Figure:
    """
    Create an advanced peer comparison chart with statistical analysis
    """
    values = []
    names = []
    
    for symbol, data in peers_data.items():
        val = data.get(metric, 0)
        if is_percentage:
            val *= 100
        values.append(val)
        names.append(symbol)
    
    # Calculate statistics
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=names,
            y=values,
            name='Values',
            text=[f'{v:.2f}' for v in values],
            textposition='auto',
        )
    )
    
    # Add mean line
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(names) - 0.5,
        y0=mean_val,
        y1=mean_val,
        line=dict(
            color='red',
            width=2,
            dash='dash'
        )
    )
    
    # Add standard deviation bands
    fig.add_shape(
        type='rect',
        x0=-0.5,
        x1=len(names) - 0.5,
        y0=mean_val - std_val,
        y1=mean_val + std_val,
        fillcolor='rgba(255,0,0,0.1)',
        line=dict(width=0)
    )
    
    fig.update_layout(
        title=f'{metric} Comparison',
        template='plotly_dark',
        height=400,
        showlegend=False,
        annotations=[
            dict(
                x=len(names)/2,
                y=mean_val,
                xanchor='center',
                yanchor='bottom',
                text=f'Mean: {mean_val:.2f}',
                showarrow=False,
                font=dict(color='red')
            )
        ]
    )
    
    return fig

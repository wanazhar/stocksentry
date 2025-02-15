import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import MinMaxScaler
from textblob import TextBlob
import requests
from datetime import datetime, timedelta
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from bs4 import BeautifulSoup
from .technical_analysis import calculate_ichimoku_cloud  # Add interface import

# ESG analysis moved to esg_analysis.py
# Market analysis and ML prediction remain here

# Enhanced risk disclosure
print('Investments carry inherent risks including potential loss of principal.')
print('Investments may lose value. Consult a financial advisor before making decisions.')

class RiskAnalyzer:
    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive risk metrics
        """
        returns = df['Close'].pct_change()
        
        metrics = {
            'volatility': returns.std() * np.sqrt(252),  # Annualized volatility
            'var_95': self._calculate_var(returns, 0.95),
            'cvar_95': self._calculate_cvar(returns, 0.95),
            'max_drawdown': self._calculate_max_drawdown(df['Close']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'sortino_ratio': self._calculate_sortino_ratio(returns),
            'beta': self._calculate_beta(returns)
        }
        
        return metrics
    
    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk"""
        return abs(np.percentile(returns, (1 - confidence) * 100))
    
    def _calculate_cvar(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence)
        return abs(returns[returns <= -var].mean())
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        rolling_max = prices.expanding().max()
        drawdowns = prices / rolling_max - 1
        return abs(drawdowns.min())
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe Ratio"""
        rf_rate = 0.02  # Assume 2% risk-free rate
        excess_returns = returns - rf_rate/252
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino Ratio"""
        rf_rate = 0.02
        excess_returns = returns - rf_rate/252
        downside_returns = returns[returns < 0]
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()
    
    def _calculate_beta(self, returns: pd.Series) -> float:
        """Calculate Beta relative to S&P 500"""
        spy = yf.download('^GSPC', start=returns.index[0], end=returns.index[-1])['Close'].pct_change()
        return np.cov(returns, spy)[0][1] / np.var(spy) 
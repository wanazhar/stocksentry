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

class ESGAnalyzer:
    def __init__(self):
        self.esg_metrics = {
            'environmental': [
                'carbonEmissions',
                'waterUsage',
                'energyEfficiency',
                'renewableEnergy',
                'wasteManagement'
            ],
            'social': [
                'employeeSatisfaction',
                'diversityScore',
                'communityRelations',
                'humanRights',
                'laborPractices'
            ],
            'governance': [
                'boardDiversity',
                'executiveCompensation',
                'shareholderRights',
                'businessEthics',
                'transparencyScore'
            ]
        }
    
    def get_esg_data(self, symbol: str) -> Dict:
        """
        Fetch ESG data from multiple sources and combine them
        """
        try:
            # Yahoo Finance ESG data
            stock = yf.Ticker(symbol)
            yahoo_esg = stock.sustainability
            
            # Additional ESG data sources could be added here
            # Example: CDP, MSCI, Sustainalytics
            
            # Combine and normalize ESG scores
            esg_scores = self._normalize_esg_scores(yahoo_esg)
            
            # Add ESG news sentiment
            esg_scores['sentiment'] = self._get_esg_sentiment(symbol)
            
            return esg_scores
        except Exception as e:
            print(f"Error fetching ESG data: {str(e)}")
            return {}
    
    def _normalize_esg_scores(self, raw_scores: pd.DataFrame) -> Dict:
        """
        Normalize ESG scores to a 0-100 scale
        """
        if raw_scores is None:
            return {}
        
        normalized = {}
        scaler = MinMaxScaler(feature_range=(0, 100))
        
        for category in self.esg_metrics.keys():
            if category in raw_scores.index:
                normalized[category] = float(scaler.fit_transform([[raw_scores.loc[category].Value]])[0][0])
        
        # Calculate overall ESG score
        if normalized:
            normalized['overall'] = sum(normalized.values()) / len(normalized)
        
        return normalized
    
    def _get_esg_sentiment(self, symbol: str) -> float:
        """
        Analyze news sentiment for ESG-related news
        """
        try:
            # Get news articles related to company's ESG
            news = self._fetch_esg_news(symbol)
            
            # Analyze sentiment
            sentiments = []
            for article in news:
                blob = TextBlob(article['title'] + ' ' + article['description'])
                sentiments.append(blob.sentiment.polarity)
            
            return np.mean(sentiments) if sentiments else 0
        except:
            return 0
    
    def _fetch_esg_news(self, symbol: str) -> List[Dict]:
        """
        Fetch ESG-related news for the company
        """
        # Implementation would depend on news API service
        # Example using a hypothetical news API
        return []

class MarketAnalyzer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    def predict_trend(self, df: pd.DataFrame, days_ahead: int = 30) -> Tuple[np.ndarray, float]:
        """
        Predict price trend using machine learning
        """
        # Prepare features
        df = self._prepare_features(df)
        
        # Split data
        X = df.drop(['Close'], axis=1)
        y = df['Close']
        
        # Train model
        self.model.fit(X[:-days_ahead], y[:-days_ahead])
        
        # Make prediction
        predictions = self.model.predict(X[-days_ahead:])
        confidence = self.model.score(X[-days_ahead:], y[-days_ahead:])
        
        return predictions, confidence
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare technical indicators as features
        """
        df = df.copy()
        
        # Technical indicators
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = self._calculate_rsi(df['Close'])
        df['MACD'] = self._calculate_macd(df['Close'])
        df['BB_upper'], df['BB_middle'], df['BB_lower'] = self._calculate_bollinger_bands(df['Close'])
        
        # Volume indicators
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        
        # Price momentum
        df['Price_Momentum'] = df['Close'].pct_change()
        df['Price_Acceleration'] = df['Price_Momentum'].pct_change()
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> pd.Series:
        """Calculate MACD"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        return exp1 - exp2
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        return upper, middle, lower

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
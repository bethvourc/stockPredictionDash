import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Tuple, Dict, Any
import pandas_market_calendars as mcal
from sklearn.metrics import mean_absolute_percentage_error
import logging

logger = logging.getLogger(__name__)

class StockService:
    @staticmethod
    async def search_stocks(query: str, limit: int = 10):
        """Search stocks by symbol or company name"""
        sp500_service = SP500Service()
        companies = await sp500_service.get_sp500_companies()
        
        # Search by symbol or company name
        results = [
            company for company in companies
            if query.upper() in company['symbol'].upper() or 
               query.upper() in company['name'].upper()
        ]
        
        return results[:limit]

    @staticmethod
    async def add_technical_indicators(data: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """Add requested technical indicators to the dataset"""
        for indicator in indicators:
            if indicator == 'SMA_50':
                data['SMA_50'] = data['Close'].rolling(window=50).mean()
            elif indicator == 'SMA_200':
                data['SMA_200'] = data['Close'].rolling(window=200).mean()
            elif indicator == 'RSI':
                data['RSI'] = StockService._calculate_rsi(data['Close'])
            elif indicator == 'MACD':
                data = StockService._calculate_macd(data)
            elif indicator == 'BB':  # Bollinger Bands
                data = StockService._calculate_bollinger_bands(data)
        return data

    @staticmethod
    def _calculate_bollinger_bands(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        sma = data['Close'].rolling(window=window).mean()
        std = data['Close'].rolling(window=window).std()
        data['BB_upper'] = sma + (std * 2)
        data['BB_middle'] = sma
        data['BB_lower'] = sma - (std * 2)
        return data

    @staticmethod
    def _calculate_macd(data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class StockData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    sma_50: Optional[float]
    sma_200: Optional[float]
    rsi: Optional[float]
    volatility: Optional[float]

class ForecastData(BaseModel):
    date: datetime
    predicted_price: float
    lower_bound: float
    upper_bound: float

class CompanyInfo(BaseModel):
    name: str
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    fifty_two_week_low: Optional[float]
    fifty_two_week_high: Optional[float]

class ForecastRequest(BaseModel):
    ticker: str
    years: int = 1
    confidence_interval: int = 90

class ForecastResponse(BaseModel):
    forecast: List[Dict[str, Any]]
    metrics: Dict[str, float]

class StockDataResponse(BaseModel):
    data: List[Dict[str, Any]]
    info: Dict[str, Any]
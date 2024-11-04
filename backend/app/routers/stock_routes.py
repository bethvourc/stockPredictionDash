from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..services.stock_service import StockService
from ..services.prediction_service import PredictionService

router = APIRouter()

@router.get("/search")
async def search_stocks(query: str, limit: int = 10):
    """Search stocks by symbol or company name"""
    try:
        stocks = await StockService.search_stocks(query, limit)
        return {"results": stocks}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/stock/{ticker}")
async def get_stock_data(
    ticker: str,
    period: Optional[str] = "1y",
    indicators: Optional[List[str]] = Query(None)
):
    """Get stock data with optional technical indicators"""
    try:
        data, info = await StockService.get_stock_data(ticker, period)
        if indicators:
            data = await StockService.add_technical_indicators(data, indicators)
        return {
            "data": data.to_dict(orient="records"),
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

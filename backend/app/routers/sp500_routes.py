from fastapi import APIRouter, BackgroundTasks
from ..services.sp500_service import SP500Service
from typing import Optional

router = APIRouter()
sp500_service = SP500Service()

@router.get("/companies")
async def get_companies():
    """Get all S&P 500 companies"""
    return await sp500_service.get_sp500_companies()

@router.get("/sectors")
async def get_sector_performance():
    """Get sector-wise performance"""
    return await sp500_service.get_sector_performance()

@router.get("/top-performers")
async def get_top_performers(timeframe: Optional[str] = 'daily'):
    """Get top performing stocks"""
    return await sp500_service.get_top_performers(timeframe)

@router.post("/update-data")
async def update_stock_data(background_tasks: BackgroundTasks):
    """Trigger stock data update"""
    await sp500_service.update_stock_data(background_tasks)
    return {"message": "Stock data update initiated"}
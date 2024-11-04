from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .routers import stock_routes, sp500_routes
from .services.sp500_service import SP500Service
import asyncio

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stock_routes.router, prefix="/api/stocks")
app.include_router(sp500_routes.router, prefix="/api/sp500")

# Initialize SP500 service on startup
@app.on_event("startup")
async def startup_event():
    sp500_service = SP500Service()
    # Initialize cache on startup
    await sp500_service.get_sp500_companies()
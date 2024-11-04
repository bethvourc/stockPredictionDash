import pandas as pd
import numpy as np
from prophet import Prophet
import pandas_market_calendars as mcal
from sklearn.metrics import mean_absolute_percentage_error
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    @staticmethod
    def generate_forecast(data: pd.DataFrame, period: int, confidence_interval: float) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Generate forecast and performance metrics"""
        try:
            # Prepare data for Prophet
            prophet_data = data[['Date', 'Close']].copy()
            prophet_data.columns = ['ds', 'y']

            # Initialize and configure Prophet model
            model = Prophet(
                changepoint_prior_scale=0.05,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                interval_width=confidence_interval/100
            )
            
            # Add market calendar holidays
            nyse = mcal.get_calendar('NYSE')
            holidays = nyse.holidays().holidays
            holiday_df = pd.DataFrame({
                'holiday': 'market_holiday',
                'ds': pd.to_datetime(holidays)
            })
            model.add_country_holidays(country_name='US')
            model.add_holidays(holiday_df)
            
            # Fit model and generate forecast
            model.fit(prophet_data)
            future = model.make_future_dataframe(periods=period)
            forecast = model.predict(future)
            
            # Calculate performance metrics
            metrics = PredictionService._calculate_metrics(
                prophet_data['y'].values,
                forecast['yhat'][:len(prophet_data)]
            )
            
            return forecast, metrics
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            raise

    @staticmethod
    def _calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate model performance metrics"""
        mape = mean_absolute_percentage_error(y_true, y_pred)
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        r2 = 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))
        
        return {
            'mape': mape,
            'rmse': rmse,
            'r2': r2
        }
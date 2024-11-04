# part1_core.py

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
import exchange_calendars as xcals
import ta
import warnings
import base64
import io
warnings.filterwarnings('ignore')

# Constants
SP500_TICKERS = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

class EnhancedEnsemblePredictor:
    def __init__(self, confidence_interval=0.9):
        self.sarima_model = None
        self.lgb_model = None
        self.catboost_model = None
        self.scaler = MinMaxScaler()
        self.confidence_interval = confidence_interval
        self.feature_columns = None
    
    def prepare_data(self, data, forecast_period):
        df = create_advanced_features(data)
        df = df.dropna()
        
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_columns]
        y = df['Close']
        
        X_scaled = self.scaler.fit_transform(X)
        return df, X_scaled, y
    
    def train_sarima(self, data):
        model = SARIMAX(
            data['Close'],
            order=(2, 1, 2),
            seasonal_order=(1, 1, 1, 5),
            enforce_stationarity=False
        )
        self.sarima_model = model.fit(disp=False)
    
    def train_lightgbm(self, X, y):
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'n_estimators': 200,
            'importance_type': 'gain'
        }
        self.lgb_model = lgb.LGBMRegressor(**params)
        self.lgb_model.fit(X, y)
    
    def train_catboost(self, X, y):
        params = {
            'iterations': 200,
            'learning_rate': 0.05,
            'depth': 6,
            'l2_leaf_reg': 3,
            'loss_function': 'RMSE',
            'verbose': False
        }
        self.catboost_model = CatBoostRegressor(**params)
        self.catboost_model.fit(X, y)
    
    def forecast(self, data, forecast_period):
        sarima_forecast = self.sarima_model.forecast(steps=forecast_period)
        
        last_data = data.copy()
        lgb_predictions = []
        catboost_predictions = []
        
        for _ in range(forecast_period):
            features = create_advanced_features(last_data)
            features = features.dropna()
            X = features[self.feature_columns].iloc[-1:]
            X_scaled = self.scaler.transform(X)
            
            lgb_pred = self.lgb_model.predict(X_scaled)[0]
            catboost_pred = self.catboost_model.predict(X_scaled)[0]
            
            lgb_predictions.append(lgb_pred)
            catboost_predictions.append(catboost_pred)
            
            new_row = last_data.iloc[-1:].copy()
            new_row.index = [new_row.index[-1] + pd.Timedelta(days=1)]
            new_row['Close'] = (lgb_pred + catboost_pred) / 2
            last_data = pd.concat([last_data, new_row])
        
        lgb_weight = 0.35
        catboost_weight = 0.35
        sarima_weight = 0.30
        
        ensemble_forecast = (
            sarima_weight * sarima_forecast +
            lgb_weight * np.array(lgb_predictions) +
            catboost_weight * np.array(catboost_predictions)
        )
        
        predictions = np.column_stack([
            sarima_forecast,
            lgb_predictions,
            catboost_predictions
        ])
        
        bootstrap_predictions = []
        for _ in range(1000):
            weights = np.random.dirichlet([3, 3, 3])
            bootstrap_predictions.append(np.average(predictions, axis=1, weights=weights))
        
        bootstrap_predictions = np.array(bootstrap_predictions)
        lower_percentile = (100 - self.confidence_interval * 100) / 2
        upper_percentile = 100 - lower_percentile
        
        forecast_df = pd.DataFrame({
            'ds': pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), 
                              periods=forecast_period),
            'yhat': ensemble_forecast,
            'yhat_lower': np.percentile(bootstrap_predictions, lower_percentile, axis=0),
            'yhat_upper': np.percentile(bootstrap_predictions, upper_percentile, axis=0)
        })
        
        return forecast_df

def create_advanced_features(data):
    df = data.copy()
    
    # Add all momentum indicators
    df_momentum = ta.add_momentum_ta(
        df, high="High", low="Low", close="Close", volume="Volume", fillna=True
    )
    
    # Add all volatility indicators
    df_volatility = ta.add_volatility_ta(
        df, high="High", low="Low", close="Close", fillna=True
    )
    
    # Add all trend indicators
    df_trend = ta.add_trend_ta(
        df, high="High", low="Low", close="Close", fillna=True
    )
    
    # Add all volume indicators
    df_volume = ta.add_volume_ta(
        df, high="High", low="Low", close="Close", volume="Volume", fillna=True
    )
    
    # Add custom features
    df['returns'] = df['Close'].pct_change()
    df['log_returns'] = np.log1p(df['returns'])
    
    for window in [5, 10, 20, 50, 200]:
        df[f'ma_{window}'] = df['Close'].rolling(window=window).mean()
        df[f'std_{window}'] = df['Close'].rolling(window=window).std()
        df[f'max_{window}'] = df['Close'].rolling(window=window).max()
        df[f'min_{window}'] = df['Close'].rolling(window=window).min()
        df[f'channel_width_{window}'] = df[f'max_{window}'] - df[f'min_{window}']
        df[f'position_in_channel_{window}'] = (df['Close'] - df[f'min_{window}']) / (df[f'max_{window}'] - df[f'min_{window}'])
    
    # Market calendar features
    nyse = xcals.get_calendar('NYSE')
    df['is_month_end'] = df.index.is_month_end.astype(int)
    df['is_month_start'] = df.index.is_month_start.astype(int)
    df['day_of_week'] = df.index.dayofweek
    df['day_of_month'] = df.index.day
    df['month'] = df.index.month
    
    return df

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        
        # Add technical indicators
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        data['Volatility'] = data['Close'].rolling(window=20).std()
        data['RSI'] = calculate_rsi(data['Close'])
        
        # Add trading volume analysis
        data['Volume_MA'] = data['Volume'].rolling(window=20).mean()
        data['Volume_StD'] = data['Volume'].rolling(window=20).std()
        
        return data
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
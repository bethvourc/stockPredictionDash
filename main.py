import streamlit as st
from datetime import date
import time
import yfinance as yf
import plotly.graph_objs as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import numpy as np

# Date time frame for data
START = "2015-01-01" 
TODAY = date.today().strftime("%Y-%m-%d")

st.title("Stock Prediction App")

stocks = ("AAPL", "GOOG", "MSFT", "GME")
selected_stocks = st.selectbox("Select dataset for prediction ", stocks)
n_years = st.slider("Years of prediction:", 1, 4)
period = n_years * 365

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Load data...")
data = load_data(selected_stocks)
time.sleep(1)
data_load_state.text("Loading data...done!")

st.subheader('Raw data')
st.write(data.tail())

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Forecasting with Exponential Smoothing
df_train = data[['Date', 'Close']].copy()

# Fit the model
model = ExponentialSmoothing(
    df_train['Close'],
    seasonal_periods=30,
    trend='add',
    seasonal='add',
)
fitted_model = model.fit()

# Create future dates
last_date = df_train['Date'].max()
future_dates = pd.date_range(
    start=last_date,
    periods=period,
    freq='D'
)

# Make prediction
forecast = fitted_model.forecast(period)
forecast_df = pd.DataFrame({
    'Date': future_dates,
    'Predicted_Close': forecast
})

# Plot the forecast
st.subheader('Forecast data')
st.write(forecast_df.tail())

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Historical'))
fig1.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Predicted_Close'], name='Forecast'))
fig1.layout.update(title_text="Forecast", xaxis_rangeslider_visible=True)
st.plotly_chart(fig1)

# Plot components - using the correct attributes
st.write('Forecast components')

# Get the components using the correct method
result = pd.DataFrame(index=data.index)
result['Observed'] = df_train['Close']
result['Trend'] = fitted_model.level
result['Season'] = fitted_model.season
result['Residual'] = fitted_model.resid

# Create the components plot
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=data['Date'], y=result['Trend'], name='Trend'))
fig2.add_trace(go.Scatter(x=data['Date'], y=result['Season'], name='Seasonal'))
fig2.add_trace(go.Scatter(x=data['Date'], y=result['Residual'], name='Residual'))
fig2.layout.update(title_text="Forecast Components", xaxis_rangeslider_visible=True)
st.plotly_chart(fig2)
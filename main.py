import streamlit as st
from datetime import date
import time
import yfinance as yf
import plotly.graph_objs as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd
import numpy as np
import requests
from io import StringIO

# Date time frame for data
START = "2015-01-01" 
TODAY = date.today().strftime("%Y-%m-%d")

st.title("Stock Prediction App")

# Function to get S&P 500 stocks
@st.cache_data
def load_sp500_stocks():
    # Get S&P 500 stocks from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]
    return list(zip(table['Symbol'].tolist(), table['Security'].tolist()))

# Load S&P 500 stocks
sp500_stocks = load_sp500_stocks()
stock_dict = dict(sp500_stocks)

# Create a search box for stocks
search_text = st.text_input("Search for a stock (by symbol or company name):", "")

# Filter stocks based on search
if search_text:
    filtered_stocks = [
        (symbol, name) for symbol, name in sp500_stocks 
        if search_text.upper() in symbol.upper() or search_text.lower() in name.lower()
    ]
else:
    filtered_stocks = sp500_stocks

# Create formatted options for selectbox
stock_options = [f"{symbol} - {name}" for symbol, name in filtered_stocks]

# Default to first stock if available, otherwise show message
if stock_options:
    selected_stock_full = st.selectbox("Select dataset for prediction", stock_options)
    selected_stocks = selected_stock_full.split(" - ")[0]  # Extract symbol from selection
else:
    st.warning("No stocks match your search criteria")
    st.stop()

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

# Display company name along with the stock symbol
st.subheader(f'Data for {selected_stocks} - {stock_dict[selected_stocks]}')
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

# Plot components
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
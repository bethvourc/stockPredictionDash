import streamlit as st
from datetime import date, datetime, timedelta
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
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        table = pd.read_html(url)[0]
        return list(zip(table['Symbol'].tolist(), table['Security'].tolist()))
    except Exception as e:
        st.error(f"Error loading S&P 500 stocks: {str(e)}")
        return []

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
period = n_years * 252  # Using trading days instead of calendar days

@st.cache_data(ttl=timedelta(hours=6))
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        if data.empty:
            return None
        data.reset_index(inplace=True)
        # Convert Date column to datetime if it's not already
        data['Date'] = pd.to_datetime(data['Date'])
        return data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        return None

data_load_state = st.text("Loading data...")
data = load_data(selected_stocks)

if data is None or data.empty:
    st.error(f"No data available for {selected_stocks}")
    st.stop()

data_load_state.text("Loading data... done!")

# Display company name along with the stock symbol
st.subheader(f'Data for {selected_stocks} - {stock_dict[selected_stocks]}')
st.write(data.tail())

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    fig.layout.update(
        title_text="Time Series Data", 
        xaxis_rangeslider_visible=True,
        xaxis_title="Date",
        yaxis_title="Price"
    )
    st.plotly_chart(fig)

plot_raw_data()

# Forecasting with Exponential Smoothing
df_train = data[['Date', 'Close']].copy()
df_train = df_train.set_index('Date')

try:
    # Fit the model with improved parameters
    model = ExponentialSmoothing(
        df_train['Close'],
        seasonal_periods=252,  # Trading days in a year
        trend='add',
        seasonal='add',
        initialization_method='estimated',
        use_boxcox=True
    )
    
    fitted_model = model.fit(optimized=True, remove_bias=True)

    # Create future dates (trading days only)
    last_date = df_train.index[-1]
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=period,
        freq='B'  # Business days
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
    
    # Historical data
    fig1.add_trace(go.Scatter(
        x=data['Date'],
        y=data['Close'],
        name='Historical',
        line=dict(color='blue')
    ))
    
    # Forecast
    fig1.add_trace(go.Scatter(
        x=forecast_df['Date'],
        y=forecast_df['Predicted_Close'],
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))

    fig1.layout.update(
        title_text="Stock Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=True,
        showlegend=True
    )
    st.plotly_chart(fig1)

    # Plot components
    st.subheader('Forecast Components')

    # Get the components
    result = pd.DataFrame(index=data['Date'])
    result['Observed'] = df_train['Close']
    result['Trend'] = fitted_model.level
    result['Season'] = fitted_model.season[:len(data.index)]
    result['Residual'] = result['Observed'] - (result['Trend'] + result['Season'])

    # Create the components plot
    fig2 = go.Figure()
    
    components = {
        'Trend': 'blue',
        'Season': 'green',
        'Residual': 'red'
    }
    
    for component, color in components.items():
        fig2.add_trace(go.Scatter(
            x=data['Date'],
            y=result[component],
            name=component,
            line=dict(color=color)
        ))

    fig2.layout.update(
        title_text="Forecast Components Analysis",
        xaxis_title="Date",
        yaxis_title="Value",
        xaxis_rangeslider_visible=True,
        showlegend=True
    )
    st.plotly_chart(fig2)

except Exception as e:
    st.error(f"An error occurred during forecasting: {str(e)}")
    st.write("Please try adjusting the parameters or selecting a different stock.")
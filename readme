# Stock Prediction App

A Streamlit web application for stock price prediction using Exponential Smoothing forecasting. The app allows users to visualize historical stock data and generate future price predictions for selected stocks.

## Features

- Historical stock data visualization
- Interactive stock selection
- Adjustable prediction timeframe (1-4 years)
- Real-time data loading from Yahoo Finance
- Exponential Smoothing forecasting
- Component analysis (trend, seasonal, residual)
- Interactive plots with range slider

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-prediction-app.git
cd stock-prediction-app
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Dependencies

- streamlit
- yfinance
- plotly
- statsmodels
- pandas
- numpy

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Select a stock from the dropdown menu (Available options: AAPL, GOOG, MSFT, GME)
3. Use the slider to adjust the prediction timeframe (1-4 years)
4. View the following information:
   - Raw historical data
   - Time series visualization
   - Forecast predictions
   - Forecast components analysis

## Technical Details

### Data Source
- Historical stock data is fetched from Yahoo Finance
- Data range: 2015-01-01 to present

### Forecasting Method
- Uses Exponential Smoothing with additive trend and seasonal components
- Seasonal period: 30 days
- Predictions are generated for the user-selected time period

### Visualizations
1. Raw Data Plot
   - Shows historical open and close prices
   - Includes range slider for time period selection

2. Forecast Plot
   - Displays historical data and predicted values
   - Interactive visualization with zoom capabilities

3. Components Plot
   - Breaks down the forecast into trend, seasonal, and residual components
   - Helps understand underlying patterns in the data

## Caching

The app implements Streamlit's caching mechanism (`@st.cache_data`) to optimize data loading performance and reduce API calls to Yahoo Finance.

## Limitations

- Predictions are based on historical patterns and may not account for unexpected market events
- Limited to four pre-selected stocks (AAPL, GOOG, MSFT, GME)
- Historical data starts from 2015
- Forecast accuracy may decrease with longer prediction periods

## Contributing

Feel free to submit issues and enhancement requests or contribute to the development of this application.

## License

MIT License
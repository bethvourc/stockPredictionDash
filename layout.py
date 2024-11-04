# part2_layout.py

from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from core import *

# Layout Components
def create_stock_info_card(ticker_info):
    return dbc.Card([
        dbc.CardBody([
            html.H4("Company Information", className="card-title"),
            html.P([
                html.Strong(ticker_info.get('longName', 'N/A')), 
                html.Br(),
                f"Sector: {ticker_info.get('sector', 'N/A')}", html.Br(),
                f"Industry: {ticker_info.get('industry', 'N/A')}", html.Br(),
                f"Market Cap: ${ticker_info.get('marketCap', 0):,.2f}", html.Br(),
                f"P/E Ratio: {ticker_info.get('trailingPE', 'N/A')}", html.Br(),
                f"52 Week Range: ${ticker_info.get('fiftyTwoWeekLow', 0):,.2f} - ${ticker_info.get('fiftyTwoWeekHigh', 0):,.2f}"
            ])
        ])
    ], className="mb-4")

def create_technical_chart(data, title):
    fig = make_subplots(rows=3, cols=1, shared_xaxis=True, 
                       vertical_spacing=0.05,
                       row_heights=[0.6, 0.2, 0.2])

    # Price and Moving Averages
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'], name='OHLC'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_50'],
        name='SMA 50', line=dict(color='orange')
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_200'],
        name='SMA 200', line=dict(color='blue')
    ), row=1, col=1)

    # Volume
    fig.add_trace(go.Bar(
        x=data.index, y=data['Volume'], name='Volume'
    ), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=data.index, y=data['RSI'], name='RSI'
    ), row=3, col=1)

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(
        height=800,
        title_text=title,
        xaxis_rangeslider_visible=False
    )

    return fig

# Main Layout
app.layout = dbc.Container([
    html.H1("Enhanced Stock Prediction App", className="my-4"),
    
    # Controls
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Parameters"),
                    dcc.Dropdown(
                        id='stock-selector',
                        options=[{'label': ticker, 'value': ticker} for ticker in SP500_TICKERS],
                        value='AAPL'
                    ),
                    html.Br(),
                    html.Label("Years of prediction:"),
                    dcc.Slider(
                        id='years-slider',
                        min=1, max=4, value=1,
                        marks={i: f'{i}y' for i in range(1, 5)},
                        step=1
                    ),
                    html.Br(),
                    html.Label("Confidence Interval (%):"),
                    dcc.Slider(
                        id='confidence-slider',
                        min=80, max=95, value=90,
                        marks={i: f'{i}%' for i in range(80, 96, 5)},
                        step=5
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Stock Info
    dbc.Row([
        dbc.Col(id='stock-info', width=12)
    ], className="mb-4"),
    
    # Technical Analysis Chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Technical Analysis"),
                    dcc.Graph(id='technical-chart')
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Forecast Chart
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Price Forecast"),
                    dcc.Loading(
                        id="loading-forecast",
                        children=[dcc.Graph(id='forecast-chart')],
                        type="default"
                    )
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Model Performance
    html.H3("Model Performance Analysis"),
    dbc.Tabs([
        dbc.Tab([
            dbc.Row(id='performance-metrics')
        ], label="Metrics"),
        
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='feature-importance-lgb')
                ], width=6),
                dbc.Col([
                    dcc.Graph(id='feature-importance-catboost')
                ], width=6)
            ])
        ], label="Feature Importance"),
        
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='model-contributions')
                ])
            ])
        ], label="Model Contributions")
    ], id="performance-tabs"),
    
    # Store components for sharing data between callbacks
    dcc.Store(id='stock-data-store'),
    dcc.Store(id='forecast-store'),
    
    # Footer
    html.Hr(),
    html.P(
        "Disclaimer: This application is for educational and research purposes only. "
        "The predictions are based on historical data and technical analysis, and should not be considered as financial advice. "
        "Past performance does not guarantee future results.",
        className="text-muted small"
    )
], fluid=True)

# Main Callbacks
@app.callback(
    [Output('stock-data-store', 'data'),
     Output('stock-info', 'children')],
    [Input('stock-selector', 'value')]
)
def update_stock_data(selected_stock):
    data = load_data(selected_stock)
    if data is not None:
        # Get company info
        ticker = yf.Ticker(selected_stock)
        info = ticker.info
        
        # Create stock info card
        info_card = create_stock_info_card(info)
        
        # Store data
        return data.to_json(date_format='iso', orient='split'), info_card
    
    return None, html.Div("Error loading stock data")

@app.callback(
    Output('technical-chart', 'figure'),
    [Input('stock-data-store', 'data'),
     Input('stock-selector', 'value')]
)
def update_technical_chart(json_data, selected_stock):
    if json_data is None:
        return go.Figure()
    
    data = pd.read_json(json_data, orient='split')
    return create_technical_chart(data, f"{selected_stock} Technical Analysis")

@app.callback(
    [Output('forecast-store', 'data'),
     Output('forecast-chart', 'figure')],
    [Input('stock-data-store', 'data'),
     Input('years-slider', 'value'),
     Input('confidence-slider', 'value'),
     Input('stock-selector', 'value')]
)
def update_forecast(json_data, n_years, confidence_interval, selected_stock):
    if json_data is None:
        return None, go.Figure()
    
    data = pd.read_json(json_data, orient='split')
    period = n_years * 365
    
    # Create and train model
    ensemble_model = EnhancedEnsemblePredictor(confidence_interval=confidence_interval/100)
    df, X_scaled, y = ensemble_model.prepare_data(data, period)
    
    ensemble_model.train_sarima(data)
    ensemble_model.train_lightgbm(X_scaled, y)
    ensemble_model.train_catboost(X_scaled, y)
    
    forecast = ensemble_model.forecast(data, period)
    
    # Create forecast plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Historical',
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line=dict(color='gray'),
        name='Upper Bound'
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line=dict(color='gray'),
        name='Lower Bound'
    ))

    fig.update_layout(
        title=f"{selected_stock} Price Forecast",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified'
    )
    
    return forecast.to_json(date_format='iso', orient='split'), fig

if __name__ == '__main__':
    app.run_server(debug=True)
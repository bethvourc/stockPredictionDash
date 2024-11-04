# part3_analysis.py

from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from core import *
from layout import app

# Performance Metrics Components
def create_performance_metrics(data, forecast):
    y_true = data['Close'].values[-len(forecast):]
    y_pred = forecast['yhat'].values
    
    mape = mean_absolute_percentage_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = 1 - (np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2))
    
    actual_direction = np.sign(np.diff(y_true))
    pred_direction = np.sign(np.diff(y_pred))
    directional_accuracy = np.mean(actual_direction == pred_direction)
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("MAPE"),
                    html.H3(f"{mape:.2%}")
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("RMSE"),
                    html.H3(f"${rmse:.2f}")
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("R² Score"),
                    html.H3(f"{r2:.3f}")
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Directional Accuracy"),
                    html.H3(f"{directional_accuracy:.2%}")
                ])
            ])
        ])
    ])

# Advanced Analysis Components
def create_trend_analysis(data):
    current_price = data['Close'].iloc[-1]
    sma_50 = data['SMA_50'].iloc[-1]
    sma_200 = data['SMA_200'].iloc[-1]
    
    trend_status = "Bullish" if current_price > sma_50 > sma_200 else \
                  "Bearish" if current_price < sma_50 < sma_200 else "Mixed"
    
    price_vs_sma50 = ((current_price / sma_50) - 1) * 100
    sma50_vs_sma200 = ((sma_50 / sma_200) - 1) * 100
    
    return dbc.Card([
        dbc.CardHeader("Trend Analysis"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Trend Status"),
                    html.H3(trend_status, 
                           style={'color': 'green' if trend_status == 'Bullish' else 'red' if trend_status == 'Bearish' else 'gray'})
                ]),
                dbc.Col([
                    html.H5("Price vs SMA50"),
                    html.H3(f"{price_vs_sma50:.2f}%")
                ]),
                dbc.Col([
                    html.H5("SMA50 vs SMA200"),
                    html.H3(f"{sma50_vs_sma200:.2f}%")
                ])
            ])
        ])
    ])

def create_volatility_analysis(data):
    current_volatility = data['Volatility'].iloc[-1]
    avg_volatility = data['Volatility'].mean()
    vol_ratio = current_volatility / avg_volatility
    vol_percentile = stats.percentileofscore(data['Volatility'].dropna(), current_volatility)
    
    return dbc.Card([
        dbc.CardHeader("Volatility Analysis"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Current Volatility"),
                    html.H3(f"${current_volatility:.2f}")
                ]),
                dbc.Col([
                    html.H5("Volatility Ratio"),
                    html.H3(f"{vol_ratio:.2f}x Average")
                ]),
                dbc.Col([
                    html.H5("Volatility Percentile"),
                    html.H3(f"{vol_percentile:.1f}%")
                ])
            ])
        ])
    ])

def create_risk_metrics(data):
    # Beta calculation
    sp500 = yf.download('^GSPC', START, TODAY)['Close']
    returns = data['Close'].pct_change()
    market_returns = sp500.pct_change()
    
    covariance = returns.cov(market_returns)
    market_variance = market_returns.var()
    beta = covariance / market_variance
    correlation = returns.corr(market_returns)
    
    # Risk metrics
    var_95 = np.percentile(returns.dropna(), 5)
    var_99 = np.percentile(returns.dropna(), 1)
    
    # Drawdown analysis
    rolling_max = data['Close'].expanding().max()
    drawdowns = data['Close'] / rolling_max - 1.0
    max_drawdown = drawdowns.min()
    current_drawdown = drawdowns.iloc[-1]
    
    return dbc.Card([
        dbc.CardHeader("Risk Metrics"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("Beta"),
                    html.H3(f"{beta:.2f}")
                ]),
                dbc.Col([
                    html.H5("Value at Risk (95%)"),
                    html.H3(f"{var_95:.2%}")
                ]),
                dbc.Col([
                    html.H5("Maximum Drawdown"),
                    html.H3(f"{max_drawdown:.2%}")
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5("Market Correlation"),
                    html.H3(f"{correlation:.2f}")
                ]),
                dbc.Col([
                    html.H5("Value at Risk (99%)"),
                    html.H3(f"{var_99:.2%}")
                ]),
                dbc.Col([
                    html.H5("Current Drawdown"),
                    html.H3(f"{current_drawdown:.2%}")
                ])
            ])
        ])
    ])

# Additional Callbacks
@app.callback(
    Output('performance-metrics', 'children'),
    [Input('stock-data-store', 'data'),
     Input('forecast-store', 'data')]
)
def update_performance_metrics(stock_json, forecast_json):
    if stock_json is None or forecast_json is None:
        return html.Div()
    
    data = pd.read_json(stock_json, orient='split')
    forecast = pd.read_json(forecast_json, orient='split')
    
    return create_performance_metrics(data, forecast)

@app.callback(
    [Output('feature-importance-lgb', 'figure'),
     Output('feature-importance-catboost', 'figure')],
    [Input('stock-data-store', 'data'),
     Input('years-slider', 'value')]
)
def update_feature_importance(stock_json, n_years):
    if stock_json is None:
        return go.Figure(), go.Figure()
    
    data = pd.read_json(stock_json, orient='split')
    period = n_years * 365
    
    ensemble_model = EnhancedEnsemblePredictor()
    df, X_scaled, y = ensemble_model.prepare_data(data, period)
    
    ensemble_model.train_lightgbm(X_scaled, y)
    ensemble_model.train_catboost(X_scaled, y)
    
    # LightGBM importance
    lgb_importance = pd.DataFrame({
        'feature': ensemble_model.feature_columns,
        'importance': ensemble_model.lgb_model.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    
    fig_lgb = go.Figure(go.Bar(
        x=lgb_importance['importance'],
        y=lgb_importance['feature'],
        orientation='h'
    ))
    fig_lgb.update_layout(
        title="LightGBM Feature Importance",
        height=400
    )
    
    # CatBoost importance
    catboost_importance = pd.DataFrame({
        'feature': ensemble_model.feature_columns,
        'importance': ensemble_model.catboost_model.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    
    fig_catboost = go.Figure(go.Bar(
        x=catboost_importance['importance'],
        y=catboost_importance['feature'],
        orientation='h'
    ))
    fig_catboost.update_layout(
        title="CatBoost Feature Importance",
        height=400
    )
    
    return fig_lgb, fig_catboost

@app.callback(
    Output('model-contributions', 'figure'),
    [Input('stock-data-store', 'data'),
     Input('forecast-store', 'data')]
)
def update_model_contributions(stock_json, forecast_json):
    if stock_json is None or forecast_json is None:
        return go.Figure()
    
    data = pd.read_json(stock_json, orient='split')
    forecast = pd.read_json(forecast_json, orient='split')
    
    last_points = min(30, len(forecast))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data.index[-last_points:],
        y=data['Close'].values[-last_points:],
        name='Actual',
        line=dict(color='black')
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast['ds'][:last_points],
        y=forecast['yhat'][:last_points],
        name='Ensemble',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Model Predictions Comparison",
        xaxis_title="Date",
        yaxis_title="Price",
        height=500
    )
    
    return fig

# Add Advanced Analysis Tabs
app.layout.children.append(
    html.Div([
        html.H3("Advanced Analysis", className="mt-4"),
        dbc.Tabs([
            dbc.Tab([
                dbc.Row([
                    dbc.Col(id='trend-analysis', width=12, className="mb-4"),
                    dbc.Col(id='volatility-analysis', width=12)
                ])
            ], label="Trend Analysis"),
            
            dbc.Tab([
                dbc.Col(id='risk-metrics', width=12)
            ], label="Risk Metrics")
        ])
    ])
)

# Advanced Analysis Callbacks
@app.callback(
    [Output('trend-analysis', 'children'),
     Output('volatility-analysis', 'children'),
     Output('risk-metrics', 'children')],
    [Input('stock-data-store', 'data')]
)
def update_advanced_analysis(stock_json):
    if stock_json is None:
        return html.Div(), html.Div(), html.Div()
    
    data = pd.read_json(stock_json, orient='split')
    
    trend = create_trend_analysis(data)
    volatility = create_volatility_analysis(data)
    risk = create_risk_metrics(data)
    
    return trend, volatility, risk

if __name__ == '__main__':
    app.run_server(debug=True)
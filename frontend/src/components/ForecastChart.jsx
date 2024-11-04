import React from 'react';
import Plot from 'react-plotly.js';

const ForecastChart = ({ historicalData, forecastData }) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow">
            <Plot
                data={[
                    {
                        type: 'scatter',
                        x: historicalData.map(d => d.Date),
                        y: historicalData.map(d => d.Close),
                        name: 'Historical',
                        line: { color: 'blue' }
                    },
                    {
                        type: 'scatter',
                        x: forecastData.map(d => d.ds),
                        y: forecastData.map(d => d.yhat),
                        name: 'Forecast',
                        line: { color: 'red', dash: 'dash' }
                    },
                    {
                        type: 'scatter',
                        x: forecastData.map(d => d.ds),
                        y: forecastData.map(d => d.yhat_upper),
                        name: 'Upper Bound',
                        line: { color: 'gray' },
                        fill: 'none'
                    },
                    {
                        type: 'scatter',
                        x: forecastData.map(d => d.ds),
                        y: forecastData.map(d => d.yhat_lower),
                        name: 'Lower Bound',
                        line: { color: 'gray' },
                        fill: 'tonexty'
                    }
                ]}
                layout={{
                    title: 'Price Forecast',
                    yaxis: { title: 'Price ($)' },
                    xaxis: { title: 'Date' },
                    showlegend: true,
                    hovermode: 'x unified'
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '500px' }}
            />
        </div>
    );
};

export default ForecastChart;

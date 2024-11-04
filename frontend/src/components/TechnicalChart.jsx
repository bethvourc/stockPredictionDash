import React from 'react';
import Plot from 'react-plotly.js';

const TechnicalChart = ({ data }) => {
    return (
        <Plot
            data={[
                {
                    type: 'candlestick',
                    x: data.map(d => d.Date),
                    open: data.map(d => d.Open),
                    high: data.map(d => d.High),
                    low: data.map(d => d.Low),
                    close: data.map(d => d.Close),
                    name: 'OHLC'
                },
                {
                    type: 'scatter',
                    x: data.map(d => d.Date),
                    y: data.map(d => d.SMA_50),
                    name: 'SMA 50',
                    line: { color: 'orange' }
                },
                {
                    type: 'scatter',
                    x: data.map(d => d.Date),
                    y: data.map(d => d.SMA_200),
                    name: 'SMA 200',
                    line: { color: 'blue' }
                }
            ]}
            layout={{
                title: 'Technical Analysis',
                yaxis: { title: 'Price' },
                xaxis: { rangeslider: { visible: false } }
            }}
            useResizeHandler={true}
            style={{ width: '100%', height: '500px' }}
        />
    );
};

export default TechnicalChart;

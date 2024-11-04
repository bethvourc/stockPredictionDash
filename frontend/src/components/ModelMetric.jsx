import React from 'react';
import { calculateMetrics } from '../utils/calculations';

const ModelMetrics = ({ data }) => {
    const metrics = calculateMetrics(data);

    return (
        <div className="bg-white p-4 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Model Performance Metrics</h2>
            <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-500">MAPE</h3>
                    <p className="text-2xl font-semibold">{metrics.mape.toFixed(2)}%</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-500">RMSE</h3>
                    <p className="text-2xl font-semibold">${metrics.rmse.toFixed(2)}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                    <h3 className="text-sm font-medium text-gray-500">R² Score</h3>
                    <p className="text-2xl font-semibold">{metrics.r2.toFixed(3)}</p>
                </div>
            </div>
        </div>
    );
};

export default ModelMetrics;